import urllib.parse

import faker
import pytest
from django.urls import reverse
from faker import factory

from functional.ui_feature_testcase_base import UiFeatureHelper


@pytest.mark.usefixtures("py")
class TestFeatures(UiFeatureHelper):
    def setUp(self):
        self.login()
        self.fake = faker.Faker()
        self.create_community_path = reverse('create-community')
        self.select_add_boundary_method = reverse('community-boundary')

    def fill_out_and_submit_account_creation_form(self):
        # fill out form
        self.py.get("[name='community_name']").type(self.fake.name())
        self.py.get("[name='community_entity']").type('a')
        self.py.get("[name='state_province_region']").type('a')
        self.py.get("[name='country']").type('Antartica')
        self.py.get("#id_description").type('a')

        # submit form
        self.py.get(".primary-btn").click()

    def select_native_land

    def test_can_select_search_the_native_land_digital_database(self):
        create_community_url = urllib.parse.urljoin(self.live_server_url, self.create_community_path)
        self.py.visit(create_community_url)

        self.fill_out_and_submit_account_creation_form()

        # verify user is on select add boundary method page
        assert self.py.url().endswith(self.select_add_boundary_method)

        # assert webpage is the selection page
        # click on
        nld_add_community_boundary = reverse('a')
        # self.py.get("[data-next='selectBoundary']").click()