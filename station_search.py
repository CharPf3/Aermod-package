"""Load surface stations and rank them by distance from a facility."""

import csv
from pathlib import Path

from geopy.distance import geodesic


# Resolve the data path relative to this script, not the user's terminal location.
SURFACE_DATA_FILE = (
    Path(__file__).parent
    / "station_data"
    / "surface_stations.csv"
)


def load_surface_stations(file_path):
    """Load surface-station records from a CSV file."""
    with file_path.open(
        mode="r",
        newline="",
        encoding="utf-8",
    ) as station_file:
        return list(csv.DictReader(station_file))


def find_nearest_station(
    facility_coordinates,
    stations,
    station_count,
):
    """Return the requested number of stations ranked by distance."""
    if station_count < 1:
        raise ValueError("station_count must be at least 1")

    ranked_stations = []

    for station in stations:
        station_coordinates = (
            float(station["latitude"]),
            float(station["longitude"]),
        )

        distance_miles = geodesic(
            facility_coordinates,
            station_coordinates,
        ).miles

        ranked_station = station.copy()
        ranked_station["distance_miles"] = distance_miles

        ranked_stations.append(ranked_station)

    ranked_stations.sort(
        key=lambda station: station["distance_miles"]
    )

    return ranked_stations[:station_count]


if __name__ == "__main__":
    # Temporary example; the future CLI will supply these values.
    facility_coordinates = (45.8831, -106.614)
    surface_stations = load_surface_stations(
        SURFACE_DATA_FILE
    )

    nearest_stations = find_nearest_station(
        facility_coordinates,
        surface_stations,
        station_count=2,
    )

    for rank, station in enumerate(
        nearest_stations,
        start=1,
    ):
        print(
            f"{rank}. {station['station_name']}, "
            f"{station['state']}: "
            f"{station['distance_miles']:.1f} miles "
            f"(WBAN {station['wban']})"
        )
