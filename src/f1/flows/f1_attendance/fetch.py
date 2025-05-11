# Fetch files are very simmilar
# pylint: disable=R0801

"""
Prefect task to fetch circuits data from the A-to-Z circuits page.
"""

from __future__ import annotations

import os
from logging import Logger
from typing import cast

import requests
from prefect import task
from prefect.logging import get_run_logger

from .utils import get_base_url, get_output_dir


def _fetch_html(file_path: str, url: str, logger: Logger | None = None) -> None:
    """
    Fetch HTML content from a URL and save it to a file.

    Args:
        file_path (str): The path to save the HTML file.
        url (str): The URL to fetch the HTML from.
        logger (Logger, optional): Logger for logging messages.
    """
    if logger:
        logger.debug("Fetching HTML from %s...", url)

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    if logger:
        logger.debug("Saved HTML to %s", file_path)


@task
def fetch_data_from_f1destinations() -> str:
    """
    Fetch data from the F1 Destinations website.

    Returns:
        str: The path to the CSV file containing circuit links.
    """
    logger = cast(Logger, get_run_logger())
    base_url = get_base_url()

    attendance_data_path = os.path.join(get_output_dir(), "attendance.html")
    _fetch_html(attendance_data_path, base_url, logger=logger)
    logger.info("Saved attendance data to %s", attendance_data_path)

    return attendance_data_path


if __name__ == "__main__":
    fetch_data_from_f1destinations()
