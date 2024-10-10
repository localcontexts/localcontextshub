import time
import urllib

import pytest
from django.urls import reverse

from functional.ui_feature_testcase_base import UiFeatureHelper
from factories.projects_factories import ProjectFactory
from communities.models import Community, Boundary
from institutions.models import Institution
from projects.models import Project


@pytest.mark.skip(reason="disable until NLD update")
@pytest.mark.usefixtures("py")
class TestBoundaryClearedFeatures(UiFeatureHelper):
    def setUp(self):
        self.login()
        self.original_source_of_boundary = 'native-land.ca'
        self.original_name_of_boundary = 'placeholder-boundary-name'
        self.original_boundary_coordinates = [
                [0, 0], [0, 1], [0, 2]
        ]
        self.community_project = None
        self.institution_project = None
        self.community = None
        self.institution = None

    def accept_cookies(self):
        # this removes the accept-cookies overlay so other
        # buttons below overlay can be clicked
        self.py.get("[class~='cookie-btn']").click()

    def select_specific_nld_territory(self, nld_terriroty: str):
        time.sleep(5)   # wait for ajax call for NLD to load
        self.py.get(".input-field.search").type(nld_terriroty)
        self.py.get(".region-results .result-item").click()

    def create_project_and_community(self):
        self.community = Community(
            community_creator=self.user,
        )
        self.community.save()
        boundary = Boundary(
            coordinates=self.original_boundary_coordinates
        )
        boundary.save()
        self.community_project = ProjectFactory(
            project_creator=self.user,
            boundary=boundary,
            source_of_boundary=self.original_source_of_boundary,
            name_of_boundary=self.original_name_of_boundary,
            urls=[]
        )
        self.community_project.save()

    def create_project_and_institution(self):
        self.institution = Institution(
            institution_creator=self.user,
        )
        self.institution.save()
        boundary = Boundary(
            coordinates=self.original_boundary_coordinates
        )
        boundary.save()
        self.institution_project = ProjectFactory(
            project_creator=self.user,
            boundary=boundary,
            source_of_boundary=self.original_source_of_boundary,
            name_of_boundary=self.original_name_of_boundary,
            urls=[]
        )
        self.institution_project.save()

    def confirm_preexisting_project_boundary_was_not_overwritten_for_community(self):
        # confirm in the UI on project actions view page
        boundary_title = self.py.get("[data-test-id='native-land-link']")
        boundary_title.should().be_visible()
        boundary_title.should().have_text(
            self.original_name_of_boundary
        )

        boundary_url_source = boundary_title.get_attribute('href')
        assert self.original_source_of_boundary in boundary_url_source, 'Unexpected Url'

        # reload project and confirm its boundary coordinates are the same
        reloaded_project = Project.objects.get(unique_id=self.community_project.unique_id)
        reloaded_boundary_coordinates = reloaded_project.boundary.get_coordinates()
        original_boundary_coordinates = self.community_project.boundary.get_coordinates()
        assert original_boundary_coordinates == reloaded_boundary_coordinates, 'Unexpected Coordinates'

    def confirm_preexisting_project_boundary_was_not_overwritten_for_institution(self):
        # confirm in the UI on project actions view page
        boundary_title = self.py.get("[data-test-id='native-land-link']")
        boundary_title.should().be_visible()
        boundary_title.should().have_text(
            self.original_name_of_boundary
        )

        boundary_url_source = boundary_title.get_attribute('href')
        assert self.original_source_of_boundary in boundary_url_source, 'Unexpected Url'

        # reload project and confirm its boundary coordinates are the same
        reloaded_project = Project.objects.get(unique_id=self.institution_project.unique_id)
        reloaded_boundary_coordinates = reloaded_project.boundary.get_coordinates()
        original_boundary_coordinates = self.institution_project.boundary.get_coordinates()
        assert original_boundary_coordinates == reloaded_boundary_coordinates, 'Unexpected Coordinates'

    def test_that_cleared_project_boundaries_are_not_saved_for_a_community(self):
        self.create_project_and_community()

        # visit project edit page for community
        project_url = urllib.parse.urljoin(
            self.live_server_url, reverse(
                'edit-project',
                kwargs={
                    'pk': self.community.id,
                    'project_uuid': self.community_project.unique_id,
                }
            )
        )
        self.py.visit(project_url)

        # click accept cookies button
        time.sleep(5)   # wait for accept banner to appear
        self.accept_cookies()

        # select NLD territory
        selected_territory = 'panamakas'
        self.select_specific_nld_territory(selected_territory)

        # clear boundary
        time.sleep(5)   # wait for boundary selection to occur
        clear_boundary_button = self.py.get("#cancel-btn")
        clear_boundary_button.click()

        # save page
        time.sleep(5)   # wait for boundary selection to occur
        save_project_button = self.py.get("#submitProjectBtn")
        save_project_button.click()

        self.confirm_preexisting_project_boundary_was_not_overwritten_for_community()

    def test_that_cleared_project_boundaries_are_not_saved_for_an_institution(self):
        self.create_project_and_institution()

        # visit project edit page for institution
        project_url = urllib.parse.urljoin(
            self.live_server_url, reverse(
                'inst-edit-project',
                kwargs={
                    'pk': self.institution.id,
                    'project_uuid': self.institution_project.unique_id,
                }
            )
        )
        self.py.visit(project_url)

        # click accept cookies button
        time.sleep(5)   # wait for accept banner to appear
        self.accept_cookies()

        # select NLD territory
        selected_territory = 'panamakas'
        self.select_specific_nld_territory(selected_territory)

        # clear boundary
        time.sleep(5)   # wait for boundary selection to occur
        clear_boundary_button = self.py.get("#cancel-btn")
        clear_boundary_button.click()

        # save page
        time.sleep(5)   # wait for boundary selection to occur
        save_project_button = self.py.get("#submitProjectBtn")
        save_project_button.click()

        self.confirm_preexisting_project_boundary_was_not_overwritten_for_institution()
