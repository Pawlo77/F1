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

    id = Column(
    BigInteger,
    primary_key=True,
    autoincrement=True,
    comment="Primary key for dim_TyreManufacturer. Business key is tyre_manufacturer_name"
    )

    tyre_manufacturer_name = Column(
        String(100),
        nullable=False,
        comment="The name of the tyre manufacturer. From f1db.tyre_manufacturer. Can be modified on source.",
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        comment="Foreign key to dim_country. Can be modified on source.",
        index=True,
    )
