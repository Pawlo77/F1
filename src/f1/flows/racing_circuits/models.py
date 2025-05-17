# Upload files are very simmilar, models do not have public methods
# pylint: disable=duplicate-code
# pylint: disable=too-few-public-methods

"""
Prefect task to upload circuits data to the database.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, Float, Index, Integer, String, Text

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import (
        Base,
        DWHMixin,
    )
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import Base, DWHMixin


class Circuit(Base, DWHMixin):
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
