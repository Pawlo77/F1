"""
Elt flow for racing circuits data.
"""

from __future__ import annotations

from logging import Logger
from typing import cast

from prefect import flow
from prefect.logging import get_run_logger

from .fetch import fetch_data_from_circuits
from .scrape import scrape_data_from_circuits
from .upload import upload_data_from_circuits


@flow(
    name="elt_circuits",
    description=(
        "Extract, Load, and Transform circuits data. "
        "First download the data using `fetch_data_from_circuits`,"
        "scrape the data using `scrape_data_from_circuits`, "
        "and then finally upload the data using `upload_data_from_circuits`"
    ),
    retries=1,
    timeout_seconds=300,
)
def elt() -> None:
    """
    This flow is a placeholder for the ELT process.
    It will first fetch the data from the circuits webpage,
    then scrape the data from the saved HTML files and
    finally upload the data to the database.
    """
    logger = cast(Logger, get_run_logger())

    logger.info("Starting fetching data from circuits...")
    circuits_meta_df_path = fetch_data_from_circuits()

    logger.info("Starting scraping data from circuits...")
    circuits_df_path = scrape_data_from_circuits(circuits_meta_df_path)

    logger.info("Starting uploading data to database...")
    upload_data_from_circuits(circuits_df_path)


if __name__ == "__main__":
    elt()
