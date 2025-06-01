"""dim_constructor model for the data warehouse."""

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
class DimConstructor(Base, DWHMixin):
    """Model for the constructor dimension table in the data warehouse."""

    __tablename__ = "dim_constructor"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": "Source tables: f1db.construct. Business key is constructor_name and constructor_full_name.",
        },
    )

    constructor_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Short name of the constructor. From f1db.construct. Can't be modified on source.",
    )
    constructor_full_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Full official name of the constructor. From f1db.construct. Can't be modified on source.",
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country. Can be modified on source.",
    )
