"""dim_race model for the data warehouse."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)

from .base import Base, DWHMixin
from .dim_circuit import DimCircuit


# pylint: disable=too-few-public-methods, duplicate-code
class DimRace(Base, DWHMixin):
    """Model for the race dimension table in the data warehouse."""

    __tablename__ = "dim_race"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": "Source tables: f1db.race, f1db.grand_prix, web.attendance",
        },
    )

    race_date = Column(Date, nullable=False, comment="Date of the race. From f1db.race")
    race_time = Column(
        String, nullable=True, comment="Time of the race (if available). From f1db.race"
    )
    race_round = Column(
        Integer, nullable=False, comment="Race round number. From f1db.race"
    )

    race_grand_prix_name = Column(
        String(100),
        nullable=False,
        comment="Name of the Grand Prix. From f1db.grand_prix",
    )
    race_grand_prix_full_name = Column(
        String(100),
        nullable=False,
        comment="Full name of the Grand Prix. From f1db.grand_prix",
    )
    race_grand_prix_short_name = Column(
        String(100),
        nullable=False,
        comment="Short name of the Grand Prix. From f1db.grand_prix",
    )
    race_grand_prix_abbreviation = Column(
        String(3),
        nullable=False,
        comment="Abbreviation for the Grand Prix. From f1db.grand_prix",
    )

    race_official_name = Column(
        String(100),
        nullable=False,
        comment="Official name of the event. From f1db.grand_prix",
    )
    race_weekend_attendance = Column(
        Integer,
        nullable=True,
        comment="Attendance at the race weekend. From web.attendance",
    )

    race_qualifying_format = Column(
        String(20),
        nullable=False,
        comment="Qualifying format used for the race. From f1db.race",
    )
    race_sprint_qualifying_format = Column(
        String(20), nullable=True, comment="Sprint qualifying format. From f1db.race"
    )

    circuit_id = Column(
        BigInteger,
        ForeignKey(DimCircuit.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_circuit.",
    )

    race_turns = Column(
        Integer, nullable=False, comment="Number of turns on the circuit. From Circuit"
    )
    race_laps = Column(
        Integer, nullable=False, comment="Number of laps in the race. From f1db.race"
    )
    race_distance = Column(
        Numeric(6, 3), nullable=False, comment="Total race distance. From f1db.race"
    )
    race_scheduled_laps = Column(
        Integer, nullable=True, comment="Scheduled number of laps. From f1db.race"
    )
    race_scheduled_distance = Column(
        Numeric(6, 3), nullable=True, comment="Scheduled race distance. From f1db.race"
    )

    race_drivers_championship_decider = Column(
        Boolean,
        nullable=True,
        comment="Race decided drivers' championship? From f1db.race",
    )
    race_constructors_championship_decider = Column(
        Boolean,
        nullable=True,
        comment="Race decided constructors' championship? From f1db.race",
    )

    race_pre_qualifying_date = Column(
        Date, nullable=True, comment="Date of pre-qualifying session. From f1db.race."
    )
    race_pre_qualifying_time = Column(
        String(5),
        nullable=True,
        comment="Time of pre-qualifying session. From f1db.race.",
    )
    race_free_practice_1_date = Column(
        Date, nullable=True, comment="Date of Free Practice 1. From f1db.race."
    )
    race_free_practice_1_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 1. From f1db.race."
    )
    race_free_practice_2_date = Column(
        Date, nullable=True, comment="Date of Free Practice 2. From f1db.race."
    )
    race_free_practice_2_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 2. From f1db.race."
    )
    race_free_practice_3_date = Column(
        Date, nullable=True, comment="Date of Free Practice 3. From f1db.race."
    )
    race_free_practice_3_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 3. From f1db.race."
    )
    race_free_practice_4_date = Column(
        Date, nullable=True, comment="Date of Free Practice 4. From f1db.race."
    )
    race_free_practice_4_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 4. From f1db.race."
    )
    race_qualifying_1_date = Column(
        Date, nullable=True, comment="Date of Qualifying 1 session. From f1db.race."
    )
    race_qualifying_1_time = Column(
        String(5),
        nullable=True,
        comment="Time of Qualifying 1 session. From f1db.race.",
    )
    race_qualifying_2_date = Column(
        Date, nullable=True, comment="Date of Qualifying 2 session. From f1db.race."
    )
    race_qualifying_2_time = Column(
        String(5),
        nullable=True,
        comment="Time of Qualifying 2 session. From f1db.race.",
    )
    race_qualifying_date = Column(
        Date, nullable=True, comment="Date of main qualifying session. From f1db.race."
    )
    race_qualifying_time = Column(
        String(5),
        nullable=True,
        comment="Time of main qualifying session. From f1db.race.",
    )
    race_sprint_qualifying_date = Column(
        Date,
        nullable=True,
        comment="Date of sprint qualifying session. From f1db.race.",
    )
    race_sprint_qualifying_time = Column(
        String(5),
        nullable=True,
        comment="Time of sprint qualifying session. From f1db.race.",
    )
    race_sprint_race_date = Column(
        Date, nullable=True, comment="Date of sprint race. From f1db.race."
    )
    race_sprint_race_time = Column(
        String(5), nullable=True, comment="Time of sprint race. From f1db.race."
    )
    race_warming_up_date = Column(
        Date, nullable=True, comment="Date of warm-up session. From f1db.race."
    )
    race_warming_up_time = Column(
        String(5), nullable=True, comment="Time of warm-up session. From f1db.race."
    )
