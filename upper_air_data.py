"""Load NOAA IGRA upper-air station metadata."""

from pathlib import Path
from zipfile import BadZipFile, ZipFile

UPPER_AIR_STATION_FILE = (
    Path(__file__).parent
    / "station_data"
    / "igra2-station-list.txt"
)

IGRA_DATA_BASE_URL = (
    "https://www.ncei.noaa.gov/data/"
    "integrated-global-radiosonde-archive/"
    "access/data-por"
)


def load_upper_air_stations(
    file_path,
    year,
):
    """Load U.S. IGRA stations whose records include the requested year."""
    year = int(year)
    stations = []

    with file_path.open(
        mode="r",
        encoding="utf-8",
    ) as station_file:

        # IGRA records are fixed-width, so fields use column positions.
        for line in station_file:
            igra_id = line[0:11].strip()

            # The initial package scope is U.S. upper-air stations.
            if not igra_id.startswith("US"):
                continue

            start_year = int(
                line[72:76]
            )
            end_year = int(
                line[77:81]
            )

            # Period-of-record filtering happens before distance ranking.
            if not start_year <= year <= end_year:
                continue

            station = {
                "igra_id": igra_id,
                "latitude": float(
                    line[12:20]
                ),
                "longitude": float(
                    line[21:30]
                ),
                "elevation_m": float(
                    line[31:37]
                ),
                "state": line[38:40].strip(),
                "station_name": (
                    line[41:71].strip()
                ),
                "start_year": start_year,
                "end_year": end_year,
                "observation_count": int(
                    line[82:88]
                ),
            }

            stations.append(station)

    return stations


def build_upper_air_file(igra_id):
    """Return the IGRA archive filename and URL."""
    igra_id = str(igra_id).strip().upper()

    filename = (
        f"{igra_id}-data.txt.zip"
    )

    file_url = (
        f"{IGRA_DATA_BASE_URL}/"
        f"{filename}"
    )

    return filename, file_url


def validate_upper_air_download(file_path):
    """Confirm that a downloaded file is a usable ZIP archive."""
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Downloaded file does not exist: "
            f"{file_path}"
        )

    if file_path.stat().st_size == 0:
        raise ValueError(
            f"Downloaded file is empty: "
            f"{file_path.name}"
        )

    try:
        with ZipFile(file_path) as archive:
            archive_members = archive.namelist()

            if not archive_members:
                raise ValueError(
                    f"ZIP archive contains no files: "
                    f"{file_path.name}"
                )

            damaged_member = archive.testzip()

    except (
        BadZipFile,
        OSError,
    ) as error:
        raise ValueError(
            f"Downloaded file is not a valid ZIP: "
            f"{file_path.name}"
        ) from error

    if damaged_member is not None:
        raise ValueError(
            f"Damaged file inside ZIP: "
            f"{damaged_member}"
        )

    return file_path


def validate_upper_air_contents(
    file_path,
    igra_id,
    year,
):
    """Confirm that extracted IGRA data contain the station and year."""
    file_path = Path(file_path)
    expected_header_start = (
        f"#{str(igra_id).strip().upper()} "
        f"{year} "
    )

    with file_path.open(
        mode="r",
        encoding="ascii",
    ) as upper_air_file:
        for line in upper_air_file:
            if line.startswith(
                expected_header_start
            ):
                return file_path

    raise ValueError(
        f"Prepared upper-air file does not contain "
        f"{igra_id} data for {year}: {file_path.name}"
    )


if __name__ == "__main__":
    # Temporary year; the future workflow will supply it.
    year = 2024

    upper_air_stations = (
        load_upper_air_stations(
            UPPER_AIR_STATION_FILE,
            year,
        )
    )

    print(
        f"Eligible U.S. stations for {year}: "
        f"{len(upper_air_stations)}"
    )

    glasgow = next(
        station
        for station in upper_air_stations
        if station["igra_id"] == "USM00072768"
    )

    print(glasgow)
