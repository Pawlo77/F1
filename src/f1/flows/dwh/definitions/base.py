"""
Base class for SQLAlchemy models for f1 data warehouse.

Requires MsSQL Server ODBC Driver 18.
For macOS, install the driver using:
- https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/
  install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    String,
)

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ...flows_utils import Base
else:
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )
    from flows_utils import Base

__all__ = [
    "Base",
    "DWHMixin",
]


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
