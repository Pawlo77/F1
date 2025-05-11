# Upload files are very simmilar
# pylint: disable=R0801

"""
Prefect task to upload f1dv data to the database.
"""

from __future__ import annotations

import os
import sys
from logging import Logger
from typing import TYPE_CHECKING, cast

import pandas as pd
from prefect import task
from prefect.logging import get_run_logger

from .models import TABLES_MAP  # type: ignore[attr-defined]
from .utils import (
    get_output_dir,
)

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import DWHMixin, UploadError, upload_data
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import DWHMixin, UploadError, upload_data


@task
def _upload_data_from_f1db(
    df: pd.DataFrame,
    table_class: DWHMixin,
    logger: Logger | None = None,
) -> None:
    """
    Upload f1dv data to dwh table.

    Args:
        df (pd.DataFrame): DataFrame containing data to be uploaded.
        table_class (DWHMixin): Class of the table to which data will be uploaded.
        logger (Logger, optional): Logger instance for logging. Defaults to None.

    Raises:
        Exception: If there is an error reading the CSV file or during the upload process.
    """
    upload_data(
        df=df,
        class_obj=table_class,
        logger=logger,
    )


# pylint: disable=too-many-locals
@task
def upload_data_from_f1db(dir_path: str) -> None:
    """
    Upload scraped data to dwh table.

    Args:
        dir_path (str): Path to the directory containing data files.

    Raises:
        Exception: If there is an error reading the CSV file or during the upload process.
    """
    logger = cast(Logger, get_run_logger())

    # TODO: make data a dict # pylint: disable=fixme
    data = []

    logger.info("Parsing data...")
    for filename in os.listdir(dir_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(dir_path, filename)
            try:
                na_vals = [
                    "",
                    "#N/A",
                    "#N/A N/A",
                    "#NA",
                    "-1.#IND",
                    "-1.#QNAN",
                    "1.#IND",
                    "1.#QNAN",
                    "NaN",
                    "nan",
                    "NULL",
                    "null",
                ]
                df = pd.read_csv(
                    file_path,
                    low_memory=False,
                    keep_default_na=False,
                    na_values=na_vals,
                )

                if "permanent_number" in df.columns:  # pylint: disable=magic-value-comparison
                    df["permanent_number"] = df["permanent_number"].map(
                        lambda x: str(int(x)) if pd.notna(x) else x
                    )

                splitted = os.path.splitext(filename)[0].split("_")
                table_id = splitted[-1]
                table_name = "_".join(splitted[:-1])
                data.append((table_name, df, table_id, file_path))

            except Exception as e:
                raise UploadError(f"Error parsing data from {file_path}") from e

    data = sorted(data, key=lambda x: (x[0], int(x[2])))
    for table_name, table_class in TABLES_MAP:
        for (
            cur_table_name,
            cur_df,
            cur_table_id,
            cur_file_path,
        ) in data:
            if table_name == cur_table_name:
                logger.info("Uploading data to %s (%s)...", table_name, cur_table_id)
                try:
                    _upload_data_from_f1db(
                        df=cur_df,
                        table_class=table_class,
                        logger=logger,
                    )
                    os.remove(cur_file_path)
                except Exception as e:
                    raise UploadError(f"Error uploading data to {table_name}") from e


if __name__ == "__main__":
    upload_data_from_f1db(
        os.path.join(get_output_dir(), "data"),
    )
