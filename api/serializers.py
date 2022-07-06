from django.db.models import fields
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from helpers.models import LabelTranslation, Notice, InstitutionNotice
from projects.models import Project, ProjectCreator
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from django.contrib.auth.models import User

class InstitutionSerializer(serializers.ModelSerializer):
    institution_name = SerializerMethodField()

    class Meta:
        model = Institution
        fields = ('id', 'institution_name')

    def get_institution_name(self, obj):
        return str(obj.institution_name)

class ResearcherSerializer(serializers.ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Researcher
        fields = ('id', 'user', 'orcid')

    def get_user(self, obj):
        return str(obj.user.first_name) + ' ' + str(obj.user.last_name)

class LabelTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelTranslation
        fields = ('translated_name', 'language_tag', 'language', 'translated_text')
    
class BCLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()
    translations = LabelTranslationSerializer(source="bclabel_translation", many=True)

    class Meta:
        model = BCLabel
        fields = ('name', 'label_type', 'language_tag', 'language', 'label_text', 'img_url', 'svg_url', 'audiofile',  'community', 'translations', 'created', 'updated')
    
    def get_community(self, obj):
        return str(obj.community.community_name)

class TKLabelSerializer(serializers.ModelSerializer):
    community = SerializerMethodField()
    translations = LabelTranslationSerializer(source="tklabel_translation", many=True)

    class Meta:
        model = TKLabel
        fields = ('name', 'label_type', 'language_tag', 'language', 'label_text', 'img_url', 'svg_url', 'audiofile', 'community', 'translations', 'created', 'updated')

    def get_community(self, obj):
        return str(obj.community.community_name)

class NoticeSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()
    researcher = ResearcherSerializer()

    class Meta:
        model = Notice
        fields = ('notice_type', 'bc_img_url', 'bc_svg_url', 'bc_default_text', 'tk_img_url', 'tk_svg_url', 'tk_default_text', 'researcher', 'institution', 'created', 'updated',)

class InstitutionNoticeSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()
    researcher = ResearcherSerializer()

    class Meta:
        model = InstitutionNotice
        fields = ('notice_type', 'institution', 'researcher', 'img_url', 'svg_url', 'default_text', 'created', 'updated',)

class ProjectOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified',)

class ProjectCreatorSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()
    researcher = ResearcherSerializer()
    community = SerializerMethodField()

    class Meta:
        model = ProjectCreator
        fields = ('institution', 'researcher', 'community')
    
    def get_community(self, obj):
        if obj.community: 
            return str(obj.community.community_name)


# Notices only   
class ProjectSerializer(serializers.ModelSerializer):
    created = ProjectCreatorSerializer(source="project_creator_project", many=True)

    notice = NoticeSerializer(source="project_notice", many=True)
    institution_notice = InstitutionNoticeSerializer(source="project_institutional_notice", many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified', 'created', 'notice', 'institution_notice', 'project_boundary_geojson')

# Labels only
class ProjectNoNoticeSerializer(serializers.ModelSerializer):
    bc_labels = BCLabelSerializer(many=True)
    tk_labels = TKLabelSerializer(many=True)

    class Meta:
        model = Project
        fields = ('unique_id', 'providers_id', 'title', 'project_privacy', 'date_added', 'date_modified', 'bc_labels', 'tk_labels', 'project_boundary_geojson')
