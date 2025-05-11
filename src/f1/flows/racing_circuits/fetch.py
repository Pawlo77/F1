# Fetch files are very simmilar
# pylint: disable=R0801

"""
Prefect task to fetch circuits data from the A-to-Z circuits page.
"""

from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from logging import Logger
from typing import Any, Tuple, cast
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from prefect import task
from prefect.logging import get_run_logger

from .utils import get_base_url, get_circuit_dir, get_output_dir


def _sanitize_filename(name: str) -> str:
    """
    Sanitize a file name by removing illegal characters.

    Args:
        name (str): The name to sanitize.

    Returns:
        A sanitized file name.
    """
    return re.sub(r'[\\/*?:"<>|]', "", name)


def _get_circuit_file_path(name: str) -> str:
    """
    Generate a valid file path for a circuit HTML file.

    Args:
        name (str): The name of the circuit.

    Returns:
        str: The file path for the circuit HTML file.
    """
    filename = _sanitize_filename(name) or "unnamed_circuit"
    return os.path.join(get_circuit_dir(), f"{filename}.html")


def _fetch_circuit_links(
    base_url: str, a_to_z_url: str, logger: Logger | None = None
) -> pd.DataFrame:
    """
    Fetch circuit links from the A-to-Z circuits page.

    Args:
        base_url (str): The base URL for the circuits website.
        a_to_z_url (str): The URL of the A-to-Z circuits page.
        logger (Logger, optional): Logger for logging messages.

    Returns:
        pd.DataFrame: A DataFrame containing circuit names and their corresponding URLs.
    """
    response = requests.get(a_to_z_url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    meta = []
    az_divs = soup.find_all("div", class_="az-section")
    for az_div in az_divs:
        az_div = cast(Tag, az_div)
        for link in az_div.find_all("a", href=True):
            tag = cast(Tag, link)
            href = str(tag["href"])
            if href.count("/") < 2:  # pylint: disable=magic-value-comparison
                continue

            full_url = urljoin(base_url, href)
            circuit_name = link.text.strip()
            meta.append((circuit_name, full_url))

    # Remove duplicate entries
    meta = list(set(meta))

    if logger:
        logger.info("Found %d circuits", len(meta))
    return pd.DataFrame(meta, columns=["Circuit Name", "URL"])


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


def _fetch_individual_circuit(row: Tuple[str, str], *args: Any, **kwargs: Any) -> None:
    """
    Helper function to fetch and save individual circuit HTML pages.

    Args:
        row (Tuple[str, str]): A tuple containing the file path and URL.
        *args: Additional arguments.
        **kwargs: Additional keyword arguments.
    """
    file_path, url = row
    # Use the _fetch_html task to download the page
    _fetch_html(file_path, url, *args, **kwargs)


@task
def fetch_data_from_circuits() -> str:
    """
    Fetch data from the A-to-Z circuits page and save individual circuit pages.

    Returns:
        str: The path to the CSV file containing circuit links.
    """
    logger = cast(Logger, get_run_logger())
    base_url = get_base_url()

    # Fetch circuit links from the A-Z page
    a_to_z_url = urljoin(base_url, "/find-a-circuit/a-to-z-circuit-list.html")
    logger.info("Fetching circuit links from %s...", a_to_z_url)
    circuits_meta_df = _fetch_circuit_links(base_url, a_to_z_url, logger=logger)
    circuits_meta_df["file_path"] = circuits_meta_df["Circuit Name"].apply(
        _get_circuit_file_path
    )
    circuits_meta_df_path = os.path.join(get_output_dir(), "circuits_meta.csv")
    circuits_meta_df.to_csv(circuits_meta_df_path, index=False, encoding="utf-8")
    logger.info("Saved circuit links CSV to %s", circuits_meta_df_path)

    # Fetch individual circuit pages concurrently
    logger.info("Fetching individual circuit pages...")
    rows = circuits_meta_df[["file_path", "URL"]].values
    with ThreadPoolExecutor() as executor:
        executor.map(partial(_fetch_individual_circuit, logger=logger), rows)
    logger.info("Completed fetching individual circuit pages (%d)", len(rows))

    return circuits_meta_df_path


if __name__ == "__main__":
    fetch_data_from_circuits()
