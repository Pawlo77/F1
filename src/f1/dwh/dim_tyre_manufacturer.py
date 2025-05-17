"""dim_tyre_manufacturer model for the data warehouse."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    String,
)

from .base import Base, DWHMixin
from .dim_country import DimCountry


# pylint: disable=too-few-public-methods, duplicate-code
class DimTyreManufacturer(Base, DWHMixin):
    """Model for the tyre manufacturer dimension table in the data warehouse."""

    __tablename__ = "dim_tyre_manufacturer"
    __table_args__ = (
        {"schema": "DWH", "comment": "Source tables: f1db.tyre_manufacturer"},
    )

    tyre_manufacturer_name = Column(
        String(100),
        nullable=False,
        comment="The name of the tyre manufacturer. From f1db.tyre_manufacturer",
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        comment="Foreign key to dim_country.",
        index=True,
    )
