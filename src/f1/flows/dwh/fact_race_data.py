# Decimal columns require type definition
# type: ignore
"""fact_race_data model for the data warehouse."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, BigInteger, Boolean, Column, ForeignKey, Integer, String

from .base import DWHMixin
from .dim_constructor import DimConstructor
from .dim_driver import DimDriver
from .dim_engine_manufacturer import DimEngineManufacturer
from .dim_race import DimRace
from .dim_tyre_manufacturer import DimTyreManufacturer

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import Base
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import Base


# pylint: disable=too-few-public-methods, duplicate-code
class FactRaceData(Base, DWHMixin):
    """Model for the fact race data table in the data warehouse."""

    __tablename__ = "fact_race_data"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": (
                "Source tables: f1.race_data. From f1.race_data. Business key "
                "is race_id + race_data_type + race_data_position_display_order."
            ),
        },
    )

    race_id = Column(
        BigInteger,
        ForeignKey(DimRace.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_race.",
    )
    race_data_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Session type (e.g., race, qualifying, practice). From f1.race_data. Can't be modified on source.",
    )
    race_data_position_display_order = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Order to display results by position. From f1.race_data. Can't be modified on source.",
    )
    race_data_position_number = Column(
        Integer,
        index=True,
        comment="Final classified position as a number. From f1.race_data. Can't be modified on source.",
    )
    race_data_position_text = Column(
        String(4),
        nullable=False,
        index=True,
        comment="Text version of the position (e.g., 'DNF', 'DSQ'). From f1.race_data. Can't be modified on source.",
    )
    race_data_driver_number = Column(
        String(3),
        nullable=False,
        index=True,
        comment="Car number of the driver. From f1.race_data. Can't be modified on source.",
    )
    driver_id = Column(
        BigInteger,
        ForeignKey(DimDriver.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_driver. Can't be modified on source.",
    )
    constructor_id = Column(
        BigInteger,
        ForeignKey(DimConstructor.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_constructor. Can't be modified on source.",
    )
    engine_manufacturer_id = Column(
        BigInteger,
        ForeignKey(DimEngineManufacturer.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_engine_manufacturer. Can't be modified on source.",
    )
    tyre_manufacturer_id = Column(
        BigInteger,
        ForeignKey(DimTyreManufacturer.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_tyre_manufacturer. Can't be modified on source.",
    )

    race_data_practice_time_millis = Column(
        Integer,
        comment="Practice time in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_practice_gap_millis = Column(
        Integer,
        comment="Gap to the leader in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_practice_interval_millis = Column(
        Integer,
        comment="Interval in milliseconds to previous driver. From f1.race_data. Can't be modified on source.",
    )
    practice_laps = Column(
        Integer,
        comment="Number of laps completed in practice. From f1.race_data. Can't be modified on source.",
    )

    race_data_qualifying_time_millis = Column(
        Integer,
        comment="Best qualifying time in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_qualifying_q1_millis = Column(
        Integer,
        comment="Q1 time in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_qualifying_q2_millis = Column(
        Integer,
        comment="Q2 time in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_qualifying_q3_millis = Column(
        Integer,
        comment="Q3 time in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_qualifying_gap_millis = Column(
        Integer,
        comment="Qualifying gap in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_qualifying_interval_millis = Column(
        Integer,
        comment="Interval to previous driver in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_qualifying_laps = Column(
        Integer,
        comment="Number of laps in qualifying. From f1.race_data. Can't be modified on source.",
    )

    race_data_starting_grid_position_qualification_position_number = Column(
        Integer,
        comment="Original qualifying position number. From f1.race_data. Can't be modified on source.",
    )
    race_data_starting_grid_position_qualification_position_text = Column(
        String(4),
        comment="Original qualifying position as text. From f1.race_data. Can't be modified on source.",
    )
    race_data_starting_grid_position_grid_penalty = Column(
        String(20),
        comment="Reason for grid penalty. From f1.race_data. Can't be modified on source.",
    )
    race_data_starting_grid_position_grid_penalty_positions = Column(
        Integer,
        comment="Number of grid positions penalized. From f1.race_data. Can't be modified on source.",
    )
    race_data_starting_grid_position_time_millis = Column(
        Integer,
        comment="Grid time in milliseconds. From f1.race_data. Can't be modified on source.",
    )

    race_data_race_shared_car = Column(
        Boolean,
        comment="True if the driver shared the car. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_laps = Column(
        Integer,
        comment="Number of laps completed in the race. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_time_millis = Column(
        Integer,
        comment="Total race time in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_time_penalty_millis = Column(
        Integer,
        comment="Penalty in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_gap_millis = Column(
        Integer,
        comment="Gap to winner in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_gap_laps = Column(
        Integer,
        comment="Number of laps behind leader. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_interval_millis = Column(
        Integer,
        comment="Interval in milliseconds to previous driver. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_reason_retired = Column(
        String(100),
        comment="Reason for not finishing the race. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_points = Column(
        DECIMAL(8, 2),
        comment="Championship points awarded. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_pole_position = Column(
        Boolean,
        comment="True if the driver started from pole. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_qualification_position_number = Column(
        Integer,
        comment="Qualification-based race position (numeric). From f1.race_data. Can't be modified on source.",
    )
    race_data_race_qualification_position_text = Column(
        String(4),
        comment="Qualification-based race position (text). From f1.race_data. Can't be modified on source.",
    )
    race_data_race_grid_position_number = Column(
        Integer,
        comment="Final grid start position (numeric). From f1.race_data. Can't be modified on source.",
    )
    race_data_race_grid_position_text = Column(
        String(2),
        comment="Final grid start position (text). From f1.race_data. Can't be modified on source.",
    )
    race_data_race_positions_gained = Column(
        Integer,
        comment="Number of positions gained during the race. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_pit_stops = Column(
        Integer,
        comment="Total number of pit stops made. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_fastest_lap = Column(
        Boolean,
        comment="True if the driver had the fastest lap. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_driver_of_the_day = Column(
        Boolean,
        comment="True if selected as Driver of the Day. From f1.race_data. Can't be modified on source.",
    )
    race_data_race_grand_slam = Column(
        Boolean,
        comment=(
            "True if achieved a Grand Slam (pole, win, lead all "
            "laps, fastest lap). From f1.race_data. Can't be modified on source."
        ),
    )

    race_data_fastest_lap_lap = Column(
        Integer,
        comment="Lap number with fastest lap. From f1.race_data. Can't be modified on source.",
    )
    race_data_fastest_lap_time_millis = Column(
        Integer,
        comment="Fastest lap time in milliseconds. From f1.race_data. Can't be modified on source.",
    )
    race_data_fastest_lap_gap_millis = Column(
        Integer,
        comment="Gap in milliseconds to best lap. From f1.race_data. Can't be modified on source.",
    )
    race_data_fastest_lap_interval_millis = Column(
        Integer,
        comment="Interval in milliseconds to previous fastest lap. From f1.race_data. Can't be modified on source.",
    )

    race_data_pit_stop_stop = Column(
        Integer,
        comment="Pit stop sequence number. From f1.race_data. Can't be modified on source.",
    )
    race_data_pit_stop_lap = Column(
        Integer,
        comment="Lap number of pit stop. From f1.race_data. Can't be modified on source.",
    )
    race_data_pit_stop_time_millis = Column(
        Integer,
        comment="Pit stop duration in milliseconds. From f1.race_data. Can't be modified on source.",
    )

    race_data_driver_of_the_day_percentage = Column(
        DECIMAL(4, 1),
        comment="Percentage of votes for Driver of the Day. From f1.race_data. Can't be modified on source.",
    )
