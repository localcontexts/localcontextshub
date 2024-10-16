from django.urls import reverse
from rest_framework import serializers
from api.base import serializers as base_serializers

from drf_spectacular.utils import extend_schema_field, inline_serializer
from drf_spectacular.types import OpenApiTypes

from projects.models import ProjectContributors, ProjectPerson, Project
from communities.models import Community

from api.views import HELPTEXT_CHOICES


class InstitutionSerializer(base_serializers.InstitutionSerializer):
    name = serializers.CharField(
        source='institution_name', help_text=HELPTEXT_CHOICES['account_name']
    )
    profile_url = serializers.SerializerMethodField(help_text=HELPTEXT_CHOICES['profile_url'])

    class Meta(base_serializers.InstitutionSerializer.Meta):
        fields = ('id', 'name', 'profile_url', 'ror_id')
        extra_kwargs = {
            'id': {'help_text': HELPTEXT_CHOICES['id']},
            'ror_id': {'help_text': HELPTEXT_CHOICES['ror_id']}
        }

    @extend_schema_field(OpenApiTypes.URI)
    def get_profile_url(self, obj):
        request = self.context.get('request')
        profile_url = reverse('public-institution', kwargs={'pk': obj.id})
        return request.build_absolute_uri(profile_url)


class ResearcherSerializer(base_serializers.ResearcherSerializer):
    name = serializers.SerializerMethodField(help_text=HELPTEXT_CHOICES['account_name'])
    profile_url = serializers.SerializerMethodField(help_text=HELPTEXT_CHOICES['profile_url'])

    class Meta(base_serializers.ResearcherSerializer.Meta):
        fields = ('id', 'name', 'profile_url', 'orcid')
        extra_kwargs = {
            'id': {'help_text': HELPTEXT_CHOICES['id']},
            'orcid': {'help_text': HELPTEXT_CHOICES['ror_id']}
        }

    @extend_schema_field(OpenApiTypes.STR)
    def get_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            full_name = str(obj.user.first_name) + ' ' + str(obj.user.last_name)
        else:
            full_name = str(obj.user.username)
        return full_name

    @extend_schema_field(OpenApiTypes.URI)
    def get_profile_url(self, obj):
        request = self.context.get('request')
        profile_url = reverse('public-researcher', kwargs={'pk': obj.user.id})
        return request.build_absolute_uri(profile_url)


class CommunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='community_name', help_text=HELPTEXT_CHOICES['account_name']
    )
    profile_url = serializers.SerializerMethodField(help_text=HELPTEXT_CHOICES['profile_url'])

    class Meta:
        model = Community
        fields = ('id', 'name', 'profile_url')
        extra_kwargs = {'id': {'help_text': HELPTEXT_CHOICES['id']}}

    @extend_schema_field(OpenApiTypes.URI)
    def get_profile_url(self, obj):
        request = self.context.get('request')
        profile_url = reverse('public-community', kwargs={'pk': obj.id})
        return request.build_absolute_uri(profile_url)


class LabelTranslationSerializer(base_serializers.LabelTranslationSerializer):
    class Meta(base_serializers.LabelTranslationSerializer.Meta):
        extra_kwargs = {
            'translated_name': {'help_text': HELPTEXT_CHOICES['translated_name']},
            'language_tag': {'help_text': HELPTEXT_CHOICES['language_tag']},
            'language': {'help_text': HELPTEXT_CHOICES['language']},
            'translated_text': {'help_text': HELPTEXT_CHOICES['translated_text']},
        }


class BCLabelSerializer(base_serializers.BCLabelSerializer):
    community = CommunitySerializer(help_text=HELPTEXT_CHOICES['community'])
    translations = LabelTranslationSerializer(
        source="bclabel_translation", many=True, help_text=HELPTEXT_CHOICES['translations']
    )

    class Meta(base_serializers.BCLabelSerializer.Meta):
        extra_kwargs = {
            'unique_id': {'help_text': HELPTEXT_CHOICES['unique_id']},
            'name': {'help_text': HELPTEXT_CHOICES['name']},
            'label_type': {'help_text': HELPTEXT_CHOICES['label_type']},
            'language_tag': {'help_text': HELPTEXT_CHOICES['language_tag']},
            'language': {'help_text': HELPTEXT_CHOICES['language']},
            'label_text': {'help_text': HELPTEXT_CHOICES['label_text']},
            'img_url': {'help_text': HELPTEXT_CHOICES['img_url']},
            'svg_url': {'help_text': HELPTEXT_CHOICES['svg_url']},
            'audiofile': {'help_text': HELPTEXT_CHOICES['audiofile']},
            'created': {'help_text': HELPTEXT_CHOICES['created']},
            'updated': {'help_text': HELPTEXT_CHOICES['updated']}
        }


class TKLabelSerializer(base_serializers.TKLabelSerializer):
    community = CommunitySerializer(help_text=HELPTEXT_CHOICES['community'])
    translations = LabelTranslationSerializer(
        source="tklabel_translation", many=True, help_text=HELPTEXT_CHOICES['translations']
    )

    class Meta(base_serializers.TKLabelSerializer.Meta):
        extra_kwargs = {
            'unique_id': {'help_text': HELPTEXT_CHOICES['unique_id']},
            'name': {'help_text': HELPTEXT_CHOICES['name']},
            'label_type': {'help_text': HELPTEXT_CHOICES['label_type']},
            'language_tag': {'help_text': HELPTEXT_CHOICES['language_tag']},
            'language': {'help_text': HELPTEXT_CHOICES['language']},
            'label_text': {'help_text': HELPTEXT_CHOICES['label_text']},
            'img_url': {'help_text': HELPTEXT_CHOICES['img_url']},
            'svg_url': {'help_text': HELPTEXT_CHOICES['svg_url']},
            'audiofile': {'help_text': HELPTEXT_CHOICES['audiofile']},
            'created': {'help_text': HELPTEXT_CHOICES['created']},
            'updated': {'help_text': HELPTEXT_CHOICES['updated']}
        }


class NoticeTranslationsSerializer(base_serializers.NoticeTranslationsSerializer):
    class Meta(base_serializers.NoticeTranslationsSerializer.Meta):
        extra_kwargs = {
            'translated_name': {'help_text': HELPTEXT_CHOICES['translated_name']},
            'language_tag': {'help_text': HELPTEXT_CHOICES['language_tag']},
            'language': {'help_text': HELPTEXT_CHOICES['language']},
            'translated_text': {'help_text': HELPTEXT_CHOICES['translated_text']},
        }


class NoticeSerializer(base_serializers.NoticeSerializer):
    translations = NoticeTranslationsSerializer(
        source="notice_translations", many=True, help_text=HELPTEXT_CHOICES['translations']
    )

    class Meta(base_serializers.NoticeSerializer.Meta):
        extra_kwargs = {
            'notice_type': {'help_text': HELPTEXT_CHOICES['notice_type']},
            'name': {'help_text': HELPTEXT_CHOICES['name']},
            'img_url': {'help_text': HELPTEXT_CHOICES['img_url']},
            'svg_url': {'help_text': HELPTEXT_CHOICES['svg_url']},
            'default_text': {'help_text': HELPTEXT_CHOICES['default_text']},
            'translations': {'help_text': HELPTEXT_CHOICES['translations']},
            'created': {'help_text': HELPTEXT_CHOICES['created']},
            'updated': {'help_text': HELPTEXT_CHOICES['updated']},
        }


class ProjectPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPerson
        fields = ('name', 'email')
        extra_kwargs = {
            'name': {'help_text': HELPTEXT_CHOICES['person_name']},
            'email': {'help_text': HELPTEXT_CHOICES['email']}
        }


class ProjectCreatorSerializer(base_serializers.ProjectCreatorSerializer):
    institution = InstitutionSerializer(help_text=HELPTEXT_CHOICES['institution'])
    community = CommunitySerializer(help_text=HELPTEXT_CHOICES['community'])
    researcher = ResearcherSerializer(help_text=HELPTEXT_CHOICES['researcher'])


class ProjectContributorSerializer(serializers.ModelSerializer):
    institutions = InstitutionSerializer(many=True, help_text=HELPTEXT_CHOICES['institutions'])
    communities = CommunitySerializer(many=True, help_text=HELPTEXT_CHOICES['communities'])
    researchers = ResearcherSerializer(many=True, help_text=HELPTEXT_CHOICES['researchers'])
    others = serializers.SerializerMethodField(help_text=HELPTEXT_CHOICES['others'])

    class Meta:
        model = ProjectContributors
        fields = ('institutions', 'communities', 'researchers', 'others')

    @extend_schema_field(
        inline_serializer(
            name = "Others",
            fields= {
                'name': serializers.CharField(help_text=HELPTEXT_CHOICES['person_name']),
                'email': serializers.EmailField(help_text=HELPTEXT_CHOICES['email'])
            },
            many=True
        ),
        OpenApiTypes.OBJECT
    )
    def get_others(self, obj):
        people = [
            people for people in ProjectPerson.objects.filter(
                project=obj.project
            ).values('name', 'email')
        ]
        return [person for person in people]


class ProjectOverviewSerializer(base_serializers.ProjectOverviewSerializer):
    created_by = ProjectCreatorSerializer(
        source="project_creator_project", many=True, help_text=HELPTEXT_CHOICES['created_by']
    )

    class Meta(base_serializers.ProjectOverviewSerializer.Meta):
        fields = base_serializers.ProjectOverviewSerializer.Meta.fields + ('created_by',)
        extra_kwargs = {
            'unique_id': {'help_text': HELPTEXT_CHOICES['unique_id']},
            'providers_id': {'help_text': HELPTEXT_CHOICES['providers_id']},
            'title': {'help_text': HELPTEXT_CHOICES['title']},
            'project_privacy': {'help_text': HELPTEXT_CHOICES['project_privacy']},
            'date_added': {'help_text': HELPTEXT_CHOICES['date_added']},
            'date_modified': {'help_text': HELPTEXT_CHOICES['date_modified']},
        }


class ProjectSerializer(base_serializers.ProjectSerializer):
    external_ids = serializers.SerializerMethodField(help_text=HELPTEXT_CHOICES['external_ids'])
    created_by = ProjectCreatorSerializer(
        source="project_creator_project", many=True, help_text=HELPTEXT_CHOICES['created_by']
    )
    contributors = ProjectContributorSerializer(
        source="project_contributors", help_text=HELPTEXT_CHOICES['contributors']
    )
    notice = NoticeSerializer(
        source="project_notice", many=True, help_text=HELPTEXT_CHOICES['notice']
    )
    bc_labels = BCLabelSerializer(many=True, help_text=HELPTEXT_CHOICES['bc_labels'])
    tk_labels = TKLabelSerializer(many=True, help_text=HELPTEXT_CHOICES['tk_labels'])
    project_contact = serializers.SerializerMethodField(
        help_text=HELPTEXT_CHOICES['project_contact']
    )
    related_projects = serializers.SerializerMethodField(
        help_text=HELPTEXT_CHOICES['related_projects']
    )
    sub_projects = serializers.SerializerMethodField(help_text=HELPTEXT_CHOICES['sub_projects'])

    class Meta(base_serializers.ProjectSerializer.Meta):
        fields = (
            'unique_id', 'external_ids', 'source_project_uuid', 'project_page', 'title',
            'description', 'project_type', 'project_contact', 'urls', 'project_privacy',
            'date_added', 'date_modified', 'created_by', 'contributors', 'notice', 'bc_labels',
            'tk_labels', 'sub_projects', 'related_projects', 'project_boundary_geojson'
        )
        extra_kwargs = {
            'unique_id': {'help_text': HELPTEXT_CHOICES['unique_id']},
            'source_project_uuid': {'help_text': HELPTEXT_CHOICES['source_project_uuid']},
            'project_page': {'help_text': HELPTEXT_CHOICES['project_page']},
            'title': {'help_text': HELPTEXT_CHOICES['title']},
            'description': {'help_text': HELPTEXT_CHOICES['description']},
            'project_type': {'help_text': HELPTEXT_CHOICES['project_type']},
            'urls': {'help_text': HELPTEXT_CHOICES['urls']},
            'project_privacy': {'help_text': HELPTEXT_CHOICES['project_privacy']},
            'date_added': {'help_text': HELPTEXT_CHOICES['date_added']},
            'date_modified': {'help_text': HELPTEXT_CHOICES['date_modified']},
            'project_boundary_geojson': {
                'help_text': HELPTEXT_CHOICES['project_boundary_geojson']
            }
        }

    @extend_schema_field(
        inline_serializer(
            name = "ExternalIDs",
            fields= {
                'providers_id': serializers.CharField(
                    help_text=HELPTEXT_CHOICES['providers_id']
                ),
                'publication_doi': serializers.CharField(
                    help_text=HELPTEXT_CHOICES['publication_doi']
                ),
                'project_data_guid': serializers.CharField(
                    help_text=HELPTEXT_CHOICES['project_data_guid']
                )
            }
        )
    )
    def get_external_ids(self, obj):
        external_ids = {
            'providers_id': obj.providers_id,
            'publication_doi': obj.publication_doi,
            'project_data_guid': obj.project_data_guid
        }
        return external_ids

    @extend_schema_field(OpenApiTypes.STR)
    def get_related_projects(self, obj):
        return [project.unique_id for project in obj.related_projects.all()]

    @extend_schema_field(OpenApiTypes.STR)
    def get_sub_projects(self, obj):
        return [p.unique_id for p in Project.objects.filter(source_project_uuid=obj.unique_id)]

    @extend_schema_field(
        inline_serializer(
            name = "ProjectContact",
            fields= {
                'name': serializers.CharField(help_text=HELPTEXT_CHOICES['person_name']),
                'email': serializers.EmailField(help_text=HELPTEXT_CHOICES['email'])
            }
        )
    )
    def get_project_contact(self, obj):
        return {'name': obj.project_contact, 'email': obj.project_contact_email}



class ProjectDateModified(base_serializers.ProjectDateModified):
    class Meta(base_serializers.ProjectDateModified.Meta):
        extra_kwargs = {
            'unique_id': {'help_text': HELPTEXT_CHOICES['unique_id']},
            'date_modified': {'help_text': HELPTEXT_CHOICES['date_modified']}
        }


class OpenToCollaborationSerializer(serializers.Serializer):
    institution = InstitutionSerializer(help_text=HELPTEXT_CHOICES['institution'])
    researcher = ResearcherSerializer(help_text=HELPTEXT_CHOICES['researcher'])
    notice = NoticeSerializer(help_text=HELPTEXT_CHOICES['notice'])
