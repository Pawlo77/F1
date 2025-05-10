# Upload files are very simmilar
# pylint: disable=R0801

"""
Prefect task to upload circuits data to the database.
"""

from __future__ import annotations

import hashlib
import os
import sys
from logging import Logger
from typing import TYPE_CHECKING, Any, cast

import numpy as np
import pandas as pd
from prefect import task
from prefect.logging import get_run_logger
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from .utils import get_output_dir

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import (
        Base,
        UploadError,
        load_default_sqlalchemy_connection,
    )
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import (
        Base,
        UploadError,
        load_default_sqlalchemy_connection,
    )


class Attendance(Base):
    """Model for the circuits table in the database."""

    __tablename__ = "attendance"
    __table_args__ = ({"schema": "web"},)

    year = Column(Integer, nullable=False, comment="Year of the race")
    race = Column(
        String(255), nullable=False, primary_key=True, comment="Name of the race"
    )
    track = Column(String(255), nullable=False, comment="Name of the track")
    weekend_attendance = Column(
        Integer, nullable=True, comment="Attendance during the race weekend"
    )

    dwh_hash = Column(
        String(96), index=True, nullable=False, comment="Hash of the circuit data"
    )
    dwh_valid_from = Column(
        DateTime, index=True, nullable=False, comment="Creation timestamp"
    )
    dwh_valid_to = Column(
        DateTime,
        index=True,
        nullable=True,
        comment="Modification timestamp",
        default=None,
    )
    dwh_version = Column(
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        comment="Version of the data",
        default=1,
    )

    def __repr__(self) -> str:
        """Return a string representation of the Attendance object."""
        return f"<Circuit(race={self.race}, year={self.year})>"

    @staticmethod
    def upsert(
        session: Session,
        row: "pd.Series[Any]",
        commit_: bool = False,
        logger: Logger | None = None,
    ) -> int:
        """
        Upsert a row into the Attendance table.

        Args:
            session (Session): The SQLAlchemy session to use.
            row (pd.Series): The row to upsert.
            commit_ (bool): Whether to commit the session after the upsert.
            logger (Logger, optional): Logger for logging messages.

        Returns:
            bool: True if the row was upserted.
        """
        try:
            race = row["race"]
            dwh_hash = row["dwh_hash"]

            attendance = Attendance(**row.to_dict())
            existing_attendance = (
                session.query(Attendance)
                .filter_by(race=race, dwh_valid_to=None)
                .first()
            )

            if existing_attendance and existing_attendance.dwh_hash == dwh_hash:
                return False

            if existing_attendance and existing_attendance.dwh_hash != dwh_hash:
                if logger:
                    logger.debug(f"Updating existing attendance: {race}...")
                setattr(existing_attendance, "dwh_valid_from", row["dwh_valid_from"])
                setattr(attendance, "dwh_version", existing_attendance.dwh_version + 1)
            elif logger:
                logger.debug(f"Adding new attendance: {race}...")

            session.add(attendance)

            if commit_:
                session.commit()
            return True

        except SQLAlchemyError as e:
            session.rollback()
            raise UploadError(
                f"Error upserting attendance {row.get('race', 'UNKNOWN')}"
            ) from e


@task
def upload_data_from_f1destinations(attendance_df_path: str) -> None:
    """
    Upload scraped data to dwh table.

    Args:
        attendance_df_path (str): Path to the CSV file containing attendance data.

    Raises:
        Exception: If there is an error reading the CSV file or during the upload process.
    """
    logger = cast(Logger, get_run_logger())

    # Read the CSV file into a DataFrame and create a unique ID for each row
    logger.info("Reading CSV file: %s...", attendance_df_path)
    try:
        attendance_df = pd.read_csv(attendance_df_path)
    except Exception as e:
        raise UploadError(f"Error reading CSV file: {attendance_df_path}") from e

    # Add metadata columns
    logger.info("Adding metadata columns...")
    try:
        attendance_df["dwh_hash"] = attendance_df.apply(
            lambda row: hashlib.sha384(
                "|".join(str(value) for value in row.values).encode("utf-8")
            ).hexdigest(),
            axis=1,
        )
        attendance_df["dwh_valid_from"] = pd.to_datetime("now")
        attendance_df = attendance_df.replace({np.nan: None})
    except Exception as e:
        raise UploadError("Error adding metadata columns") from e

    logger.info("Starting data upload process...")
    with load_default_sqlalchemy_connection() as conn:
        # Create the table defined in the Circuit model if it doesn't exist
        try:
            Attendance.__table__.create(bind=conn, checkfirst=True)  # type: ignore
        except SQLAlchemyError as e:
            raise UploadError("Error creating table") from e

        i = modified = 0
        try:
            # Create a session
            with sessionmaker(bind=conn)() as session:
                # Iterate over the DataFrame and upsert each row
                for _, row in attendance_df.iterrows():
                    modified += Attendance.upsert(session, row, logger=logger)
                    i += 1
                session.commit()
        except Exception as e:
            raise UploadError(f"Error during data upload process, in {i}th row") from e
    logger.info(
        "Data upload process completed. %d rows processed, %d modified.",
        i,
        modified,
    )


if __name__ == "__main__":
    upload_data_from_f1destinations(
        os.path.join(get_output_dir(), "attendance_data.csv"),
    )
