"""fact_entrant model for the data warehouse."""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, Numeric, String

from .base import Base, DWHMixin
from .dim_constructor import DimConstructor
from .dim_country import DimCountry
from .dim_driver import DimDriver
from .dim_engine_manufacturer import DimEngineManufacturer
from .dim_tyre_manufacturer import DimTyreManufacturer


# pylint: disable=too-few-public-methods, duplicate-code
class FactEntrant(Base, DWHMixin):
    """Model for the fact entrant data table in the data warehouse."""

    __tablename__ = "fact_entrant"
    __table_args__ = (
        {"schema": "DWH", "comment": "Source tables: f1.race_data. From f1.race_data."},
    )

    entrant_name = Column(
        String(100),
        nullable=False,
        comment="Display name of the entrant. From f1db.entrant",
    )
    entrant_year = Column(
        Integer, nullable=False, comment="Season year. From f1db.season_entrant"
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country.",
    )
    constructor_id = Column(
        BigInteger,
        ForeignKey(DimConstructor.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_constructor.",
    )
    engine_manufacturer_id = Column(
        BigInteger,
        ForeignKey(DimEngineManufacturer.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_engine_manufacturer.",
    )
    entrant_engine_name = Column(
        String(100), nullable=False, comment="Short engine name. From f1db.engine"
    )
    entrant_engine_full_name = Column(
        String(100), nullable=False, comment="Full engine name. From f1db.engine"
    )
    entrant_engine_capacity = Column(
        Numeric(2, 1),
        nullable=True,
        comment="Engine capacity in liters. From f1db.engine",
    )
    entrant_engine_configuration = Column(
        String(3),
        nullable=True,
        comment="Engine configuration (e.g. V6, V8). From f1db.engine",
    )
    entrant_engine_aspiration = Column(
        String(19),
        nullable=True,
        comment="Aspiration type (e.g. Turbocharged, Naturally aspirated). From f1db.engine",
    )
    tyre_manufacturer_id = Column(
        BigInteger,
        ForeignKey(DimTyreManufacturer.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_tyre_manufacturer.",
    )
    entrant_chassis_name = Column(
        String(100), nullable=False, comment="Short chassis name. From Chassis"
    )
    entrant_chassis_full_name = Column(
        String(100), nullable=False, comment="Full chassis name. From Chassis"
    )
    driver_id = Column(
        BigInteger,
        ForeignKey(DimDriver.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_driver.",
    )
    entrant_driver_rounds = Column(
        String(100),
        nullable=True,
        comment="Comma-separated round numbers. From f1db.season_entrant_driver",
    )
    entrant_driver_rounds_text = Column(
        String(100),
        nullable=True,
        comment="Text description of rounds. From f1db.season_entrant_driver",
    )
    entrant_test_driver = Column(
        Boolean,
        nullable=False,
        comment="Indicates if this is a test/reserve driver. From f1db.season_entrant_driver",
    )
