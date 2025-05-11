# Upload files are very simmilar, models do not have public methods
# pylint: disable=R0801
# pylint: disable=too-few-public-methods

"""
Prefect task to upload circuits data to the database.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import Base, DWHMixin
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import Base, DWHMixin


class Attendance(Base, DWHMixin):
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
