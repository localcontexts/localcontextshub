import os
import time
import urllib.parse
from pathlib import Path

import faker
import pytest
from django.urls import reverse
from selenium.webdriver.common.alert import Alert

from functional.ui_feature_testcase_base import UiFeatureHelper

from communities.models import Community


class TestFeatures(UiFeatureHelper):
    def setUp(self):
        self.login()
        self.alert_dialog = Alert(self.py.webdriver)
        self.community_name = 'placeholder'
        self.fake = faker.Faker()
        test_folder = Path(
            os.path.realpath(__file__)
        ).parents[1]
        self.shapefile_folder = os.path.join(test_folder, 'fixtures', 'files', 'shapefiles')
        self.create_community_path = reverse('create-community')
        self.select_add_boundary_method_path = reverse('community-boundary')
        self.select_nld_add_boundary_method_path = reverse('add-community-boundary')
        self.select_upload_boundary_file_method_path = reverse('upload-boundary-file')
        self.dashboard = reverse('dashboard')

    def fill_out_and_submit_account_creation_form(self):
        # set the community name; we may use this name
        # later to verify the community was created properly
        self.community_name = self.fake.name()

        # fill out form
        self.py.get("[name='first_name']").type(self.community_name)
        self.py.get("[name='last_name']").type(self.fake.name())
        self.py.get("[name='community_name']").type(self.fake.name())
        self.py.get("[name='community_entity']").type(self.fake.name())
        self.py.get("[name='state_province_region']").type(self.fake.name())
        self.py.get("[name='country']").type('Antartica')
        self.py.get("#id_description").type('a')
        self.py.get("[name='contact_name']").type('Test User')
        self.py.get("#communityContactEmailField").type(self.fake.email())

        # submit form
        time.sleep(10)
        self.py.get(".primary-btn").click()
        time.sleep(30)

    def select_native_land_method_and_submit(self):
        # pick NLD add boundary radio button
        self.py.get(f"[data-next='{self.select_nld_add_boundary_method_path}']").click()

        # submit form
        self.py.get(".primary-btn").click()

    def select_upload_shapefile_and_submit(self):
        # pick upload shapefile radio button
        self.py.get(f"[data-next='{self.select_upload_boundary_file_method_path}']").click()

        # submit form
        self.py.get(".primary-btn").click()

    def select_specific_nld_territory(self, nld_terriroty: str):
        time.sleep(5)   # wait for ajax call for NLD to load
        self.py.get(".input-field.search").type(nld_terriroty)
        self.py.get("#region-results .result-item").click()

    def select_share_boundary_publicly(self):
        self.py.get("#share-boundary-publicly").click()

    def accept_cookies(self):
        # this removes the accept-cookies overlay so other
        # buttons below overlay can be clicked
        self.py.get("[class~='cookie-btn']").click()

    def navigate_to_search_native_land_digital_database_page(self):
        create_community_url = urllib.parse.urljoin(self.live_server_url, self.create_community_path)
        self.py.visit(create_community_url)

        # click accept cookies button
        time.sleep(5)   # wait for accept banner to appear
        self.accept_cookies()
        time.sleep(15)
        self.fill_out_and_submit_account_creation_form()

        # verify user is on select add boundary method page
        assert self.select_add_boundary_method_path in self.get_current_url()

        # self.select_native_land_method_and_submit()
        #
        # # verify user is on select boundary by nld page
        # assert self.select_nld_add_boundary_method_path in self.get_current_url()

    def navigate_to_upload_shapefile_page(self):
        create_community_url = urllib.parse.urljoin(self.live_server_url, self.create_community_path)
        self.py.visit(create_community_url)

        # click accept cookies button
        time.sleep(20)   # wait for accept banner to appear
        self.accept_cookies()

        self.fill_out_and_submit_account_creation_form()

        # verify user is on select add boundary method page
        assert self.select_add_boundary_method_path in self.get_current_url()

        self.select_upload_shapefile_and_submit()

        # verify user is on select boundary by upload shapefile page
        assert self.select_upload_boundary_file_method_path in self.get_current_url()

    def test_select_native_land_digital_territory_with_share_publicly(self):
        self.navigate_to_search_native_land_digital_database_page()
        selected_territory = 'panamakas'

        # select an nld territory
        self.select_specific_nld_territory(selected_territory)
        self.select_share_boundary_publicly()

        # navigate to next page
        self.py.get("#community-boundary-continue-btn").click()

        # verify user is on the confirm community page
        assert self.dashboard in self.get_current_url()

        # verify community and boundary exists with the expected values
        created_community = Community.objects.get(community_name=self.community_name)
        assert created_community.share_boundary_publicly, 'Share Boundary Publicly Should Be True'
        assert created_community.name_of_boundary == selected_territory
        assert created_community.source_of_boundary == 'https://native-land.ca/maps/territories/panamakas'
        assert created_community.boundary.geometry is not None, 'Territory Should Have Coordinates'

    def test_select_native_land_digital_territory_without_share_publicly(self):
        self.navigate_to_search_native_land_digital_database_page()
        selected_territory = 'panamakas'

        # select an nld territory
        self.select_specific_nld_territory(selected_territory)

        # navigate to next page
        self.py.get("#community-boundary-continue-btn").click()

        # verify user is on the confirm community page
        time.sleep(5)   # wait for ajax call to finish
        assert self.dashboard in self.get_current_url()

        # verify community and boundary exists with the expected values
        created_community = Community.objects.get(community_name=self.community_name)
        assert not created_community.share_boundary_publicly, 'Share Boundary Publicly Should Be False'
        assert created_community.name_of_boundary == selected_territory
        assert created_community.source_of_boundary == 'https://native-land.ca/maps/territories/panamakas'
        assert created_community.boundary.geometry is not None, 'Territory Should Have Coordinates'

    def test_clicking_upload_shapefile_on_nld_page_navigates_to_upload_shapefile_page(self):
        self.navigate_to_search_native_land_digital_database_page()

        # self.py.get("#navigate-to-option a").click()
        #
        # # verify user is on the upload shapefile page
        # assert self.select_upload_boundary_file_method_path in self.get_current_url()

    def test_clicking_skip_this_step_on_nld_page_navigates_to_confirm_page(self):
        self.navigate_to_search_native_land_digital_database_page()

        self.py.get("#skip-this-step a").click()

        # verify user is on the dashboard page after skipping
        assert self.dashboard in self.get_current_url()

    def click_okay_on_alert_dialog(self):
        self.alert_dialog.accept()

    def test_select_shapefile_with_share_publicly(self):
        self.navigate_to_upload_shapefile_page()
        shapefile = os.path.join(self.shapefile_folder, 'shapefile-dr-janette-file.zip')
        selected_territory = 'Kahurautao'

        self.py.get("#shapefile-input").upload(shapefile)

        # wait for alert dialog to open
        time.sleep(4)
        expected_alert_warning = "Warning:\nThere is more than 1 boundary present. Only the first will be used."
        assert self.alert_dialog.text == expected_alert_warning

        self.click_okay_on_alert_dialog()

        # wait for alert dialog to close
        time.sleep(4)
        self.select_share_boundary_publicly()

        # navigate to next page
        self.py.get("#community-boundary-continue-btn").click()

        # wait for ajax call
        time.sleep(4)
        # verify user is on the dashbaord page
        assert self.dashboard in self.get_current_url()

        # verify community and boundary exists with the expected values
        created_community = Community.objects.get(community_name=self.community_name)
        assert created_community.share_boundary_publicly, 'Share Boundary Publicly Should Be True'
        assert created_community.name_of_boundary == selected_territory
        assert created_community.source_of_boundary == 'shape-file'
        assert created_community.boundary.geometry is not None, 'Territory Should Have Coordinates'

    def test_select_shapefile_without_share_publicly(self):
        self.navigate_to_upload_shapefile_page()
        shapefile = os.path.join(self.shapefile_folder, 'shapefile-dr-janette-file.zip')
        selected_territory = 'Kahurautao'

        self.py.get("#shapefile-input").upload(shapefile)

        # wait for alert dialog to open
        time.sleep(4)
        expected_alert_warning = "Warning:\nThere is more than 1 boundary present. Only the first will be used."
        assert self.alert_dialog.text == expected_alert_warning

        self.click_okay_on_alert_dialog()

        # navigate to next page
        self.py.get("#community-boundary-continue-btn").click()

        # wait for ajax call
        time.sleep(4)
        # verify user is on the dashbaord page
        assert self.dashboard in self.get_current_url()

        # verify community and boundary exists with the expected values
        created_community = Community.objects.get(community_name=self.community_name)
        assert not created_community.share_boundary_publicly, 'Share Boundary Publicly Should Be False'
        assert created_community.name_of_boundary == selected_territory
        assert created_community.source_of_boundary == 'shape-file'
        assert created_community.boundary.geometry is not None, 'Territory Should Have Coordinates'

    def test_clicking_select_by_nld_on_upload_shapefile_page_navigates_to_select_by_nld_page(self):
        self.navigate_to_upload_shapefile_page()

        self.py.get("#navigate-to-option a").click()

        # verify user is on the select by nld page
        assert self.select_nld_add_boundary_method_path in self.get_current_url()

    def test_clicking_skip_this_step_on_upload_shapefile_page_navigates_to_confirm_page(self):
        self.navigate_to_upload_shapefile_page()

        self.py.get("#skip-this-step a").click()

        # verify user is on the dashbaord page
        assert self.dashboard in self.get_current_url()
