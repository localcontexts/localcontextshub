import factory
import requests
from django.core.files.uploadedfile import SimpleUploadedFile
from helpers.models import Notice, NoticeTranslation, OpenToCollaborateNoticeURL, EntitiesNotified, LabelTranslation, ProjectComment, ProjectStatus, LabelNote, LabelVersion, LabelTranslationVersion, NoticeDownloadTracker, CollectionsCareNoticePolicy, HubActivity
from factories.accounts_factories import UserFactory
from factories.bclabels_factories import BCLabelFactory
from factories.tklabels_factories import TKLabelFactory
from factories.communities_factories import CommunityFactory
from factories.researchers_factories import ResearcherFactory
from factories.institutions_factories import InstitutionFactory
from factories.projects_factories import ProjectFactory


class NoticeFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the Notice Model'''

    class Meta:
        model = Notice

    project = factory.SubFactory(ProjectFactory)
    notice_type = factory.Faker('random_element',
                                elements=[
                                    'biocultural', 'traditional_knowledge',
                                    'attribution_incomplete'
                                ])
    name = factory.Faker('word')
    researcher = factory.SubFactory(ResearcherFactory)
    institution = factory.SubFactory(InstitutionFactory)
    img_url = factory.Faker('image_url')
    svg_url = factory.Faker('image_url')
    default_text = factory.Faker('text')
    archived = factory.Faker('boolean')
    created = factory.Faker('date_time_this_month')
    updated = factory.Faker('date_time_this_month')


class NoticeTranslationFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the NoticeTranslation Model'''

    class Meta:
        model = NoticeTranslation

    notice_type = factory.Faker('random_element',
                                elements=[
                                    'biocultural', 'traditional_knowledge',
                                    'attribution_incomplete'
                                ])
    notice = factory.SubFactory(NoticeFactory)
    language_tag = factory.Faker('language_code')
    language = factory.Faker('language_name')
    translated_name = factory.Faker('word')
    translated_text = factory.Faker('text')


class OpenToCollaborateNoticeURLFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the OpenToCollaborateNoticeURL Model'''

    class Meta:
        model = OpenToCollaborateNoticeURL

    institution = factory.SubFactory(InstitutionFactory)
    researcher = factory.SubFactory(ResearcherFactory)
    name = factory.Faker('name')
    url = factory.Faker('url')
    added = factory.Faker('date_time_this_year')


class EntitiesNotifiedFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the EntitiesNotified Model'''

    class Meta:
        model = EntitiesNotified
        skip_postgeneration_save = True

    project = factory.SubFactory(ProjectFactory)

    @factory.post_generation
    def set_communities(self, create, extracted, **kwargs):
        if create:
            self.communities.add(CommunityFactory())

    @factory.post_generation
    def set_institutions(self, create, extracted, **kwargs):
        if create:
            self.institutions.add(InstitutionFactory())

    @factory.post_generation
    def set_researchers(self, create, extracted, **kwargs):
        if create:
            self.researchers.add(ResearcherFactory())


class LabelTranslationFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the LabelTranslation Model'''

    class Meta:
        model = LabelTranslation
        skip_postgeneration_save = True

    bclabel = factory.SubFactory(BCLabelFactory)
    tklabel = factory.SubFactory(TKLabelFactory)
    translated_name = factory.Faker('word')
    language_tag = factory.Faker('language_code')
    language = factory.Faker('language_name')
    translated_text = factory.Faker('text')

    #This functions checks if the language is set than fetchs language tag from URL and set the language_tag
    @factory.post_generation
    def set_language_tag(self, create, extracted, **kwargs):
        if not create:
            return

        if self.language:
            url = 'https://raw.githubusercontent.com/biocodellc/localcontexts_json/main/data/ianaObj.json'
            data = requests.get(url).json()

            if self.language in data.keys():
                self.language_tag = data[self.language]


class ProjectCommentFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectComment Model'''

    class Meta:
        model = ProjectComment

    project = factory.SubFactory(ProjectFactory)
    community = factory.SubFactory(CommunityFactory)
    sender = factory.SubFactory(UserFactory)
    sender_affiliation = factory.Faker('company')
    message = factory.Faker('text', max_nb_chars=1500)
    created = factory.Faker('date_time_this_month')


class ProjectStatusFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the ProjectStatus Model'''

    class Meta:
        model = ProjectStatus

    project = factory.SubFactory(ProjectFactory)
    community = factory.SubFactory(CommunityFactory)
    seen = factory.Faker('boolean')
    status = factory.Faker(
        'random_element',
        elements=['pending', 'not_pending', 'labels_applied'])


class LabelNoteFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the LabelNote Model'''

    class Meta:
        model = LabelNote

    bclabel = factory.SubFactory(BCLabelFactory)
    tklabel = factory.SubFactory(TKLabelFactory)
    sender = factory.SubFactory(UserFactory)
    note = factory.Faker('text')


class LabelVersionFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the LabelVersion Model'''

    class Meta:
        model = LabelVersion

    created_by = factory.SubFactory(UserFactory)
    is_approved = factory.Faker('boolean')
    approved_by = factory.SubFactory(UserFactory)
    bclabel = factory.SubFactory(BCLabelFactory)
    tklabel = factory.SubFactory(TKLabelFactory)
    version = factory.Faker('random_int', min=1, max=30)
    version_text = factory.Faker('text')
    created = factory.Faker('date_time_this_year')


class LabelTranslationVersionFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the LabelTranslationVersion Model'''

    class Meta:
        model = LabelTranslationVersion

    version_instance = factory.SubFactory(LabelVersionFactory)
    translated_name = factory.Faker('word')
    language_tag = factory.Faker('language_code')
    language = factory.Faker('language_name')
    translated_text = factory.Faker('text')
    created = factory.Faker('date_time_this_year')


class NoticeDownloadTrackerFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the NoticeDownloadTracker Model'''

    class Meta:
        model = NoticeDownloadTracker

    institution = factory.SubFactory(InstitutionFactory)
    researcher = factory.SubFactory(ResearcherFactory)
    user = factory.SubFactory(UserFactory)
    collections_care_notices = factory.Faker('boolean')
    open_to_collaborate_notice = factory.Faker('boolean')
    date_downloaded = factory.Faker('date_time_this_year')


class CollectionsCareNoticePolicyFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the CollectionsCareNoticePolicy Model'''

    class Meta:
        model = CollectionsCareNoticePolicy

    institution = factory.SubFactory(InstitutionFactory)
    policy_document = SimpleUploadedFile("policy_document.txt",
                                         b"file_content",
                                         content_type="text/plain")
    url = factory.Faker('url')
    added = factory.Faker('date_time_this_year')


class HubActivityFactory(factory.django.DjangoModelFactory):
    '''This is the Factory for the HubActivity Model'''

    class Meta:
        model = HubActivity

    action_user_id = factory.Faker('random_int', min=1, max=1000)
    action_account_type = factory.Faker('word')
    community_id = factory.Faker('random_int', min=1, max=1000)
    institution_id = factory.Faker('random_int', min=1, max=1000)
    project_id = factory.Faker('random_int', min=1, max=1000)
    action_type = factory.Faker(
        'random_element',
        elements=('New Member Added', 'New User', 'New Researcher',
                  'New Community', 'New Institution', 'Project Edited',
                  'Project Created', 'Community Notified', 'Label(s) Applied',
                  'Disclosure Notice(s) Added', 'Engagement Notice Added'))
    date = factory.Faker('date_time_this_year')
