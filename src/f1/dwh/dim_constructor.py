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
    __table_args__ = ({"schema": "DWH", "comment": "Source tables: f1db.construct"},)

    constructor_name = Column(
        String(100),
        nullable=False,
        comment="Short name of the constructor. From f1db.construct",
    )
    constructor_full_name = Column(
        String(100),
        nullable=False,
        comment="Full official name of the constructor. From f1db.construct",
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country.",
    )
