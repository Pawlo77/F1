"""dim_engine_manufacturer model for the data warehouse."""

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
class DimEngineManufacturer(Base, DWHMixin):
    """Model for the engine manufacturer dimension table in the data warehouse."""

    __tablename__ = "dim_engine_manufacturer"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": "Source tables: f1db.season_engine_manufacturer, f1db.engine_manufacturer",
        },
    )

    engine_name = Column(
        String(100),
        nullable=False,
        comment="The name of the engine manufacturer. From f1db.engine_manufacturer",
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country.",
    )
