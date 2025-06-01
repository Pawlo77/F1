"""dim_country model for the data warehouse."""

from __future__ import annotations

from sqlalchemy import Column, String

from .base import Base, DWHMixin


# pylint: disable=too-few-public-methods, duplicate-code
class DimCountry(Base, DWHMixin):
    """Model for the country dimension table in the data warehouse."""

    __tablename__ = "dim_country"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": "Source tables: f1.country, f1.continent. Business key is country_name.",
        },
    )

    country_alpha2_code = Column(
        String(2),
        nullable=False,
        unique=True,
        comment="ISO 3166-1 alpha-2 country code. From f1db.country. Can't be modified on source.",
    )
    country_alpha3_code = Column(
        String(3),
        nullable=False,
        unique=True,
        comment="ISO 3166-1 alpha-3 country code. From f1db.country. Can't be modified on source.",
    )
    country_name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Country name. From f1db.country. Can't be modified on source.",
    )
    country_demonym = Column(
        String(100),
        nullable=True,
        comment="Name used to denote the nationals of the country. From f1db.country. Can't be modified on source.",
    )
    continent_name = Column(
        String(100),
        nullable=False,
        comment="Name of the continent the country belongs to. From f1db.continent. Can't be modified on source.",
    )
    continent_code = Column(
        String(2),
        nullable=False,
        comment="Code of the continent (custom-defined). From f1db.continent. Can't be modified on source.",
    )
    continent_demonym = Column(
        String(100),
        nullable=False,
        comment="Term for people from the continent. From f1db.continent. Can't be modified on source.",
    )
