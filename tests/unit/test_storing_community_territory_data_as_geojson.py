import pytest
from django.test import TestCase
from marshmallow import ValidationError

from communities.models import Boundary
from helpers.schema import GEOJSON_MULTI_POLYGON_TYPE


class TestStoringCoordinatesAsGeoJson(TestCase):
    def setUp(self):
        self.expected_geometry = {
            'type': GEOJSON_MULTI_POLYGON_TYPE, 'coordinates': [
                [[(0, 0), (1, 1), (2, 2), (3, 3)]],
                [[(4, 4), (5, 5), (6, 6), (7, 7)]]
            ],
        }
        self.boundary = Boundary(
            geometry=self.expected_geometry
        )
        self.boundary.save()

    def test_coordinates_can_be_saved_as_geo_polygons(self):
        self.assertEqual(self.boundary.geometry, self.expected_geometry)

    def test_non_geo_coordinates_as_tuple(self):
        expected_coordinates = self.expected_geometry['coordinates'][0][0]
        observed_coordinates = self.boundary.get_coordinates()
        self.assertEqual(observed_coordinates, expected_coordinates)

    def test_non_geo_coordinates_as_list(self):
        expected_coordinates = [
            [c[0], c[1]] for c in self.expected_geometry['coordinates'][0][0]
        ]
        observed_coordinates = self.boundary.get_coordinates(as_tuple=False)
        self.assertEqual(observed_coordinates, expected_coordinates)

    def test_geojson_raises_error_for_invalid_geojson_type(self):
        geometry_with_invalid_geojson_type = {
            'type': 'some invalid GeoJson type', 'coordinates': [
                [[(0, 0), (1, 1), (2, 2), (3, 3)]],
                [[(4, 4), (5, 5), (6, 6), (7, 7)]]
            ],
        }
        boundary = Boundary(
            geometry=geometry_with_invalid_geojson_type
        )
        with pytest.raises(ValidationError) as e:
            boundary.save()
        assert e.value.args[0]['type'][0] == 'Invalid multi polygon type'

    def test_geojson_raises_error_for_invalid_geojson_coordinate_key(self):
        geometry_with_invalid_geojson_coordinate_key = {
            'type': GEOJSON_MULTI_POLYGON_TYPE, 'some invalid coordinates key': [
                [[(0, 0), (1, 1), (2, 2), (3, 3)]],
                [[(4, 4), (5, 5), (6, 6), (7, 7)]]
            ],
        }
        boundary = Boundary(
            geometry=geometry_with_invalid_geojson_coordinate_key
        )
        with pytest.raises(ValidationError) as e:
            boundary.save()
        assert e.value.args[0]['coordinates'][0] == 'Missing data for required field.'

    def test_geojson_raises_error_for_invalid_geojson_coordinate_value(self):
        geometry_with_invalid_geojson_coordinate_key = {
            'type': GEOJSON_MULTI_POLYGON_TYPE,
            'coordinates': 'some invalid coordinates value',
        }
        boundary = Boundary(
            geometry=geometry_with_invalid_geojson_coordinate_key
        )
        with pytest.raises(ValidationError) as e:
            boundary.save()
        assert e.value.args[0]['coordinates'][0] == 'Not a valid list.'

    def test_geojson_raises_error_for_invalid_geojson_lat_lon(self):
        geometry_with_invalid_geojson_coordinate_key = {
            'type': GEOJSON_MULTI_POLYGON_TYPE, 'coordinates': [
                [[(0, 900), (900, 1), (2, 2), (3, 3)]],
            ],
        }
        boundary = Boundary(
            geometry=geometry_with_invalid_geojson_coordinate_key
        )
        with pytest.raises(ValidationError) as e:
            boundary.save()

        assert e.value.args[0]['coordinates'][0][0][0][1] == ['Latitude must be between -90, 90']
        assert e.value.args[0]['coordinates'][0][0][1][0] == ['Longitude must be between -180, 180']
