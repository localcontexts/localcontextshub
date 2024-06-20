from django.urls import reverse, reverse_lazy
from api.base import serializers as base_serializers
from api.base.serializers import *

from projects.models import ProjectContributors, ProjectPerson
from communities.models import Community

class InstitutionSerializer(base_serializers.InstitutionSerializer):
    name = serializers.CharField(source='institution_name')
    profile_url = serializers.SerializerMethodField()

    class Meta(base_serializers.InstitutionSerializer.Meta):
        model = Institution
        fields = ('id', 'name', 'profile_url', 'ror_id')
        
    def get_profile_url(self, obj):
        request = self.context.get('request')
        profile_url = reverse('public-institution', kwargs={'pk': obj.id})
        return request.build_absolute_uri(profile_url)
    
class ResearcherSerializer(base_serializers.ResearcherSerializer):
    name = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()

    class Meta(base_serializers.ResearcherSerializer.Meta):
        model = Researcher
        fields = ('id', 'name', 'profile_url', 'orcid')
    
    def get_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            full_name = str(obj.user.first_name) + ' ' + str(obj.user.last_name)
        else:
            full_name = str(obj.user.username)
        return full_name
        
    def get_profile_url(self, obj):
        request = self.context.get('request')
        profile_url = reverse('public-researcher', kwargs={'pk': obj.user.id})
        return request.build_absolute_uri(profile_url)
    
class CommunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='community_name')
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ('id', 'name', 'profile_url')
        
    def get_profile_url(self, obj):
        request = self.context.get('request')
        profile_url = reverse('public-community', kwargs={'pk': obj.id})
        return request.build_absolute_uri(profile_url)
    
class ProjectPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPerson
        fields = ('name', 'email')

class ProjectCreatorSerializer(base_serializers.ProjectCreatorSerializer):
    institution = InstitutionSerializer()
    community = CommunitySerializer()
    researcher = ResearcherSerializer()

    class Meta(base_serializers.ProjectCreatorSerializer.Meta):
        model = ProjectCreator
        fields = ('institution', 'community', 'researcher')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.project.project_creator.first_name and instance.project.project_creator.last_name:
            full_name = str(instance.project.project_creator.first_name) + ' ' + str(instance.project.project_creator.last_name)
        else:
            full_name = None

        if instance.institution:
            representation.pop('researcher')
            representation.pop('community')
            representation['institution']['user_id'] = instance.project.project_creator.id
            representation['institution']['user_name'] = full_name
        elif instance.community:
            representation.pop('institution')
            representation.pop('researcher')
            representation['community']['user_id'] = instance.project.project_creator.id
            representation['community']['user_name'] = full_name
        elif instance.researcher:
            representation.pop('institution')
            representation.pop('community')
            representation['researcher']['user_id'] = instance.project.project_creator.id
            representation['researcher']['user_name'] = full_name
        return representation
    
class ProjectContributorSerializer(serializers.ModelSerializer):
    institutions = InstitutionSerializer(many=True)
    communities = CommunitySerializer(many=True)
    researchers = ResearcherSerializer(many=True)
    others = serializers.SerializerMethodField()

    class Meta:
        model = ProjectContributors
        # fields = ('institutions', 'communities', 'researchers')
        fields = ('institutions', 'communities', 'researchers', 'others')

    def get_others(self, obj):
        people = [people for people in ProjectPerson.objects.filter(project=obj.project).values('name', 'email')]
        return [person for person in people]
     
class ProjectOverviewSerializer(base_serializers.ProjectOverviewSerializer):
    created_by = ProjectCreatorSerializer(source="project_creator_project", many=True)

    class Meta(base_serializers.ProjectOverviewSerializer.Meta):
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified', 'created_by',)

# Notices only
class ProjectSerializer(base_serializers.ProjectSerializer):
    external_ids = serializers.SerializerMethodField()
    created_by = ProjectCreatorSerializer(source="project_creator_project", many=True)
    contributors = ProjectContributorSerializer(source="project_contributors")
    notice = NoticeSerializer(source="project_notice", many=True)
    project_contact = serializers.SerializerMethodField()
    related_projects = serializers.SerializerMethodField()
    sub_projects = serializers.SerializerMethodField()

    class Meta(base_serializers.ProjectSerializer.Meta):
        model = Project
        fields = ('unique_id', 'external_ids', 'source_project_uuid', 'project_page', 'title', 'description', 'project_type', 'project_contact', 'urls', 'project_privacy', 'date_added', 'date_modified', 'created_by', 'contributors', 'notice', 'sub_projects', 'related_projects', 'project_boundary_geojson')

    def get_external_ids(self, obj):
        return {'providers_id': obj.providers_id, 'publication_doi': obj.publication_doi, 'project_data_guid': obj.project_data_guid}

    def get_related_projects(self, obj):
        return [project.unique_id for project in obj.related_projects.all()]
    
    def get_sub_projects(self, obj):
        return [p.unique_id for p in Project.objects.filter(source_project_uuid=obj.unique_id)]
    
    def get_project_contact(self, obj):
        return {'name': obj.project_contact, 'email': obj.project_contact_email}

# Labels only
class ProjectNoNoticeSerializer(base_serializers.ProjectNoNoticeSerializer):
    external_ids = serializers.SerializerMethodField()
    created_by = ProjectCreatorSerializer(source="project_creator_project", many=True)
    contributors = ProjectContributorSerializer(source="project_contributors")
    bc_labels = BCLabelSerializer(many=True)
    tk_labels = TKLabelSerializer(many=True)
    project_contact = serializers.SerializerMethodField()
    related_projects = serializers.SerializerMethodField()
    sub_projects = serializers.SerializerMethodField()

    class Meta(base_serializers.ProjectNoNoticeSerializer.Meta):
        model = Project
        fields = ('unique_id', 'external_ids', 'source_project_uuid', 'project_page', 'title', 'description', 'project_type', 'project_contact', 'urls', 'project_privacy', 'date_added', 'date_modified', 'created_by', 'contributors', 'bc_labels', 'tk_labels', 'sub_projects', 'related_projects', 'project_boundary_geojson')
    
    def get_external_ids(self, obj):
        return {'providers_id': obj.providers_id, 'publication_doi': obj.publication_doi, 'project_data_guid': obj.project_data_guid}
    
    def get_related_projects(self, obj):
        return [project.unique_id for project in obj.related_projects.all()]
    
    def get_sub_projects(self, obj):
        return [p.unique_id for p in Project.objects.filter(source_project_uuid=obj.unique_id)]
    
    def get_project_contact(self, obj):
        return {'name': obj.project_contact, 'email': obj.project_contact_email}