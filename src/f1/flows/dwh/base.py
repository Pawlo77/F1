"""
Base class for SQLAlchemy models for f1 data warehouse.

Requires MsSQL Server ODBC Driver 18.
For macOS, install the driver using:
- https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/
  install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15
"""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    String,
)


# pylint: disable=too-few-public-methods, duplicate-code
class DWHMixin:
    """Mixin class for DWH-related columns."""

    dwh_id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        nullable=False,
        comment="Unique identifier for the record",
    )
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
