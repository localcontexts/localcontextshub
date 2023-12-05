import pytest
import requests
from unittest.mock import patch
from django.test import TestCase
from factories.accounts_factories import UserFactory
from helpers.models import Notice, NoticeTranslation
from factories.communities_factories import CommunityFactory
from factories.institutions_factories import InstitutionFactory
from factories.researchers_factories import ResearcherFactory
from factories.helpers_factories import NoticeFactory, NoticeTranslationFactory, OpenToCollaborateNoticeURLFactory,EntitiesNotifiedFactory,LabelTranslationFactory, ProjectCommentFactory, NoticeDownloadTrackerFactory, HubActivityFactory, LabelTranslationVersionFactory, LabelVersionFactory,LabelNoteFactory, ProjectStatusFactory, CollectionsCareNoticePolicyFactory


# Fixture for Notice model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_notice():
    return NoticeFactory()

# Test case for creating a Notice instance
@pytest.mark.django_db
def test_create_notice(new_notice):
    assert isinstance(new_notice, Notice)
    assert new_notice.pk is not None

# Test case for the __str__ method
@pytest.mark.django_db
def test_notice_str_method(new_notice):
    result = new_notice.__str__()

    assert isinstance(result, str)

# Test case for the set_translation method
@pytest.mark.django_db
def test_notice_set_translation(new_notice):
    language_tag = 'fr'
    new_notice.set_translation(language_tag)
    translation = NoticeTranslation.objects.filter(notice=new_notice, language_tag=language_tag).first()
    
    assert translation is not None
    assert translation.translated_text is not None
    
# Fixture for NoticeTranslation model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_notice_translation():
    return NoticeTranslationFactory()

# Test case for NoticeTranslation __str__ method
@pytest.mark.django_db
def test_notice_translation_str_method(new_notice_translation):
    result = new_notice_translation.__str__()

    assert isinstance(result, str)
    assert result == str(new_notice_translation)
    
# Fixture for OpenToCollaborateNoticeURL model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_open_to_collaborate_notice_url():
    return OpenToCollaborateNoticeURLFactory()

# Test case for OpenToCollaborateNoticeURL __str__ method
@pytest.mark.django_db
def test_open_to_collaborate_notice_url_str_method(new_open_to_collaborate_notice_url):
    result = new_open_to_collaborate_notice_url.__str__()

    assert isinstance(result, str)
    assert result == str(new_open_to_collaborate_notice_url.name)

# Fixture for EntitiesNotified model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_entities_notified():
    return EntitiesNotifiedFactory()


# Test case for EntitiesNotified is_user_authenticated method  
@pytest.mark.django_db
def test_is_user_in_notified_account(new_entities_notified):
    entities_notified = new_entities_notified

    # Create user objects for different account types
    community_user = UserFactory()
    institution_user = UserFactory()
    researcher_user = UserFactory()
    
    community = CommunityFactory()
    community.viewers.add(community_user)
    institution = InstitutionFactory()
    institution.viewers.add(institution_user)
    
    # Add communities, institutions, and researchers to EntitiesNotified
    entities_notified.communities.add(community)
    entities_notified.institutions.add(institution)
  
    assert entities_notified.is_user_in_notified_account(community_user) is True
    assert entities_notified.is_user_in_notified_account(institution_user) is True

# Test case for EntitiesNotified __str__ method  
@pytest.mark.django_db
def test_entities_notified_str_method(new_entities_notified):
    result = new_entities_notified.__str__()

    assert isinstance(result, str)
    assert result == str(new_entities_notified.project.title)

# Fixture for LabelTranslation model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_label_translation():
    return LabelTranslationFactory()

# Test case for LabelTranslation __str__ method  
@pytest.mark.django_db
def test_new_label_translation_str_method(new_label_translation):
    result = new_label_translation.__str__()

    assert isinstance(result, str)
    assert result == str(new_label_translation.translated_name)

# Fixture for ProjectComment model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project_comment():
    return ProjectCommentFactory()

# Test case for ProjectComment __str__ method  
@pytest.mark.django_db
def test_new_project_comment_str_method(new_project_comment):
    result = new_project_comment.__str__()

    assert isinstance(result, str)

# Fixture for ProjectStatus model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_project_status():
    return ProjectStatusFactory()

# Test case for ProjectStatus __str__ method 
@pytest.mark.django_db
def test_new_project_status_str_method(new_project_status):
    result = new_project_status.__str__()

    assert isinstance(result, str)

# Fixture for LabelNote model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_label_note():
    return LabelNoteFactory()

# Test case for LableNote __str__ method 
@pytest.mark.django_db
def test_new_label_note_str_method(new_label_note):
    result = new_label_note.__str__()

    assert isinstance(result, str)

# Fixture for LabelVersion model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_label_version():
    return LabelVersionFactory()

# Test case for LabelVersion __str__ method 
@pytest.mark.django_db
def test_new_label_version_str_method(new_label_version):
    result = new_label_version.__str__()

    assert isinstance(result, str)

# Fixture for LabelTranslationVersion model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_label_translation_version():
    return LabelTranslationVersionFactory()

# Test case for LabelTranslationVersion __str__ method 
@pytest.mark.django_db
def test_new_label_translation_version_str_method(new_label_translation_version):
    result = new_label_translation_version.__str__()

    assert isinstance(result, str)

# Fixture for NoticeDownloadTracker model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_notice_download_tracker():
    return NoticeDownloadTrackerFactory()

# Test case for NoticeDownloadTracker __str__ method 
@pytest.mark.django_db
def test_new_notice_download_tracker_str_method(new_notice_download_tracker):
    result = new_notice_download_tracker.__str__()

    assert isinstance(result, str)

# Fixture for CollectionsCareNoticePolicy model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_collections_care_notice():
    return CollectionsCareNoticePolicyFactory()

# Test case for CollectionsCareNoticePolicy __str__ method 
@pytest.mark.django_db
def test_new_collections_care_notice_str_method(new_collections_care_notice):
    result = new_collections_care_notice.__str__()

    assert isinstance(result, str)

# Fixture for HubActivity model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_hub_activity():
    return HubActivityFactory()

# Test case for HubActivity __str__ method 
@pytest.mark.django_db
def test_new_hub_activity_str_method(new_hub_activity):
    result = new_hub_activity.__str__()

    assert isinstance(result, str)
