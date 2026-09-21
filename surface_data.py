"""Locate NOAA full ISD/ISHD files using a WBAN code and year."""

import gzip
import re
from pathlib import Path

import requests

from file_download import download_file


ISD_BASE_URL = (
    "https://www.ncei.noaa.gov/pub/data/noaa"
)


def load_isd_filenames(year):
    """Return every full ISD filename listed for one year."""
    year = str(year)
    year_url = f"{ISD_BASE_URL}/{year}/"

    response = requests.get(
        year_url,
        timeout=30,
    )
    response.raise_for_status()

    file_pattern = re.compile(
        r'href="([^"]+\.gz)"'
    )

    return file_pattern.findall(
        response.text
    )


def find_isd_file(
    wban,
    year,
    available_filenames=None,
):
    """Return the full ISD filename and URL for one WBAN and year."""
    wban = str(wban).zfill(5)
    year = str(year)

    if available_filenames is None:
        available_filenames = (
            load_isd_filenames(year)
        )

    expected_ending = f"-{wban}-{year}.gz"

    matches = [
        filename
        for filename in available_filenames
        if filename.endswith(expected_ending)
    ]

    if not matches:
        raise FileNotFoundError(
            f"No full ISD file found for "
            f"WBAN {wban} in {year}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"More than one full ISD file found for "
            f"WBAN {wban} in {year}"
        )

    filename = matches[0]
    file_url = (
        f"{ISD_BASE_URL}/"
        f"{year}/"
        f"{filename}"
    )

    return filename, file_url


def validate_isd_download(file_path):
    """Confirm that a downloaded ISD file is a usable gzip file."""
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Downloaded file does not exist: {file_path}"
        )

    if file_path.stat().st_size == 0:
        raise ValueError(
            f"Downloaded file is empty: {file_path.name}"
        )

    try:
        with gzip.open(
            file_path,
            mode="rb",
        ) as compressed_file:
            uncompressed_data = compressed_file.read()

    except (
        gzip.BadGzipFile,
        EOFError,
        OSError,
    ) as error:
        raise ValueError(
            f"Downloaded file is not a valid gzip file: "
            f"{file_path.name}"
        ) from error

    if not uncompressed_data:
        raise ValueError(
            f"Downloaded file contains no data: "
            f"{file_path.name}"
        )

    return file_path


def validate_isd_contents(
    file_path,
    usaf,
    wban,
    year,
):
    """Confirm that an extracted file contains the expected full ISD data."""
    file_path = Path(file_path)

    with file_path.open(
        mode="r",
        encoding="ascii",
    ) as isd_file:
        first_record = (
            isd_file.readline()
            .rstrip("\r\n")
        )

    try:
        variable_character_count = int(
            first_record[0:4]
        )
    except ValueError as error:
        raise ValueError(
            f"Prepared surface file is not in full ISD format: "
            f"{file_path.name}"
        ) from error

    expected_record_length = (
        105 + variable_character_count
    )

    if len(first_record) != expected_record_length:
        raise ValueError(
            f"Prepared surface file is not in full ISD format: "
            f"{file_path.name}"
        )

    found_usaf = first_record[4:10]
    found_wban = first_record[10:15]
    found_year = first_record[15:19]

    expected_usaf = str(usaf).strip()
    expected_wban = str(wban).zfill(5)
    expected_year = str(year)

    if (
        found_usaf != expected_usaf
        or found_wban != expected_wban
        or found_year != expected_year
    ):
        raise ValueError(
            f"Prepared surface file does not match "
            f"USAF {expected_usaf}, WBAN {expected_wban}, "
            f"and year {expected_year}: {file_path.name}"
        )

    return file_path


def download_isd_file(
    file_url,
    destination_directory,
):
    """Download a full ISD file and return its saved path."""
    return download_file(
        file_url,
        destination_directory,
    )


if __name__ == "__main__":
    filename, file_url = find_isd_file(
        wban="24037",
        year=2024,
    )
    download_directory = (
        Path(__file__).parent
        / "downloads"
    )

    downloaded_path = download_isd_file(
        file_url,
        download_directory,
    )

    validated_path = validate_isd_download(
        downloaded_path
    )

    print(f"Filename: {filename}")
    print(f"URL: {file_url}")
    print(f"Downloaded to: {downloaded_path}")
    print(f"Validated: {validated_path.name}")
