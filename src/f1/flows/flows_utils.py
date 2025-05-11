"""
Utility functions for the F1 project.

Requires MsSQL Server ODBC Driver 18.
For macOS, install the driver using:
- https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/
  install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15
"""

from __future__ import annotations

import hashlib
import os
import shutil
import threading
from logging import Logger
from queue import Empty, Queue
from time import sleep
from typing import Any, List, cast

import numpy as np
import pandas as pd
from prefect.variables import Variable
from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy import (
    Column,
    Connection,
    DateTime,
    String,
    inspect,
    text,
)
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# pylint: disable=too-few-public-methods
class DWHMixin:
    """Mixin class for DWH-related columns."""

    dwh_hash = Column(
        String(96), index=True, nullable=False, comment="Hash of the data"
    )
    dwh_valid_from = Column(
        DateTime, index=True, nullable=False, comment="Creation timestamp"
    )
    dwh_modified_at = Column(
        DateTime, index=True, nullable=False, comment="Modification timestamp"
    )
    dwh_valid_to = Column(
        DateTime, index=True, nullable=True, comment="Deletion timestamp"
    )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @classmethod
    def upsert(
        cls,
        pk_keys: List[str],
        session: Session,
        data_row: "pd.Series[Any]",
        commit_: bool = False,
        logger: Logger | None = None,
    ) -> bool:
        """
        Upsert a row into the Attendance table by automatically
        detecting the model and primary keys.

        Args:
            pk_keys (List[str]): List of primary key column names.
            session (Session): The SQLAlchemy session to use.
            data_row (pd.Series): The row to upsert.
            commit_ (bool): Whether to commit the session after the upsert.
            logger (Logger, optional): Logger for logging messages.

        Returns:
            bool: True if a new row was added or updated.
        """
        try:
            pk_values = {col: data_row[col] for col in pk_keys}

            # Retrieve the existing record using primary key values and valid record flag
            existing_obj = session.query(cls).filter_by(**pk_values).first()

            dwh_hash = data_row["dwh_hash"]

            if existing_obj and getattr(existing_obj, "dwh_hash", None) == dwh_hash:
                return False

            if existing_obj and getattr(existing_obj, "dwh_hash", None) != dwh_hash:
                if logger:
                    logger.debug(f"Updating existing record with keys {pk_values}...")

                # Update the existing record
                for k, v in data_row.items():
                    k = str(k)
                    if not k.startswith("dwh_"):
                        setattr(existing_obj, k, v)

                setattr(existing_obj, "dwh_mofified_at", data_row["dwh_valid_from"])
                setattr(existing_obj, "dwh_hash", data_row["dwh_hash"])
            else:
                if logger:
                    logger.debug(f"Adding new record with keys {pk_values}...")
                new_obj = cls(**data_row.to_dict())
                session.add(new_obj)

            if commit_:
                session.commit()
            return True

        except SQLAlchemyError as e:
            session.rollback()

            record_indentifier = "UNKNOWN"
            if "pk_values" in locals():  # pylint: disable=magic-value-comparison
                record_indentifier = str(pk_values)

            raise UploadError(
                f"Error upserting record with keys {record_indentifier}"
            ) from e


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models.
    This class is used to define the base for all SQLAlchemy models in the project.
    """


class ScrapeError(Exception):
    """
    Custom exception for scraping errors.
    """


class UploadError(Exception):
    """Custom exception for upload errors."""


# pylint: disable=too-many-instance-attributes
class _UploadWorker(threading.Thread):
    """Thread worker for uploading data to the database."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        queue: "Queue[pd.Series[Any]]",
        class_obj: DWHMixin,
        pk_keys: List[str],
        logger: Logger | None = None,
        log_every: int = 1000,
    ):
        """
        Initialize the _UploadWorker.

        Args:
            queue ("Queue[pd.Series[Any]]"): The queue to get rows from.
            class_obj (DWHMixin): The SQLAlchemy model class to use for the upload.
            pk_keys (List[str]): List of primary key column names.
            logger (Logger, optional): Logger for logging messages.
            log_every (int): Number of rows to process before logging progress.
        """
        super().__init__()
        self.queue = queue
        self.class_obj = class_obj
        self.pk_keys = pk_keys

        self.logger = logger
        self.log_every = log_every

        self.modified_count = 0
        self.processed_count = 0

        self.name = f"_UploadWorker-{id(self)}"

    def run(self, max_retries: int = 3, retries_delay: int = 5) -> None:
        """
        Run the worker thread to process rows from the queue.

        Args:
            max_retries (int): Maximum number of retries for database operations.
            retries_delay (int): Delay in seconds between retries.
        """

        with load_default_sqlalchemy_connection() as thread_conn:
            with sessionmaker(bind=thread_conn)() as thread_session:
                while True:
                    try:
                        cur_row = self.queue.get(timeout=1)
                    except Empty:
                        # Queue is empty
                        break

                    for take in range(max_retries):
                        try:
                            if self.class_obj.upsert(
                                self.pk_keys,
                                thread_session,
                                cur_row,
                                logger=self.logger,
                            ):
                                self.modified_count += 1
                            thread_session.commit()

                            self.processed_count += 1
                            if (
                                self.logger
                                and self.processed_count % self.log_every == 0
                            ):
                                self.logger.info(
                                    "Row %d processed successfully in %s",
                                    self.processed_count,
                                    self.name,
                                )
                            self.queue.task_done()
                            break

                        except OperationalError as e:
                            # Handle database connection errors
                            if self.logger:
                                self.logger.error(
                                    "Database connection error in %s: %s, take %d",
                                    self.name,
                                    e,
                                    take,
                                )
                            thread_session.rollback()
                            if take == max_retries - 1:
                                raise UploadError(
                                    (
                                        "Max retries reached for row "
                                        f"{self.processed_count} in {self.name}"
                                    )
                                ) from e
                            sleep(retries_delay)

                        except Exception as e:
                            thread_session.rollback()
                            if self.logger:
                                self.logger.error(
                                    "Error processing row in %s: %s", self.name, e
                                )
                            raise UploadError(f"Error in {self.name}") from e


# pylint: disable=too-many-branches,too-many-statements
def upload_data(
    class_obj: DWHMixin,
    df_path: str | None = None,
    df: pd.DataFrame | None = None,
    logger: Logger | None = None,
) -> None:
    """
    Upload scraped data to dwh table.

    Args:
        class_obj (DWHMixin): The SQLAlchemy model class to use for the upload.
        df_path (str, optional): Path to the CSV file containing data.
        df (pd.DataFrame, optional): DataFrame containing data. If provided, df_path is ignored.
        logger (Logger, optional): Logger for logging messages.

    Raises:
        Exception: If there is an error reading the CSV file or during the upload process.
    """
    if df_path is None and df is None:
        raise ValueError("Either df_path or df must be provided.")

    _num_workers = Variable.get("num_workers", default=32)
    try:
        num_workers = int(_num_workers)  # type: ignore
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"Invalid value for num_workers: {_num_workers}. Must be an integer."
        ) from e

    if df_path is not None:
        # Read the CSV file into a DataFrame and create a unique ID for each row
        if logger:
            logger.info("Reading CSV file: %s...", df_path)
        try:
            df = pd.read_csv(df_path)
        except Exception as e:
            raise UploadError(f"Error reading CSV file: {df_path}") from e

    if df is None:
        raise ValueError("DataFrame is None. Please provide a valid DataFrame.")
    if df.empty:
        if logger:
            logger.warning("DataFrame is empty. No data to upload.")
        return

    # Add metadata columns
    if logger:
        logger.info("Adding metadata columns...")
    try:
        df["dwh_hash"] = df.apply(
            lambda row: hashlib.sha384(
                "|".join(str(value) for value in row.values).encode("utf-8")
            ).hexdigest(),
            axis=1,
        )
        df["dwh_valid_from"] = df["dwh_modified_at"] = pd.to_datetime("now")
        df = df.replace({np.nan: None})
    except Exception as e:
        raise UploadError("Error adding metadata columns") from e

    mapper = inspect(class_obj)
    if mapper is None:
        raise ValueError("No mapper found for the provided class object.")

    if logger:
        logger.info("Starting data upload process...")

    work_queue: "Queue[pd.Series[Any]]" = Queue()
    for _, cur_row in df.iterrows():
        work_queue.put(cur_row)
    total_rows = work_queue.qsize()

    # with load_default_sqlalchemy_connection() as conn:
    #     class_obj.__table__.drop(bind=conn, checkfirst=True)
    #     class_obj.__table__.create(bind=conn, checkfirst=True)

    i = modified = 0
    try:
        workers = []
        for _ in range(num_workers):
            worker = _UploadWorker(
                queue=work_queue,
                class_obj=class_obj,
                pk_keys=[col.name for col in mapper.primary_key],
                logger=logger,
            )
            worker.start()
            workers.append(worker)

        while not work_queue.empty():
            for worker in workers:
                if not worker.is_alive():
                    raise UploadError(f"Worker {worker.name} has stopped unexpectedly.")
            sleep(1.0)

        modified = sum(worker.modified_count for worker in workers)
        i = total_rows

    except Exception as e:
        raise UploadError(f"Error during data upload process, in {i}th row") from e

    if logger:
        logger.info(
            "Data upload process completed. %d rows processed, %d modified.",
            i,
            modified,
        )


def load_default_connector() -> SqlAlchemyConnector:
    """
    Load the default SQLAlchemy connector for the F1 project.

    Returns:
        SqlAlchemyConnector: The default SQLAlchemy connector.
    """
    return SqlAlchemyConnector.load("f1-mssql-azure")


def load_default_sqlalchemy_connection() -> Connection:
    """
    Load the default SQLAlchemy connection for the F1 project.

    Returns:
        Connection: The default SQLAlchemy connection.
    """
    return cast(Connection, load_default_connector().get_connection())


def clean_up_output_dir(output_dir: str, logger: Logger | None = None) -> None:
    """
    Clean up the output directory by removing all files and subdirectories.

    Args:
        output_dir (str): The path to the output directory to clean up.
        logger (Logger, optional): Logger for logging messages.
    """
    if os.path.exists(output_dir):
        if os.path.isfile(output_dir):
            os.remove(output_dir)
        elif os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
    elif logger:
        logger.warning("The specified output path does not exist: %s", output_dir)


if __name__ == "__main__":
    # Test the connection
    with load_default_sqlalchemy_connection() as conn:
        result = conn.execute(text("SELECT @@version;")).fetchall()
        for row in result:
            print(row)
