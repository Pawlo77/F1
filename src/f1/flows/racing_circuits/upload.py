"""
Prefect task to upload circuits data to the database.
"""

from __future__ import annotations

import hashlib
import os
from logging import Logger
from typing import Any, cast

import pandas as pd
from prefect import task
from prefect.logging import get_run_logger
from sqlalchemy import JSON, Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from f1.utils import Base, UploadError, load_default_sqlalchemy_connection

from .utils import get_output_dir


class Circuit(Base):
    """Model for the circuits table in the database."""

    __tablename__ = "circuits_details"
    __table_args__ = (
        Index("ix_lat_long", "latitude", "longitude"),
        {"schema": "web"},
    )

    circuit_name = Column(
        String(255),
        primary_key=True,
        nullable=False,
        comment="Circuit name, part of composite PK",
    )
    overview = Column(Text, nullable=False, comment="Overview of the circuit")
    history = Column(JSON, nullable=False, comment="History of the circuit")
    location = Column(String(255), nullable=True, comment="Location of the circuit")
    phone = Column(String(255), nullable=True, comment="Phone number of the circuit")
    email = Column(String(255), nullable=True, comment="Email of the circuit")
    website = Column(String(510), nullable=True, comment="Website of the circuit")
    latitude = Column(Float, nullable=False, comment="Latitude of the circuit")
    longitude = Column(Float, nullable=False, comment="Longitude of the circuit")
    maps = Column(JSON, nullable=False, comment="Maps of the circuit")
    rating = Column(Float, nullable=True, comment="Rating of the circuit")
    reviews_num = Column(Integer, nullable=False, comment="Number of reviews")
    tags = Column(
        JSON, nullable=False, comment="Tags of the circuit, indicating ex. FIA Grade"
    )
    url = Column(
        String(510), nullable=False, comment="URL of the circuit in racingcircuits.info"
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
        """Return a string representation of the Circuit object."""
        return f"<Circuit(name={self.circuit_name}, location={self.location})>"

    @staticmethod
    def upsert(
        session: Session,
        row: "pd.Series[Any]",
        commit_: bool = False,
        logger: Logger | None = None,
    ) -> None:
        """
        Upsert a row into the Circuit table.

        Args:
            session (Session): The SQLAlchemy session to use.
            row (pd.Series): The row to upsert.
            commit_ (bool): Whether to commit the session after the upsert.
            logger (Logger, optional): Logger for logging messages.
        """
        try:
            circuit_name = row["circuit_name"]
            dwh_hash = row["dwh_hash"]

            circuit = Circuit(**row.to_dict())
            existing_circuit = (
                session.query(Circuit).filter_by(circuit_name=circuit_name).first()
            )

            if existing_circuit and existing_circuit.dwh_hash != dwh_hash:
                if logger:
                    logger.debug(f"Updating existing circuit: {circuit_name}...")
                setattr(existing_circuit, "dwh_valid_from", row["dwh_valid_from"])
                setattr(circuit, "dwh_version", existing_circuit.dwh_version + 1)
            elif not existing_circuit and logger:
                logger.debug(f"Adding new circuit: {circuit_name}...")

            session.add(circuit)

            if commit_:
                session.commit()

        except SQLAlchemyError as e:
            session.rollback()
            raise UploadError(
                f"Error upserting circuit {row.get('circuit_name', 'UNKNOWN')}"
            ) from e


@task
def upload_data_from_circuits(circuits_df_path: str) -> None:
    """
    Upload scraped data to dwh table.

    Args:
        circuits_df_path (str): Path to the CSV file containing circuit data.

    Raises:
        Exception: If there is an error reading the CSV file or during the upload process.
    """
    logger = cast(Logger, get_run_logger())

    # Read the CSV file into a DataFrame and create a unique ID for each row
    logger.info("Reading CSV file: %s...", circuits_df_path)
    try:
        circuits_df = pd.read_csv(circuits_df_path)
    except Exception as e:
        raise UploadError(f"Error reading CSV file: {circuits_df_path}") from e

    # Add metadata columns
    logger.info("Adding metadata columns...")
    try:
        circuits_df["dwh_hash"] = circuits_df.apply(
            lambda row: hashlib.sha384(
                "|".join(str(value) for value in row.values).encode("utf-8")
            ).hexdigest(),
            axis=1,
        )
        circuits_df["dwh_valid_from"] = pd.to_datetime("now")
    except Exception as e:
        raise UploadError("Error adding metadata columns") from e

    logger.info("Starting data upload process...")
    with load_default_sqlalchemy_connection() as conn:
        # Create the table defined in the Circuit model if it doesn't exist
        try:
            Circuit.__table__.create(bind=conn, checkfirst=True)  # type: ignore
        except SQLAlchemyError as e:
            raise UploadError("Error creating table") from e

        i = 0
        try:
            # Create a session
            with sessionmaker(bind=conn)() as session:
                # Iterate over the DataFrame and upsert each row
                for _, row in circuits_df.iterrows():
                    Circuit.upsert(session, row, logger=logger)
                    i += 1
                session.commit()
        except Exception as e:
            raise UploadError(f"Error during data upload process, in {i}th row") from e


if __name__ == "__main__":
    upload_data_from_circuits(
        os.path.join(get_output_dir(), "circuit_data.csv"),
    )
