from django.test import TestCase
import pytest
from factories.researchers_factories import ResearcherFactory


class TestResearcher(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.researcher = ResearcherFactory()

    def test_get_projects_exists(self):
        result = self.researcher.get_projects()

        assert isinstance(result, bool)

    def test_str_method(self):
        string = str(self.researcher)

        assert isinstance(string, str)
        assert string == str(self.researcher)
