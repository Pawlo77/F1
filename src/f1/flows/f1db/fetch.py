# Fetch files are very simmilar
# pylint: disable=duplicate-code

"""
Prefect task to fetch circuits data from the A-to-Z circuits page.
"""

from __future__ import annotations

import os
import zipfile
from logging import Logger
from typing import Any, Dict, cast
from urllib.parse import urljoin

import requests
from prefect import task
from prefect.logging import get_run_logger
from prefect.variables import Variable

from .utils import get_output_dir

HEADERS: dict[str, str] = {
    "Accept": "application/vnd.github.v3+json",
}


def _download_release_info(url: str, logger: Logger | None = None) -> Dict[str, Any]:
    """
    Download the release info from the given URL.

    Args:
        url (str): The URL to download the release info from.
        logger (Logger, optional): Logger for logging messages.

    Returns:
        Dict[str, Any]: The release info as a dictionary.
    """
    if logger:
        logger.debug("Fetching release info from %s...", url)

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return cast(Dict[str, Any], response.json())


def _fetch_zip_file(
    base_url: str,
    tag_name: str,
    zip_filename: str,
    target_file_path: str,
    logger: Logger | None = None,
) -> None:
    """
    Download the CSV ZIP file from the given URL.

    Args:
        base_url (str): The base URL for the F1DB repository.
        tag_name (str): The tag name of the release.
        zip_filename (str): The name of the CSV ZIP file.
        target_file_path (str): The path to save the downloaded file.
        logger (Logger, optional): Logger for logging messages.
    """
    url = urljoin(
        base_url,
        f"{tag_name}/{zip_filename}",
    )
    if logger:
        logger.debug("Downloading %s...", url)

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    with open(target_file_path, "wb") as f:
        f.write(response.content)
    if logger:
        logger.info("Saved ZIP file as %s", target_file_path)


@task
def fetch_data_from_f1db() -> str:
    """
    Fetch newest version of the F1DB data.

    Returns:
        str: The path sql file containing the data.
    """
    logger = cast(Logger, get_run_logger())
    output_dir = get_output_dir()

    logger.info("Fetching release info...")
    api_url = str(
        Variable.get(
            "f1db_api_url",
            default="https://api.github.com/repos/f1db/f1db/releases/latest",
        )
    )
    release_info = _download_release_info(api_url, logger=logger)
    tag_name = release_info.get("tag_name")
    if not tag_name:
        raise ValueError("No tag name found in the release info.")

    logger.info("Downloading release %s...", tag_name)
    zip_filename = str(
        Variable.get(
            "f1db-csv-zip-filename", default="f1db-sql-sqlite-single-inserts.zip"
        )
    )
    target_file_path = os.path.join(output_dir, zip_filename)
    base_url = str(
        Variable.get(
            "f1db_base_url", default="https://github.com/f1db/f1db/releases/download/"
        )
    )
    _fetch_zip_file(
        base_url,
        tag_name,
        zip_filename,
        target_file_path,
        logger=logger,
    )

    logger.info("Extracting files...")
    with zipfile.ZipFile(target_file_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    return os.path.join(output_dir, "f1db-sql-sqlite-single-inserts.sql")


if __name__ == "__main__":
    fetch_data_from_f1db()
