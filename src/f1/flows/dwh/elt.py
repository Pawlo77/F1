# Elt files are very simmilar
# pylint: disable=duplicate-code

"""
Elt flow for dwh.
"""

from __future__ import annotations

import os
import sys
from logging import Logger
from typing import TYPE_CHECKING, cast

from prefect import flow
from prefect.logging import get_run_logger
from sqlalchemy import text

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import load_default_sqlalchemy_connection
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import load_default_sqlalchemy_connection


@flow(
    name="elt_dwh",
    description=(
        "Extract, Load, and Transform f1db data for the data warehouse (DWH). "
    ),
    retries=1,
    timeout_seconds=3600,
    retry_delay_seconds=60,
)
def elt() -> None:
    """
    This flow is a placeholder for the ELT process.
    It calls the stored procedure [dwh].[etl] to perform the ETL process.
    """
    logger = cast(Logger, get_run_logger())

    logger.info("Starting etl...")
    with load_default_sqlalchemy_connection() as connection:
        result = connection.execute(text("EXEC [dwh].[etl]"))
        for row in result:
            logger.info("dwh.etl result: %s", row)


if __name__ == "__main__":
    elt()
