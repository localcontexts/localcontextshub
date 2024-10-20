from django.test import TestCase

from communities.models import Boundary


class TestStoringCoordinatesAsGeoJson(TestCase):
    def setUp(self):
        self.expected_geometry = {
            'type': 'MULTIPOLYGON', 'polygons': [
                [(0, 0), (1, 1), (2, 2), (3, 3)],
                [(4, 4), (5, 5), (6, 6), (7, 7)]
            ],
        }
        self.boundary = Boundary(
            geometry=self.expected_geometry
        )
        self.boundary.save()

    def test_coordinates_can_be_saved_as_geo_polygons(self):
        self.assertEqual(self.boundary.geometry, self.expected_geometry)

    def test_non_geo_coordinates_as_tuple(self):
        expected_coordinates = self.expected_geometry['polygons'][0]
        observed_coordinates = self.boundary.get_coordinates()
        self.assertEqual(observed_coordinates, expected_coordinates)

    def test_non_geo_coordinates_as_list(self):
        expected_coordinates = [
            [c[0], c[1]] for c in self.expected_geometry['polygons'][0]
        ]
        observed_coordinates = self.boundary.get_coordinates(as_tuple=False)
        self.assertEqual(observed_coordinates, expected_coordinates)
