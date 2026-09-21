"""Download remote files without loading them entirely into memory."""

from pathlib import Path

import requests


def download_file(
    file_url,
    destination_directory,
    chunk_size=1024 * 1024,
):
    """Download a file in chunks and return its saved path."""
    destination_directory = Path(
        destination_directory
    )

    destination_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = file_url.rsplit("/", 1)[-1]

    destination_path = (
        destination_directory
        / filename
    )

    with requests.get(
        file_url,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()

        with destination_path.open(
            mode="wb"
        ) as downloaded_file:

            for chunk in response.iter_content(
                chunk_size=chunk_size
            ):
                if chunk:
                    downloaded_file.write(chunk)

    return destination_path
