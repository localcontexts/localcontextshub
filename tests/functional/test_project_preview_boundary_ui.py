import time
import urllib

import pytest
from django.urls import reverse

from functional.ui_feature_testcase_base import UiFeatureHelper
from factories.projects_factories import ProjectFactory
from communities.models import Community
from institutions.models import Institution


@pytest.mark.usefixtures("py")
class TestProjectBoundaryPreviewFeatures(UiFeatureHelper):
    def setUp(self):
        self.login()
        self.community_project = None
        self.institution_project = None
        self.community = None
        self.institution = None

    def accept_cookies(self):
        # this removes the accept-cookies overlay so other
        # buttons below overlay can be clicked
        time.sleep(5)   # wait for accept banner to appear
        self.py.get("[class~='cookie-btn']").click()

    def select_specific_nld_territory(self):
        time.sleep(5)   # wait for ajax call for NLD to load
        selected_territory = 'Panamakas'
        self.py.get(".input-field.search").type(selected_territory)
        self.py.get(".region-results .result-item").click()

    def create_project_and_community(self):
        self.community = Community(
            community_creator=self.user,
        )
        self.community.save()
        self.community_project = ProjectFactory(
            project_creator=self.user,
            urls=[]
        )
        self.community_project.save()

    def create_project_and_institution(self):
        self.institution = Institution(
            institution_creator=self.user,
        )
        self.institution.save()
        self.institution_project = ProjectFactory(
            project_creator=self.user,
            urls=[]
        )
        self.institution_project.save()

    def verify_expected_boundary_data_is_present(self):
        # grab the boundary variable from Javascript
        boundary = self.py.webdriver.execute_script('return boundary')
        assert len(boundary) > 0, 'Boundary preview data should exist'

    def test_project_boundary_preview_for_a_community(self):
        self.accept_cookies()
        self.create_project_and_community()

        # visit project edit page for community
        community_project_url = urllib.parse.urljoin(
            self.live_server_url, reverse(
                'edit-project',
                kwargs={
                    'pk': self.community.id,
                    'project_uuid': self.community_project.unique_id,
                }
            )
        )
        self.py.visit(community_project_url)
        self.select_specific_nld_territory()

        time.sleep(5) # wait for Javascript actions
        boundary_preview_url = urllib.parse.urljoin(
            self.live_server_url, reverse('boundary-preview')
        )
        self.py.visit(boundary_preview_url)
        self.verify_expected_boundary_data_is_present()

    def test_project_boundary_preview_for_an_institution(self):
        self.accept_cookies()
        self.create_project_and_institution()

        # visit project edit page for community
        institution_project_url = urllib.parse.urljoin(
            self.live_server_url, reverse(
                'inst-edit-project',
                kwargs={
                    'pk': self.institution.id,
                    'project_uuid': self.institution_project.unique_id,
                }
            )
        )
        self.py.visit(institution_project_url)
        self.select_specific_nld_territory()

        time.sleep(5) # wait for Javascript actions
        boundary_preview_url = urllib.parse.urljoin(
            self.live_server_url, reverse('boundary-preview')
        )
        self.py.visit(boundary_preview_url)
        self.verify_expected_boundary_data_is_present()
