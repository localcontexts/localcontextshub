import pytest
from django.test import TestCase
from factories.accounts_factories import UserFactory
from helpers.models import Notice, NoticeTranslation
from factories.communities_factories import CommunityFactory
from factories.institutions_factories import InstitutionFactory
from factories.researchers_factories import ResearcherFactory
from factories.helpers_factories import NoticeFactory, NoticeTranslationFactory, OpenToCollaborateNoticeURLFactory,EntitiesNotifiedFactory,LabelTranslationFactory, ProjectCommentFactory, NoticeDownloadTrackerFactory, HubActivityFactory, LabelTranslationVersionFactory, LabelVersionFactory,LabelNoteFactory, ProjectStatusFactory, CollectionsCareNoticePolicyFactory

class TestNotice(TestCase):
    @pytest.mark.django_db
    def setUp(self):
         self.notice = NoticeFactory()

    def test_notice_str_method(self):
        new_notice = self.notice
        string = str(new_notice)
        self.assertIsInstance(string, str)
        self.assertEqual(string, new_notice.project.title)

    def test_notice_set_translation(self):
        new_notice = self.notice
        language_tag = "fr"
        new_notice.set_translation(language_tag)
        translation = NoticeTranslation.objects.filter(notice=new_notice, language_tag=language_tag).first()

        self.assertIsNotNone(translation)
        self.assertIsNotNone(translation.translated_text)

class TestNoticeTranslation(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.notice_translation = NoticeTranslationFactory()

    def test_notice_translation_str_method(self):
        new_notice_translation = self.notice_translation
        string = str(new_notice_translation)
        
        self.assertIsInstance(string, str)
        self.assertEqual(string, f"{new_notice_translation.notice} - {new_notice_translation.language}")
   
class TestOpenToCollaborateNoticeURL(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.open_to_collaborate_notice_url  = OpenToCollaborateNoticeURLFactory()

    def test_open_to_collaborate_notice_url_str_method(self):
        new_open_to_collaborate_notice_url = self.open_to_collaborate_notice_url
        string = str(new_open_to_collaborate_notice_url)
        
        self.assertIsInstance(string, str)
        self.assertEqual(string,new_open_to_collaborate_notice_url.name)

class TestEntitiesNotified(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.entities_notified  = EntitiesNotifiedFactory()

    def test_is_user_in_notified_account(self):
        new_entities_notified = self.entities_notified

        # Create user objects for different account types
        community_user = UserFactory()
        institution_user = UserFactory()
        researcher_user = UserFactory()
        
        community = CommunityFactory()
        community.viewers.add(community_user)
        institution = InstitutionFactory()
        institution.viewers.add(institution_user)
        
        # Add communities, institutions, and researchers to EntitiesNotified
        new_entities_notified.communities.add(community)
        new_entities_notified.institutions.add(institution)
    
        assert new_entities_notified.is_user_in_notified_account(community_user) is True
        assert new_entities_notified.is_user_in_notified_account(institution_user) is True
    
    def test_entities_notified_str_method(self):
        new_entities_notified = self.entities_notified
        string = new_entities_notified.__str__()

        assert isinstance(string, str)
        assert string == str(new_entities_notified.project.title)

class TestLabelTranslation(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.label_translation = LabelTranslationFactory()

    def test_new_label_translation_str_method(self):
        new_label_translation = self.label_translation
        string = new_label_translation.__str__()

        assert isinstance(string, str)
        assert string == str(new_label_translation.translated_name)

class TestProjectComment(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.project_comment = ProjectCommentFactory()

    def test_new_label_translation_str_method(self):
        new_project_comment = self.project_comment
        string = new_project_comment.__str__()

        assert isinstance(string, str)
        assert string == 'Comment {} by {}'.format(new_project_comment.message, new_project_comment.community)

class TestProjectStatus(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.project_status = ProjectStatusFactory()

    def test_new_project_status_str_method(self):
        new_project_status = self.project_status
        string = new_project_status.__str__()

        assert isinstance(string, str)
        assert string == f"{new_project_status.community} - {new_project_status.seen} - {new_project_status.status}"

class TestLabelNote(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.label_note = LabelNoteFactory()

    def test_new_project_status_str_method(self):
        new_label_note = self.label_note
        string = new_label_note.__str__()

        assert isinstance(string, str)
        assert string == f"{new_label_note.bclabel} - {new_label_note.tklabel} - {new_label_note.sender}"

class TestLabelVersion(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.label_version = LabelVersionFactory()

    def test_new_label_version_str_method(self):
        new_label_version = self.label_version
        string = new_label_version.__str__()

        assert isinstance(string, str)
        assert string == f"{new_label_version.bclabel} - {new_label_version.tklabel} - {new_label_version.version}"

class TestLabelTranslationVersion(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.label_translation_version = LabelTranslationVersionFactory()

    def test_new_label_translation_version_str_method(self):
        new_label_translation_version = self.label_translation_version
        string = new_label_translation_version.__str__()

        assert isinstance(string, str)
        assert string == f"{new_label_translation_version.version_instance}"

class TestNoticeDownloadTracker(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.notice_download_tracker = NoticeDownloadTrackerFactory()

    def test_new_notice_download_tracker_str_method(self):
        new_notice_download_tracker = self.notice_download_tracker
        string = new_notice_download_tracker.__str__()

        assert isinstance(string, str)
        assert string == new_notice_download_tracker.user.get_full_name()

class TestCollectionsCareNoticePolicy(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.collections_care_notice = CollectionsCareNoticePolicyFactory()

    def test_new_collections_care_notice_str_method(self):
        new_collections_care_notice = self.collections_care_notice
        string = new_collections_care_notice.__str__()

        assert isinstance(string, str)
        assert string == new_collections_care_notice.institution.institution_name

class TestHubActivity(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.hub_activity = HubActivityFactory()