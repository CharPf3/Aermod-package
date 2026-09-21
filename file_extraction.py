"""Extract downloaded gzip and ZIP archives without changing their data."""

import gzip
from pathlib import Path
import shutil
from zipfile import ZipFile


def extract_archive(
    archive_path,
    output_path,
):
    """Extract one gzip or single-file ZIP archive."""
    archive_path = Path(archive_path)
    output_path = Path(output_path)

    if not archive_path.is_file():
        raise FileNotFoundError(
            f"Archive does not exist: {archive_path}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if archive_path.suffix.lower() == ".gz":
        with gzip.open(archive_path, "rb") as source:
            with output_path.open("wb") as destination:
                shutil.copyfileobj(
                    source,
                    destination,
                )

    elif archive_path.suffix.lower() == ".zip":
        with ZipFile(archive_path) as archive:
            files = [
                member
                for member in archive.infolist()
                if not member.is_dir()
            ]

            if len(files) != 1:
                raise ValueError(
                    "ZIP archive must contain exactly one file"
                )

            with archive.open(files[0]) as source:
                with output_path.open("wb") as destination:
                    shutil.copyfileobj(
                        source,
                        destination,
                    )

    else:
        raise ValueError(
            "Archive must end in .gz or .zip"
        )

    if output_path.stat().st_size == 0:
        raise ValueError(
            f"Extracted file is empty: {output_path.name}"
        )

    return output_path
