"""Create the geographic area used to request AERMAP terrain data."""

from pathlib import Path

from geopy.distance import geodesic
import rasterio
from seamless_3dep import get_dem


TERRAIN_RESOLUTIONS = (10, 30, 60)


def create_terrain_bounding_box(
    facility_coordinates,
    distance_km=75,
):
    """Return terrain bounds as west, south, east, and north."""
    latitude, longitude = facility_coordinates

    if not -90 <= latitude <= 90:
        raise ValueError("latitude must be between -90 and 90")

    if not -180 <= longitude <= 180:
        raise ValueError("longitude must be between -180 and 180")

    if distance_km <= 0:
        raise ValueError("distance_km must be greater than 0")

    distance = geodesic(kilometers=distance_km)

    # Bearings are measured clockwise: north, east, south, then west.
    north = distance.destination(
        facility_coordinates,
        bearing=0,
    )
    east = distance.destination(
        facility_coordinates,
        bearing=90,
    )
    south = distance.destination(
        facility_coordinates,
        bearing=180,
    )
    west = distance.destination(
        facility_coordinates,
        bearing=270,
    )

    return (
        west.longitude,
        south.latitude,
        east.longitude,
        north.latitude,
    )


def download_terrain_data(
    bounding_box,
    output_directory,
    resolution=10,
):
    """Download 3DEP terrain files that cover a bounding box."""
    if resolution not in TERRAIN_RESOLUTIONS:
        raise ValueError(
            "resolution must be 10, 30, or 60 meters"
        )

    return get_dem(
        bounding_box,
        output_directory,
        res=resolution,
    )


def inspect_terrain_file(file_path):
    """Return useful metadata from a downloaded terrain GeoTIFF."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Terrain file does not exist: {file_path}"
        )

    if file_path.stat().st_size == 0:
        raise ValueError(
            f"Terrain file is empty: {file_path.name}"
        )

    with rasterio.open(file_path) as terrain_file:
        compression = terrain_file.compression

        return {
            "file_path": file_path,
            "driver": terrain_file.driver,
            "crs": str(terrain_file.crs),
            "bounds": tuple(terrain_file.bounds),
            "width": terrain_file.width,
            "height": terrain_file.height,
            "band_count": terrain_file.count,
            "data_type": terrain_file.dtypes[0],
            "compression": (
                compression.value
                if compression is not None
                else "NONE"
            ),
        }


if __name__ == "__main__":
    # Use a small area first so we can inspect one download quickly.
    colstrip_coordinates = (45.8831, -106.614)
    test_distance_km = 5

    bounding_box = create_terrain_bounding_box(
        colstrip_coordinates,
        distance_km=test_distance_km,
    )
    download_directory = (
        Path(__file__).parent
        / "downloads"
        / "terrain_test"
    )
    terrain_files = download_terrain_data(
        bounding_box,
        download_directory,
        resolution=10,
    )

    print("Requested Colstrip terrain bounding box:")
    print("(west, south, east, north)")
    print(bounding_box)

    for terrain_file in terrain_files:
        file_details = inspect_terrain_file(
            terrain_file
        )

        print("\nDownloaded terrain file:")
        print(file_details["file_path"])
        print(f"Driver: {file_details['driver']}")
        print(f"CRS: {file_details['crs']}")
        print(f"Bounds: {file_details['bounds']}")
        print(
            "Size: "
            f"{file_details['width']} x "
            f"{file_details['height']} pixels"
        )
        print(
            f"Bands: {file_details['band_count']}"
        )
        print(
            f"Data type: {file_details['data_type']}"
        )
        print(
            f"Compression: "
            f"{file_details['compression']}"
        )
