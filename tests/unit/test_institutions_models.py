from django.test import TestCase
import pytest
from factories.accounts_factories import UserFactory
from factories.institutions_factories import InstitutionFactory


class TestInstitute(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.institution = InstitutionFactory()
        self.user = UserFactory()

    def test_get_location(self):
        new_institution = self.institution
        new_institution.city_town = "Test City"
        new_institution.state_province_region = "Test State"
        new_institution.country = "Test Country"
        new_institution.is_approved = True
        new_institution.save()

        expected_location = "Test City, Test State, Test Country"
        assert new_institution.get_location() == expected_location

    def test_get_location_none_specified(self):
        new_institution = self.institution
        new_institution.city_town = None
        new_institution.state_province_region = None
        new_institution.country = None
        new_institution.save()

        assert new_institution.get_location() == "None specified"

    def test_get_member_count(self):
        new_institution = self.institution
        new_institution.admins.add(self.user)
        new_institution.save()

        member_count = new_institution.get_member_count()
        expected_member_count = 2

        assert member_count == expected_member_count

    def test_get_member_count_no_members(self):
        new_institution = self.institution
        member_count = new_institution.get_member_count()
        expected_member_count = 1

        assert member_count == expected_member_count

    def test_model_methods(self):
        new_institution = self.institution
        admin = UserFactory()
        new_institution.admins.add(admin)
        editors = UserFactory()
        new_institution.editors.add(editors)
        viewers = UserFactory()
        new_institution.viewers.add(viewers)

        # Test get_admins
        admins_list = new_institution.get_admins()
        assert all(
            [admin in admins_list for admin in new_institution.admins.all()])

        # Test get_editors
        editors_list = new_institution.get_editors()
        assert all([
            editor in editors_list for editor in new_institution.editors.all()
        ])

        # Test get_viewers
        viewers_list = new_institution.get_viewers()
        assert all([
            viewer in viewers_list for viewer in new_institution.viewers.all()
        ])

    def test_is_user_in_institution(self):
        new_institution = self.institution
        new_institution.viewers.add(self.user)

        result = new_institution.is_user_in_institution(self.user)
        assert isinstance(result, bool)

    def test_str_method(self):
        new_institution = self.institution
        string = str(new_institution)

        assert isinstance(string, str)
        assert string == new_institution.institution_name
