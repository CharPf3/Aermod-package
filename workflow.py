"""Coordinate weather-station and terrain downloads for one site."""

from pathlib import Path

from station_search import (
    SURFACE_DATA_FILE,
    find_nearest_station,
    load_surface_stations,
)
from surface_data import (
    download_isd_file,
    find_isd_file,
    load_isd_filenames,
    validate_isd_contents,
    validate_isd_download,
)
from upper_air_data import (
    UPPER_AIR_STATION_FILE,
    load_upper_air_stations,
    build_upper_air_file,
    validate_upper_air_contents,
    validate_upper_air_download,
)
from terrain_data import (
    create_terrain_bounding_box,
    download_terrain_data,
    inspect_terrain_file,
)


from file_download import download_file

from file_extraction import extract_archive


# Surface-data selection and download
def select_available_surface_stations(
    facility_coordinates,
    stations,
    year,
    station_count,
):
    """Select the nearest stations with files for the requested year."""
    if station_count < 1:
        raise ValueError(
            "station_count must be at least 1"
        )

    ranked_stations = find_nearest_station(
        facility_coordinates,
        stations,
        station_count=len(stations),
    )

    available_filenames = (
        load_isd_filenames(year)
    )

    selected_stations = []
    skipped_stations = []

    for station in ranked_stations:
        try:
            filename, file_url = (
                find_isd_file(
                    station["wban"],
                    year,
                    available_filenames,
                )
            )

        except FileNotFoundError:
            skipped_stations.append(station)
            continue

        selected_station = station.copy()

        selected_station["rank"] = (
            len(selected_stations) + 1
        )
        selected_station["usaf"] = (
            filename.split("-", 1)[0]
        )
        selected_station["filename"] = filename
        selected_station["file_url"] = file_url

        selected_stations.append(
            selected_station
        )

        if len(selected_stations) == station_count:
            break

    if len(selected_stations) < station_count:
        raise ValueError(
            f"Only {len(selected_stations)} stations "
            f"with data were found for {year}"
        )

    return selected_stations, skipped_stations


def download_selected_surface_stations(
    selected_stations,
    destination_directory,
):
    """Download and validate every selected surface station."""
    downloaded_stations = []

    for station in selected_stations:
        downloaded_path = (
            download_isd_file(
                station["file_url"],
                destination_directory,
            )
        )

        validate_isd_download(
            downloaded_path
        )

        downloaded_station = station.copy()
        downloaded_station["downloaded_path"] = (
            downloaded_path
        )

        downloaded_stations.append(
            downloaded_station
        )

    return downloaded_stations


def download_selected_upper_air_stations(
    selected_stations,
    destination_directory,
):
    """Download and validate selected upper-air archives."""
    downloaded_stations = []

    for rank, station in enumerate(
        selected_stations,
        start=1,
    ):
        filename, file_url = (
            build_upper_air_file(
                station["igra_id"]
            )
        )

        downloaded_path = download_file(
            file_url,
            destination_directory,
        )

        validate_upper_air_download(
            downloaded_path
        )

        downloaded_station = station.copy()
        downloaded_station["rank"] = rank
        downloaded_station["filename"] = filename
        downloaded_station["file_url"] = file_url
        downloaded_station["downloaded_path"] = (
            downloaded_path
        )

        downloaded_stations.append(
            downloaded_station
        )

    return downloaded_stations

def format_station_name(station_name):
    """Create a short station name for a filename."""
    short_name = station_name.split("/")[0]
    short_name = short_name.split(";")[0]

    return "".join(
        character
        for character in short_name.title()
        if character.isalnum()
    )

def prepare_station_files(
    downloaded_stations,
    destination_directory,
    year,
    station_code_key,
):
    """Extract station archives and give them readable names."""
    destination_directory = Path(
        destination_directory
    )
    prepared_stations = []

    for station in downloaded_stations:
        station_name = format_station_name(
            station["station_name"]
        )
        station_code = station[
            station_code_key
        ]

        prepared_filename = (
            f"{station['rank']:02d}_"
            f"{station_code}_"
            f"{station_name}_"
            f"{year}.txt"
        )

        prepared_path = extract_archive(
            station["downloaded_path"],
            destination_directory
            / prepared_filename,
        )
        prepared_station = station.copy()
        prepared_station["prepared_filename"] = (
            prepared_filename
        )
        prepared_station["prepared_path"] = (
            prepared_path
        )

        prepared_stations.append(
            prepared_station
        )

    return prepared_stations


def download_site_terrain(
    facility_coordinates,
    destination_directory,
    distance_km=75,
):
    """Download and inspect terrain surrounding one facility."""
    bounding_box = create_terrain_bounding_box(
        facility_coordinates,
        distance_km,
    )

    terrain_files = download_terrain_data(
        bounding_box,
        destination_directory,
        resolution=10,
    )

    terrain_file_details = []

    for terrain_file in terrain_files:
        file_details = inspect_terrain_file(
            terrain_file
        )
        terrain_file_details.append(
            file_details
        )

    return bounding_box, terrain_file_details


if __name__ == "__main__":
    # Shared temporary inputs
    facility_coordinates = (
        27.77,
        -97.50,
    )
    year = 2024
    surface_station_count = 2
    upper_air_station_count = 1
    # Use 5 km while testing; the intended full distance is 75 km.
    terrain_distance_km = 5

    # Load the source-specific station inventories.
    surface_stations = load_surface_stations(
        SURFACE_DATA_FILE
    )

    upper_air_stations = load_upper_air_stations(
        UPPER_AIR_STATION_FILE,
        year,
    )

    # Both station types use the same distance-ranking function.
    nearest_upper_air_stations = (
        find_nearest_station(
            facility_coordinates,
            upper_air_stations,
            station_count=upper_air_station_count,
        )
    )

    # Surface selection also verifies that files exist for the year.
    selected_stations, skipped_stations = (
        select_available_surface_stations(
            facility_coordinates,
            surface_stations,
            year,
            surface_station_count,
        )
    )

    # This raw download folder will later become the site output folder.
    download_directory = (
        Path(__file__).parent
        / "downloads"
    )

    aermet_directory = (
        download_directory
        / "AERMET"
    )

    terrain_directory = (
        download_directory
        / "terrain"
    )

    downloaded_upper_air_stations = (
        download_selected_upper_air_stations(
            nearest_upper_air_stations,
            download_directory,
        )
    )

    downloaded_surface_stations = (
        download_selected_surface_stations(
            selected_stations,
            download_directory,
        )
    )

    prepared_surface_stations = (
        prepare_station_files(
            downloaded_surface_stations,
            aermet_directory,
            year,
            station_code_key="wban",
        )
    )

    prepared_upper_air_stations = (
        prepare_station_files(
            downloaded_upper_air_stations,
            aermet_directory,
            year,
            station_code_key="igra_id",
        )
    )

    for station in prepared_surface_stations:
        validate_isd_contents(
            station["prepared_path"],
            station["usaf"],
            station["wban"],
            year,
        )

    for station in prepared_upper_air_stations:
        validate_upper_air_contents(
            station["prepared_path"],
            station["igra_id"],
            year,
        )

    terrain_bounding_box, terrain_file_details = (
        download_site_terrain(
            facility_coordinates,
            terrain_directory,
            distance_km=terrain_distance_km,
        )
    )


    print("\nSurface stations:")

    for station in skipped_stations:
        print(
            f"Skipped {station['station_name']}, "
            f"{station['state']}: "
            f"no full ISD file for {year}"
        )

    for station in prepared_surface_stations:
        print(
            f"{station['rank']}. "
            f"{station['station_name']}, "
            f"{station['state']}: "
            f"{station['distance_miles']:.1f} miles"
        )
        print(
            f"   File: {station['filename']}"
        )
        print(
            f"   Prepared: "
            f"{station['prepared_filename']}"
        )
        print(
            f"   Prepared path: "
            f"{station['prepared_path']}"
        )


    print("\nUpper-air stations:")

    for station in prepared_upper_air_stations:
        print(
            f"{station['rank']}. "
            f"{station['station_name']}: "
            f"{station['distance_miles']:.1f} miles "
            f"({station['igra_id']})"
        )
        print(
            f"   File: {station['filename']}"
        )
        print(
            f"   Downloaded: "
            f"{station['downloaded_path']}"
        )
        print(
            f"   Prepared: "
            f"{station['prepared_filename']}"
        )
        print(
            f"   Prepared path: "
            f"{station['prepared_path']}"
        )



    print("\nTerrain:")
    print(
        "Requested bounds "
        "(west, south, east, north):"
    )

    print(terrain_bounding_box)

    for file_details in terrain_file_details:
        print(
            f"File: "
            f"{file_details['file_path'].name}"
        )
        print(
            f"Saved: "
            f"{file_details['file_path']}"
        )
        print(
            f"CRS: "
            f"{file_details['crs']}"
        )
        print(
            f"Size: "
            f"{file_details['width']} x "
            f"{file_details['height']} pixels"
        )
        print(
            f"Compression: "
            f"{file_details['compression']}"
        )
