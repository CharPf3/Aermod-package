"""Tests for terrain bounding boxes and downloaded-file checks."""

import unittest

from geopy.distance import geodesic

from terrain_data import (
    create_terrain_bounding_box,
    download_terrain_data,
    inspect_terrain_file,
)


class TerrainBoundingBoxTests(unittest.TestCase):
    def test_colstrip_bounding_box(self):
        facility_coordinates = (45.8831, -106.614)

        west, south, east, north = (
            create_terrain_bounding_box(
                facility_coordinates,
                distance_km=75,
            )
        )

        self.assertAlmostEqual(west, -107.5801, places=4)
        self.assertAlmostEqual(south, 45.2083, places=4)
        self.assertAlmostEqual(east, -105.6479, places=4)
        self.assertAlmostEqual(north, 46.5578, places=4)

    def test_box_extends_75_km_from_facility(self):
        latitude = 45.8831
        longitude = -106.614

        west, south, east, north = (
            create_terrain_bounding_box(
                (latitude, longitude),
                distance_km=75,
            )
        )

        north_south_km = geodesic(
            (south, longitude),
            (north, longitude),
        ).kilometers
        east_west_km = geodesic(
            (latitude, west),
            (latitude, east),
        ).kilometers

        self.assertAlmostEqual(
            north_south_km,
            150,
            delta=0.1,
        )
        self.assertAlmostEqual(
            east_west_km,
            150,
            delta=0.1,
        )

    def test_default_distance_is_75_km(self):
        facility_coordinates = (45.8831, -106.614)

        default_box = create_terrain_bounding_box(
            facility_coordinates
        )
        explicit_box = create_terrain_bounding_box(
            facility_coordinates,
            distance_km=75,
        )

        self.assertEqual(default_box, explicit_box)

    def test_rejects_invalid_values(self):
        invalid_inputs = [
            ((91, -106.614), 75),
            ((45.8831, -181), 75),
            ((45.8831, -106.614), 0),
            ((45.8831, -106.614), -1),
        ]

        for coordinates, distance_km in invalid_inputs:
            with self.subTest(
                coordinates=coordinates,
                distance_km=distance_km,
            ):
                with self.assertRaises(ValueError):
                    create_terrain_bounding_box(
                        coordinates,
                        distance_km,
                    )


class TerrainFileTests(unittest.TestCase):
    def test_rejects_unsupported_resolution(self):
        with self.assertRaises(ValueError):
            download_terrain_data(
                (-107, 45, -106, 46),
                "downloads",
                resolution=20,
            )

    def test_rejects_missing_terrain_file(self):
        with self.assertRaises(FileNotFoundError):
            inspect_terrain_file(
                "file_that_does_not_exist.tif"
            )


if __name__ == "__main__":
    unittest.main()
