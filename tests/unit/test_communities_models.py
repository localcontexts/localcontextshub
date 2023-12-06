import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from communities.models import Community
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory, InviteMemberFactory, JoinRequestFactory


# This fixture for Community model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_community():
    return CommunityFactory()

# This test is for Community model validation of community_name uniqueness
@pytest.mark.django_db
def test_community_creation_with_unique_name(new_community):
    name = new_community.community_name
    with pytest.raises(Exception):
        Community.objects.create(community_name=name)

# This test is for Community model get_location method
@pytest.mark.django_db
def test_get_location(new_community):
    community =new_community
    community.city_town = None
    community.state_province_region = None
    community.country = None
    community.save()
    expected_result = 'None specified'
    result = community.get_location()
    assert result == expected_result

# Test for Community model image upload
@pytest.mark.django_db
def test_community_image_upload(new_community):
    image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
    new_community.image = image_file
    new_community.save()
    assert new_community.image.url is not None

# Test for Community model support document upload
@pytest.mark.django_db
def test_community_support_document_upload(new_community):
    document_file = SimpleUploadedFile("test_document.txt", b"file_content", content_type="text/plain")
    new_community.support_document = document_file
    new_community.save()
    assert new_community.support_document.url is not None

# This test is for Community model __str__ method
@pytest.mark.django_db
def test_str_method(new_community):
    community = new_community
    string = str(community)
    assert isinstance(string, str)
    assert string == community.community_name

# This test is for Community model is_user_in_community method
@pytest.mark.django_db
def test_is_user_in_community(new_community):
    user_in_community = UserFactory()
    new_community.admins.set([new_community.admins.first(), user_in_community])
    assert new_community.is_user_in_community(user_in_community)

# This test is for Community model get_collaborator method
@pytest.mark.django_db
def test_get_collaborator(new_community):
    user = UserFactory()
    new_community.admins.add(user)
    collaborators = new_community.get_collaborator()
    assert all(u in collaborators for u in new_community.admins.all())


@pytest.mark.django_db    
def test_model_methods(new_community):
    # Test get_admins
    admin = UserFactory()
    community = new_community
    community.admins.add(admin)
    admins = community.get_admins()
    assert admin, admins

    # Test get_editors
    editor = UserFactory()
    community.editors.add(editor)
    editors = community.get_editors()
    assert editor, editors

    # Test get_viewers
    viewer = UserFactory()
    community.viewers.add(viewer)
    viewers = community.get_viewers()
    assert viewer, viewers
    
    member_count = community.get_member_count()
    expected_member_count = 7
    assert member_count == expected_member_count

# This fixture for InviteMember model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_invite_member():
    return InviteMemberFactory()

# This test is for InviteMember model __str__ method
@pytest.mark.django_db
def test_new_invite_member_str_method(new_invite_member):
    invite_member = new_invite_member
    string = str(invite_member)
    assert isinstance(string, str)
    assert string == f"{invite_member.sender}-{invite_member.receiver}-{invite_member.status}"

# This fixture for JoinRequest model instance creation
@pytest.fixture
@pytest.mark.django_db
def new_join_request():
    return JoinRequestFactory()

# This test is for JoinRequest model __str__ method
@pytest.mark.django_db
def test_new_join_request_str_method(new_join_request):
    join_request = new_join_request
    string = str(join_request)
    assert isinstance(string, str)
    assert string == f"{join_request.user_from}-{join_request.user_to}-{join_request.status}"