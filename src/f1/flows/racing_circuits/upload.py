# Upload files are very simmilar
# pylint: disable=R0801

"""
Prefect task to upload circuits data to the database.
"""

from __future__ import annotations

import os
import sys
from logging import Logger
from typing import TYPE_CHECKING, cast

from prefect import task
from prefect.logging import get_run_logger

from .models import Circuit
from .utils import get_output_dir

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import DWHMixin, upload_data
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import DWHMixin, upload_data


@task
def upload_data_from_circuits(df_path: str) -> None:
    """
    Upload scraped data to dwh table.

    Args:
        df_path (str): Path to the CSV file containing data.

    Raises:
        Exception: If there is an error reading the CSV file or during the upload process.
    """
    logger = cast(Logger, get_run_logger())
    upload_data(df_path=df_path, class_obj=cast(DWHMixin, Circuit), logger=logger)
    os.remove(df_path)


if __name__ == "__main__":
    upload_data_from_circuits(
        os.path.join(get_output_dir(), "circuit_data.csv"),
    )
