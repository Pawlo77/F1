# Elt files are very simmilar
# pylint: disable=R0801

"""
Elt flow for f1db data.
"""

from __future__ import annotations

import os
import sys
from logging import Logger
from typing import TYPE_CHECKING, cast

from prefect import flow
from prefect.logging import get_run_logger

from .fetch import fetch_data_from_f1db
from .scrape import scrape_data_from_f1db
from .upload import upload_data_from_f1db
from .utils import get_output_dir

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import clean_up_output_dir
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import clean_up_output_dir


@flow(
    name="elt_f1db",
    description=(
        "Extract, Load, and Transform f1db data. "
        "First download the data using `fetch_data_from_f1db`,"
        "and then upload the data using `upload_data_from_f1db`"
    ),
    retries=1,
    timeout_seconds=3600,
    retry_delay_seconds=60,
)
def elt() -> None:
    """
    This flow is a placeholder for the ELT process.
    It will first fetch the data from the f1db webpage,
    then upload the data to the database.
    """
    logger = cast(Logger, get_run_logger())

    logger.info("Starting fetching data from f1db...")
    sql_file_path = fetch_data_from_f1db()

    logger.info("Starting scraping data from f1db...")
    extract_dir = scrape_data_from_f1db(sql_file_path)

    logger.info("Starting uploading data to database...")
    upload_data_from_f1db(extract_dir)

    clean_up_output_dir(output_dir=get_output_dir(), logger=logger)


if __name__ == "__main__":
    elt()
