"""Tests for extracting downloaded data archives."""

import gzip
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from file_extraction import extract_archive
from surface_data import validate_isd_contents
from upper_air_data import validate_upper_air_contents


class FileExtractionTests(unittest.TestCase):
    def test_extracts_gzip_file(self):
        expected_data = b"first surface record\n"

        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            archive_path = directory / "surface.txt.gz"
            output_path = directory / "surface.txt"

            with gzip.open(archive_path, "wb") as archive:
                archive.write(expected_data)

            extracted_path = extract_archive(
                archive_path,
                output_path,
            )

            self.assertEqual(
                extracted_path.read_bytes(),
                expected_data,
            )

    def test_extracts_single_file_zip(self):
        expected_data = b"#USM00072251 upper-air record\n"

        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            archive_path = directory / "upper-air.zip"
            output_path = directory / "upper-air.txt"

            with ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "station-data.txt",
                    expected_data,
                )

            extracted_path = extract_archive(
                archive_path,
                output_path,
            )

            self.assertEqual(
                extracted_path.read_bytes(),
                expected_data,
            )

    def test_rejects_zip_with_multiple_files(self):
        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            archive_path = directory / "multiple-files.zip"

            with ZipFile(archive_path, "w") as archive:
                archive.writestr("first.txt", "first")
                archive.writestr("second.txt", "second")

            with self.assertRaises(ValueError):
                extract_archive(
                    archive_path,
                    directory / "output.txt",
                )

    def test_rejects_unsupported_file_type(self):
        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            archive_path = directory / "terrain.tiff"
            archive_path.write_bytes(b"terrain")

            with self.assertRaises(ValueError):
                extract_archive(
                    archive_path,
                    directory / "output.tiff",
                )


class DataContentValidationTests(unittest.TestCase):
    def test_validates_full_isd_station_and_year(self):
        with TemporaryDirectory() as temporary_directory:
            file_path = (
                Path(temporary_directory)
                / "surface.txt"
            )
            first_record = (
                "0000"
                "722510"
                "12924"
                "20240101"
                "0000"
            )
            first_record += "X" * (
                105 - len(first_record)
            )
            file_path.write_text(
                first_record + "\n",
                encoding="ascii",
            )

            validated_path = validate_isd_contents(
                file_path,
                usaf="722510",
                wban="12924",
                year=2024,
            )

            self.assertEqual(
                validated_path,
                file_path,
            )

    def test_rejects_isd_lite_data(self):
        with TemporaryDirectory() as temporary_directory:
            file_path = (
                Path(temporary_directory)
                / "surface.txt"
            )
            file_path.write_text(
                "2024 01 01 00 211 167 10166\n",
                encoding="ascii",
            )

            with self.assertRaises(ValueError):
                validate_isd_contents(
                    file_path,
                    usaf="722510",
                    wban="12924",
                    year=2024,
                )

    def test_validates_igra_station_and_year(self):
        with TemporaryDirectory() as temporary_directory:
            file_path = (
                Path(temporary_directory)
                / "upper-air.txt"
            )
            file_path.write_text(
                "#USM00072251 2023 12 31 12\n"
                "#USM00072251 2024 01 01 00\n",
                encoding="ascii",
            )

            validated_path = (
                validate_upper_air_contents(
                    file_path,
                    igra_id="USM00072251",
                    year=2024,
                )
            )

            self.assertEqual(
                validated_path,
                file_path,
            )

    def test_rejects_igra_file_without_requested_year(self):
        with TemporaryDirectory() as temporary_directory:
            file_path = (
                Path(temporary_directory)
                / "upper-air.txt"
            )
            file_path.write_text(
                "#USM00072251 2023 12 31 12\n",
                encoding="ascii",
            )

            with self.assertRaises(ValueError):
                validate_upper_air_contents(
                    file_path,
                    igra_id="USM00072251",
                    year=2024,
                )


if __name__ == "__main__":
    unittest.main()
