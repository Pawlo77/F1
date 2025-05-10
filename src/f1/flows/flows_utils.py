"""
Utility functions for the F1 project.

Requires MsSQL Server ODBC Driver 18.
For macOS, install the driver using:
- https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/
  install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15
"""

from __future__ import annotations

from typing import cast

from prefect_sqlalchemy import SqlAlchemyConnector
from sqlalchemy import Connection, text
from sqlalchemy.orm import DeclarativeBase


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


if __name__ == "__main__":
    # Test the connection
    with load_default_sqlalchemy_connection() as conn:
        result = conn.execute(text("SELECT @@version;")).fetchall()
        for row in result:
            print(row)
