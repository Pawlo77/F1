"""dim_driver model for the data warehouse."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, Date, ForeignKey, String

from .base import DWHMixin
from .dim_country import DimCountry

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import Base
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import Base


# pylint: disable=too-few-public-methods, duplicate-code
class DimDriver(Base, DWHMixin):
    """Model for the driver dimension table in the data warehouse."""

    __tablename__ = "dim_driver"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": "Source tables: f1db.driver. Business key is driver_full_name.",
        },
    )

    driver_name = Column(
        String(100),
        nullable=False,
        comment="Display name of the driver. From f1db.driver. Can be modified on source.",
    )
    driver_first_name = Column(
        String(100),
        nullable=False,
        comment="Driver's first name. From f1db.driver. Can't be modified on source.",
    )
    driver_last_name = Column(
        String(100),
        nullable=False,
        comment="Driver's last name. From f1db.driver. Can't be modified on source.",
    )
    driver_full_name = Column(
        String(100),
        nullable=False,
        comment="Driver's full name. From f1db.driver. Can't be modified on source.",
        index=True,
    )
    driver_abbreviation = Column(
        String(3),
        nullable=False,
        comment="Driver abbreviation (typically 3 letters). From f1db.driver. Can be modified on source.",
    )
    driver_permanent_number = Column(
        String(2),
        nullable=True,
        comment="Driver's permanent racing number. From f1db.driver. Can be modified on source.",
    )
    driver_gender = Column(
        String(6),
        nullable=False,
        comment="Gender of the driver. From f1db.driver. Can't be modified on source.",
    )

    driver_date_of_birth = Column(
        Date,
        nullable=False,
        comment="Date of birth. From f1db.driver. Can't be modified on source.",
    )
    driver_date_of_death = Column(
        Date,
        nullable=True,
        comment="Date of death (if applicable). From f1db.driver. Can be modified on source.",
    )
    driver_place_of_birth = Column(
        String(100),
        nullable=False,
        comment="Place of birth. From f1db.driver. Can't be modified on source.",
    )

    driver_country_of_birth_country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country. Can't be modified on source.",
    )
    driver_nationality_country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country. Can't be modified on source.",
    )
    driver_second_nationality_country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=True,
        index=True,
        comment="Foreign key to dim_country. Can't be modified on source.",
    )
