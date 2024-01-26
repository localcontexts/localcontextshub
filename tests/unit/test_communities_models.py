import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from communities.models import Community
from factories.accounts_factories import UserFactory
from factories.communities_factories import CommunityFactory, JoinRequestFactory


class TestCommunity(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.new_community = CommunityFactory()

    def test_community_creation_with_unique_name(self):
        name = self.new_community.community_name
        with pytest.raises(Exception):
            Community.objects.create(community_name=name)

    def test_get_location(self):
        community = self.new_community
        community.city_town = None
        community.state_province_region = None
        community.country = None
        community.save()
        expected_result = "None specified"
        result = community.get_location()
        assert result == expected_result

    def test_community_image_upload(self):
        image_file = SimpleUploadedFile("test_image.jpg",
                                        b"file_content",
                                        content_type="image/jpeg")
        self.new_community.image = image_file
        self.new_community.save()
        assert self.new_community.image.url is not None

    def test_community_support_document_upload(self):
        document_file = SimpleUploadedFile("test_document.txt",
                                           b"file_content",
                                           content_type="text/plain")
        self.new_community.support_document = document_file
        self.new_community.save()
        assert self.new_community.support_document.url is not None

    def test_str_method(self):
        community = self.new_community
        string = str(community)
        assert isinstance(string, str)
        assert string == community.community_name

    def test_is_user_in_community(self):
        user_in_community = UserFactory()
        self.new_community.admins.set(
            [self.new_community.admins.first(), user_in_community])
        assert self.new_community.is_user_in_community(user_in_community)

    def test_get_collaborator(self):
        user = UserFactory()
        self.new_community.admins.add(user)
        collaborators = self.new_community.get_collaborator()
        assert all(u in collaborators for u in self.new_community.admins.all())

    def test_get_methods(self):
        admin = UserFactory()
        self.new_community.admins.add(admin)
        admins = self.new_community.get_admins()
        assert admin, admins

        editor = UserFactory()
        self.new_community.editors.add(editor)
        editors = self.new_community.get_editors()

        assert editor, editors

        viewer = UserFactory()
        self.new_community.viewers.add(viewer)
        viewers = self.new_community.get_viewers()
        assert viewer, viewers

        member_count = self.new_community.get_member_count()
        expected_member_count = 7
        assert member_count == expected_member_count


class TestJoinRequest(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.new_join_request = JoinRequestFactory()

    def test_new_join_request_str_method(self):
        join_request = self.new_join_request
        string = str(join_request)
        assert isinstance(string, str)
        assert string == f"{join_request.user_from}-{join_request.user_to}-{join_request.status}"
