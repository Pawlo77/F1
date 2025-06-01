# Upload files are very similar, models do not have public methods,
# Decimal columns require type definition
#
# pylint: disable=duplicate-code
# pylint: disable=too-few-public-methods,too-many-lines
# type: ignore

"""
Prefect task to upload circuits data to the database.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Tuple

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import Base, DWHMixin
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import Base, DWHMixin


class Continent(Base, DWHMixin):
    """Model for the continent table in the database."""

    __tablename__ = "continent"
    __table_args__ = (
        UniqueConstraint("code", name="uq_continent_code"),
        UniqueConstraint("name", name="uq_continent_name"),
        CheckConstraint("LEN(code) = 2", name="ck_continent_code_length"),
        CheckConstraint(
            "LEN(code) = 2 AND code NOT LIKE '%[^A-Z]%'",
            name="ck_continent_code_format",
        ),
        {"schema": "f1db", "comment": "Continent information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the continent.",
    )
    code = Column(
        String(2),
        nullable=False,
        unique=True,
        comment="The unique code of the continent.",
    )
    name = Column(
        String(100), nullable=False, unique=True, comment="The name of the continent."
    )
    demonym = Column(
        String(100),
        nullable=False,
        comment="The demonym used for people from the continent.",
    )


class Country(Base, DWHMixin):
    """Model for the country table in the database."""

    __tablename__ = "country"
    __table_args__ = (
        UniqueConstraint("alpha2_code", name="uq_country_alpha2_code"),
        UniqueConstraint("alpha3_code", name="uq_country_alpha3_code"),
        UniqueConstraint("name", name="uq_country_name"),
        CheckConstraint(
            "LEN(alpha2_code) = 2 AND alpha2_code NOT LIKE '%[^A-Z]%'",
            name="ck_country_alpha2_format",
        ),
        CheckConstraint(
            "LEN(alpha3_code) = 3 AND alpha3_code NOT LIKE '%[^A-Z]%'",
            name="ck_country_alpha3_format",
        ),
        {"schema": "f1db", "comment": "Country information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the country.",
    )
    alpha2_code = Column(
        String(2), nullable=False, unique=True, comment="The two-letter country code."
    )
    alpha3_code = Column(
        String(3), nullable=False, unique=True, comment="The three-letter country code."
    )
    name = Column(
        String(100), nullable=False, unique=True, comment="The name of the country."
    )
    demonym = Column(
        String(100),
        nullable=True,
        comment="The demonym used for people from the country.",
    )
    continent_id = Column(
        String(100),
        ForeignKey(Continent.id),
        nullable=False,
        comment="References the continent identifier.",
        index=True,
    )


class Driver(Base, DWHMixin):
    """Model for the driver table in the database."""

    __tablename__ = "driver"
    __table_args__ = (
        CheckConstraint(
            "LEN(abbreviation) = 3 AND abbreviation NOT LIKE '%[^A-Z'']%'",
            name="ck_driver_abbreviation_format",
        ),
        CheckConstraint(
            (
                "permanent_number IS NULL OR (permanent_number NOT"
                " LIKE '%[^0-9]%' AND LEN(permanent_number) BETWEEN 1 AND 2)"
            ),
            name="ck_driver_permanent_number_format",
        ),
        CheckConstraint("gender IN ('MALE', 'FEMALE')", name="ck_driver_gender_enum"),
        CheckConstraint(
            "best_championship_position IS NULL OR best_championship_position >= 1",
            name="ck_driver_best_champ_position",
        ),
        CheckConstraint(
            "best_starting_grid_position IS NULL OR best_starting_grid_position >= 1",
            name="ck_driver_best_grid_position",
        ),
        CheckConstraint(
            "best_race_result IS NULL OR best_race_result >= 1",
            name="ck_driver_best_race_result",
        ),
        CheckConstraint(
            "total_championship_wins >= 0", name="ck_driver_total_championship_wins"
        ),
        CheckConstraint("total_race_entries >= 0", name="ck_driver_total_race_entries"),
        CheckConstraint("total_race_starts >= 0", name="ck_driver_total_race_starts"),
        CheckConstraint("total_race_wins >= 0", name="ck_driver_total_race_wins"),
        CheckConstraint("total_race_laps >= 0", name="ck_driver_total_race_laps"),
        CheckConstraint("total_podiums >= 0", name="ck_driver_total_podiums"),
        CheckConstraint("total_points >= 0", name="ck_driver_total_points"),
        CheckConstraint(
            "total_championship_points >= 0", name="ck_driver_total_champ_points"
        ),
        CheckConstraint(
            "total_pole_positions >= 0", name="ck_driver_total_pole_positions"
        ),
        CheckConstraint("total_fastest_laps >= 0", name="ck_driver_total_fastest_laps"),
        CheckConstraint(
            "total_driver_of_the_day >= 0", name="ck_driver_total_driver_of_day"
        ),
        CheckConstraint("total_grand_slams >= 0", name="ck_driver_total_grand_slams"),
        {"schema": "f1db", "comment": "Driver information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the driver.",
    )
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The driver's last name or family name.",
    )
    first_name = Column(
        String(100), nullable=False, index=True, comment="The driver's first name."
    )
    last_name = Column(
        String(100), nullable=False, index=True, comment="The driver's last name."
    )
    full_name = Column(
        String(100), nullable=False, index=True, comment="The driver's full name."
    )
    abbreviation = Column(
        String(3), nullable=False, index=True, comment="Abbreviation for the driver."
    )
    permanent_number = Column(
        String(2), nullable=True, index=True, comment="The driver's permanent number."
    )
    gender = Column(
        String(6), nullable=False, index=True, comment="The driver's gender."
    )
    date_of_birth = Column(
        Date, nullable=False, index=True, comment="The driver's birth date."
    )
    date_of_death = Column(
        Date,
        nullable=True,
        index=True,
        comment="The driver's death date, if applicable.",
    )
    place_of_birth = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The place where the driver was born.",
    )
    country_of_birth_country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=False,
        index=True,
        comment="Reference to the country of birth.",
    )
    nationality_country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=False,
        index=True,
        comment="Reference to the nationality country.",
    )
    second_nationality_country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=True,
        index=True,
        comment="Reference to the second nationality country.",
    )
    best_championship_position = Column(
        Integer,
        nullable=True,
        comment="Best championship position achieved by the driver.",
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the driver.",
    )
    best_race_result = Column(
        Integer, nullable=True, comment="Best race result achieved by the driver."
    )
    total_championship_wins = Column(
        Integer, nullable=False, comment="Total championship wins."
    )
    total_race_entries = Column(Integer, nullable=False, comment="Total race entries.")
    total_race_starts = Column(Integer, nullable=False, comment="Total race starts.")
    total_race_wins = Column(Integer, nullable=False, comment="Total race wins.")
    total_race_laps = Column(Integer, nullable=False, comment="Total race laps.")
    total_podiums = Column(Integer, nullable=False, comment="Total podium finishes.")
    total_points = Column(
        Numeric(8, 2), nullable=False, comment="Total points scored by the driver."
    )
    total_championship_points = Column(
        Numeric(8, 2), nullable=False, comment="Total championship points."
    )
    total_pole_positions = Column(
        Integer, nullable=False, comment="Total pole positions."
    )
    total_fastest_laps = Column(Integer, nullable=False, comment="Total fastest laps.")
    total_driver_of_the_day = Column(
        Integer, nullable=False, comment="Total 'Driver of the Day' awards."
    )
    total_grand_slams = Column(
        Integer, nullable=False, comment="Total grand slams achieved by the driver."
    )


class DriverFamilyRelationship(Base, DWHMixin):
    """Model for the driver_family_relationship table in the database."""

    __tablename__ = "driver_family_relationship"
    __table_args__ = (
        UniqueConstraint(
            "driver_id", "other_driver_id", "type", name="uq_driver_other_driver_type"
        ),
        {"schema": "f1db", "comment": "Driver family relationships"},
    )
    FamilyRelationshipEnum = Enum(
        "PARENT",
        "PARENT_IN_LAW",
        "CHILD",
        "CHILD_IN_LAW",
        "SPOUSE",
        "SIBLING",
        "SIBLING_IN_LAW",
        "HALF_SIBLING",
        "GRANDPARENT",
        "GRANDCHILD",
        "PARENTS_SIBLING",
        "PARENTS_SIBLINGS_CHILD",
        "SIBLINGS_CHILD",
        "SIBLINGS_CHILD_IN_LAW",
        "SIBLINGS_GRANDCHILD",
        "GRANDPARENTS_SIBLING",
        name="family_relationship_enum",
    )

    driver_id = Column(
        String(100),
        ForeignKey(Driver.id),
        primary_key=True,
        nullable=False,
        index=True,
        comment="Reference to the driver id.",
    )
    position_display_order = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Display order position.",
    )
    other_driver_id = Column(
        String(100),
        ForeignKey(Driver.id),
        nullable=False,
        index=True,
        comment="Reference to the related driver id.",
    )
    type = Column(
        FamilyRelationshipEnum,
        nullable=False,
        comment="Type of the family relationship.",
    )


class Constructor(Base, DWHMixin):
    """Model for the constructor table in the database."""

    __tablename__ = "constructor"
    __table_args__ = (
        CheckConstraint(
            "best_championship_position IS NULL OR best_championship_position >= 1",
            name="chk_c_best_champ_pos_min",
        ),
        CheckConstraint(
            "best_starting_grid_position IS NULL OR best_starting_grid_position >= 1",
            name="chk_c_best_grid_pos_min",
        ),
        CheckConstraint(
            "best_race_result IS NULL OR best_race_result >= 1",
            name="chk_c_best_race_result_min",
        ),
        CheckConstraint(
            "total_championship_wins >= 0", name="chk_c_total_champ_wins_min"
        ),
        CheckConstraint("total_race_entries >= 0", name="chk_total_entries_min"),
        CheckConstraint("total_race_starts >= 0", name="chk_total_starts_min"),
        CheckConstraint("total_race_wins >= 0", name="chk_total_wins_min"),
        CheckConstraint("total_1_and_2_finishes >= 0", name="chk_total_1_and_2_min"),
        CheckConstraint("total_race_laps >= 0", name="chk_total_laps_min"),
        CheckConstraint("total_podiums >= 0", name="chk_c_total_podiums_min"),
        CheckConstraint("total_podium_races >= 0", name="chk_c_total_podium_races_min"),
        CheckConstraint("total_points >= 0", name="chk_c_total_points_min"),
        CheckConstraint(
            "total_championship_points >= 0", name="chk_c_total_champ_points_min"
        ),
        CheckConstraint("total_pole_positions >= 0", name="chk_total_poles_min"),
        CheckConstraint("total_fastest_laps >= 0", name="chk_total_fastest_min"),
        {"schema": "f1db", "comment": "Constructor information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the constructor.",
    )
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The basic name for the constructor.",
    )
    full_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The full name for the constructor.",
    )
    country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=False,
        index=True,
        comment="Reference to the country identifier.",
    )
    best_championship_position = Column(
        Integer,
        nullable=True,
        comment="Best championship position achieved by the constructor.",
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the constructor.",
    )
    best_race_result = Column(
        Integer,
        nullable=True,
        comment="Best race result achieved by the constructor.",
    )
    total_championship_wins = Column(
        Integer,
        nullable=False,
        comment="Total championship wins.",
    )
    total_race_entries = Column(
        Integer,
        nullable=False,
        comment="Total race entries.",
    )
    total_race_starts = Column(
        Integer,
        nullable=False,
        comment="Total race starts.",
    )
    total_race_wins = Column(
        Integer,
        nullable=False,
        comment="Total race wins.",
    )
    total_1_and_2_finishes = Column(
        Integer,
        nullable=False,
        comment="Total 1 and 2 finishes.",
    )
    total_race_laps = Column(
        Integer,
        nullable=False,
        comment="Total race laps.",
    )
    total_podiums = Column(
        Integer,
        nullable=False,
        comment="Total podium finishes.",
    )
    total_podium_races = Column(
        Integer,
        nullable=False,
        comment="Total podium races.",
    )
    total_points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total points scored by the constructor.",
    )
    total_championship_points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total championship points.",
    )
    total_pole_positions = Column(
        Integer,
        nullable=False,
        comment="Total pole positions.",
    )
    total_fastest_laps = Column(
        Integer,
        nullable=False,
        comment="Total fastest laps.",
    )


class ConstructorChronology(Base, DWHMixin):
    """Model for the constructor chronology table in the database."""

    __tablename__ = "constructor_chronology"
    __table_args__ = (
        UniqueConstraint(
            "constructor_id",
            "other_constructor_id",
            "year_from",
            "year_to",
            name="uq_constructor_other_years",
        ),
        CheckConstraint(
            "position_display_order >= 1", name="chk_position_display_order_min"
        ),
        CheckConstraint(
            "(year_to IS NULL) OR (year_from <= year_to)",
            name="chk_year_from_le_year_to",
        ),
        {"schema": "f1db", "comment": "Constructor chronology"},
    )

    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the constructor's identifier.",
        index=True,
    )
    position_display_order = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Display order position.",
        index=True,
    )
    other_constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        nullable=False,
        comment="Reference to the related constructor's identifier.",
        index=True,
    )
    year_from = Column(
        Integer,
        nullable=False,
        comment="Start year for the chronology.",
        index=True,
    )
    year_to = Column(
        Integer,
        nullable=True,
        comment="End year for the chronology.",
        index=True,
    )


class Chassis(Base, DWHMixin):
    """Model for the chassis table in the database."""

    __tablename__ = "chassis"
    __table_args__ = (
        UniqueConstraint(
            "constructor_id", "full_name", name="uq_constructor_full_name"
        ),
        CheckConstraint("LEN(id) > 0", name="chk_chassis_id_not_empty"),
        CheckConstraint("LEN(name) > 0", name="chk_chassis_name_not_empty"),
        CheckConstraint("LEN(full_name) > 0", name="chk_chassis_full_name_not_empty"),
        {"schema": "f1db", "comment": "Chassis information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the chassis.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        nullable=False,
        comment="Reference to the constructor identifier.",
        index=True,
    )
    name = Column(
        String(100),
        nullable=False,
        comment="The basic name for the chassis.",
        index=True,
    )
    full_name = Column(
        String(100),
        nullable=False,
        comment="The full name for the chassis.",
        index=True,
    )


class EngineManufacturer(Base, DWHMixin):
    """Model for the engine_manufacturer table in the database."""

    __tablename__ = "engine_manufacturer"
    __table_args__ = (
        CheckConstraint("LEN(name) > 0", name="chk_engine_manufacturer_name_not_empty"),
        CheckConstraint(
            "best_championship_position IS NULL OR best_championship_position >= 1",
            name="chk_em_best_champ_pos_min",
        ),
        CheckConstraint(
            "best_starting_grid_position IS NULL OR best_starting_grid_position >= 1",
            name="chk_em_best_grid_pos_min",
        ),
        CheckConstraint(
            "best_race_result IS NULL OR best_race_result >= 1",
            name="chk_em_best_race_result_min",
        ),
        CheckConstraint(
            "total_championship_wins >= 0", name="chk_em_total_champ_wins_min"
        ),
        CheckConstraint(
            "total_race_entries >= 0", name="chk_em_total_race_entries_min"
        ),
        CheckConstraint("total_race_starts >= 0", name="chk_em_total_race_starts_min"),
        CheckConstraint("total_race_wins >= 0", name="chk_em_total_race_wins_min"),
        CheckConstraint("total_race_laps >= 0", name="chk_em_total_race_laps_min"),
        CheckConstraint("total_podiums >= 0", name="chk_em_total_podiums_min"),
        CheckConstraint(
            "total_podium_races >= 0", name="chk_em_total_podium_races_min"
        ),
        CheckConstraint("total_points >= 0", name="chk_em_total_points_min"),
        CheckConstraint(
            "total_championship_points >= 0", name="chk_em_total_champ_points_min"
        ),
        CheckConstraint(
            "total_pole_positions >= 0", name="chk_em_total_pole_positions_min"
        ),
        CheckConstraint(
            "total_fastest_laps >= 0", name="chk_em_total_fastest_laps_min"
        ),
        {"schema": "f1db", "comment": "Engine manufacturer information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the engine manufacturer.",
    )
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The name of the engine manufacturer.",
    )
    country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=False,
        comment="Reference to the country identifier.",
        index=True,
    )
    best_championship_position = Column(
        Integer,
        nullable=True,
        comment="Best championship position achieved by the engine manufacturer.",
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the engine manufacturer.",
    )
    best_race_result = Column(
        Integer,
        nullable=True,
        comment="Best race result achieved by the engine manufacturer.",
    )
    total_championship_wins = Column(
        Integer,
        nullable=False,
        comment="Total championship wins.",
    )
    total_race_entries = Column(
        Integer,
        nullable=False,
        comment="Total race entries.",
    )
    total_race_starts = Column(
        Integer,
        nullable=False,
        comment="Total race starts.",
    )
    total_race_wins = Column(
        Integer,
        nullable=False,
        comment="Total race wins.",
    )
    total_race_laps = Column(
        Integer,
        nullable=False,
        comment="Total race laps.",
    )
    total_podiums = Column(
        Integer,
        nullable=False,
        comment="Total podium finishes.",
    )
    total_podium_races = Column(
        Integer,
        nullable=False,
        comment="Total podium races.",
    )
    total_points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total points scored by the engine manufacturer.",
    )
    total_championship_points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total championship points.",
    )
    total_pole_positions = Column(
        Integer,
        nullable=False,
        comment="Total pole positions.",
    )
    total_fastest_laps = Column(
        Integer,
        nullable=False,
        comment="Total fastest laps.",
    )


class Engine(Base, DWHMixin):
    """Model for the engine table in the database."""

    __tablename__ = "engine"
    __table_args__ = (
        CheckConstraint("capacity >= 0.0", name="chk_capacity_min"),
        CheckConstraint("capacity % 0.1 = 0", name="chk_capacity_multiple_of_0_1"),
        CheckConstraint(
            (
                "configuration IN ('F4', 'F8', 'F12', 'H16', 'L4', 'L6', "
                "'L8', 'V2', 'V6', 'V8', 'V10', 'V12', 'V16', 'W12')"
            ),
            name="chk_configuration_valid",
        ),
        CheckConstraint(
            (
                "aspiration IN ('NATURALLY_ASPIRATED', 'SUPERCHARGED', "
                "'TURBOCHARGED', 'TURBOCHARGED_HYBRID')"
            ),
            name="chk_aspiration_valid",
        ),
        {"schema": "f1db", "comment": "Engine information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the engine.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        nullable=False,
        comment="Reference to the engine manufacturer identifier.",
        index=True,
    )
    name = Column(
        String(100),
        nullable=False,
        comment="The basic name for the engine.",
        index=True,
    )
    full_name = Column(
        String(100),
        nullable=False,
        comment="The full name for the engine.",
        index=True,
    )
    capacity = Column(
        Numeric(2, 1),
        nullable=True,
        comment="The engine capacity.",
        index=True,
    )
    configuration = Column(
        Enum(
            "F4",
            "F8",
            "F12",
            "H16",
            "L4",
            "L6",
            "L8",
            "V2",
            "V6",
            "V8",
            "V10",
            "V12",
            "V16",
            "W12",
            name="engine_configuration_enum",
            create_type=False,
        ),
        nullable=True,
        comment="The engine configuration.",
    )
    aspiration = Column(
        Enum(
            "NATURALLY_ASPIRATED",
            "SUPERCHARGED",
            "TURBOCHARGED",
            "TURBOCHARGED_HYBRID",
            name="engine_aspiration_enum",
            create_type=False,
        ),
        nullable=True,
        comment="The engine aspiration type.",
    )


class TyreManufacturer(Base, DWHMixin):
    """Model for the tyre_manufacturer table in the database."""

    __tablename__ = "tyre_manufacturer"
    __table_args__ = (
        CheckConstraint(
            "best_starting_grid_position >= 1 OR best_starting_grid_position IS NULL",
            name="chk_best_starting_grid_position",
        ),
        CheckConstraint(
            "best_race_result >= 1 OR best_race_result IS NULL",
            name="chk_best_race_result",
        ),
        CheckConstraint(
            "total_race_entries >= 0",
            name="chk_tm_total_race_entries_min",
        ),
        CheckConstraint(
            "total_race_starts >= 0",
            name="chk_tm_total_race_starts_min",
        ),
        CheckConstraint(
            "total_race_wins >= 0",
            name="chk_tm_total_race_wins_min",
        ),
        CheckConstraint(
            "total_race_laps >= 0",
            name="chk_tm_total_race_laps_min",
        ),
        CheckConstraint(
            "total_podiums >= 0",
            name="chk_tm_total_podiums_min",
        ),
        CheckConstraint(
            "total_podium_races >= 0",
            name="chk_tm_total_podium_races_min",
        ),
        CheckConstraint(
            "total_pole_positions >= 0",
            name="chk_tm_total_pole_positions_min",
        ),
        CheckConstraint(
            "total_fastest_laps >= 0",
            name="chk_tm_total_fastest_laps_min",
        ),
        {"schema": "f1db", "comment": "Tyre manufacturer information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the tyre manufacturer.",
    )
    name = Column(
        String(100),
        nullable=False,
        comment="The name of the tyre manufacturer.",
        index=True,
    )
    country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=False,
        comment="Reference to the country identifier.",
        index=True,
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the tyre manufacturer.",
    )
    best_race_result = Column(
        Integer,
        nullable=True,
        comment="Best race result achieved by the tyre manufacturer.",
    )
    total_race_entries = Column(
        Integer, nullable=False, comment="Total race entries by the tyre manufacturer."
    )
    total_race_starts = Column(
        Integer, nullable=False, comment="Total race starts by the tyre manufacturer."
    )
    total_race_wins = Column(
        Integer, nullable=False, comment="Total race wins by the tyre manufacturer."
    )
    total_race_laps = Column(
        Integer, nullable=False, comment="Total race laps by the tyre manufacturer."
    )
    total_podiums = Column(
        Integer,
        nullable=False,
        comment="Total podium finishes by the tyre manufacturer.",
    )
    total_podium_races = Column(
        Integer, nullable=False, comment="Total podium races by the tyre manufacturer."
    )
    total_pole_positions = Column(
        Integer,
        nullable=False,
        comment="Total pole positions by the tyre manufacturer.",
    )
    total_fastest_laps = Column(
        Integer, nullable=False, comment="Total fastest laps by the tyre manufacturer."
    )


class Entrant(Base, DWHMixin):
    """Model for the entrant table in the database."""

    __tablename__ = "entrant"
    __table_args__ = ({"schema": "f1db", "comment": "Entrant information"},)

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the entrant.",
    )
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The name of the entrant.",
    )


class Circuit(Base, DWHMixin):
    """Model for the circuit table in the database."""

    __tablename__ = "circuit"
    __table_args__ = (
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90", name="check_latitude_range"
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180", name="check_longitude_range"
        ),
        CheckConstraint(
            "type IN ('RACE', 'ROAD', 'STREET')", name="check_circuit_type"
        ),
        CheckConstraint(
            "direction IN ('CLOCKWISE', 'ANTI_CLOCKWISE')",
            name="check_circuit_direction",
        ),
        CheckConstraint("total_races_held >= 0", name="check_total_races_held"),
        {"schema": "f1db", "comment": "Circuit information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the circuit.",
    )
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The name of the circuit.",
    )
    full_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The full name of the circuit.",
    )
    previous_names = Column(
        String(255),
        nullable=True,
        comment="Previous names of the circuit, if any.",
    )
    type = Column(
        String(6),
        nullable=False,
        index=True,
        comment="Type of the circuit.",
    )
    direction = Column(
        String(14),
        nullable=False,
        index=True,
        comment="The direction for the circuit.",
    )
    place_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The place name of the circuit.",
    )
    country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=False,
        index=True,
        comment="Reference to the country identifier.",
    )
    latitude = Column(
        Numeric(10, 6),
        nullable=False,
        index=True,
        comment="The latitude coordinate of the circuit.",
    )
    longitude = Column(
        Numeric(10, 6),
        nullable=False,
        index=True,
        comment="The longitude coordinate of the circuit.",
    )
    length = Column(
        Numeric(6, 3),
        nullable=False,
        comment="The length of the circuit.",
    )
    turns = Column(
        Integer,
        nullable=False,
        comment="The number of turns in the circuit.",
    )
    total_races_held = Column(
        Integer,
        nullable=False,
        comment="Total races held at the circuit.",
    )


class GrandPrix(Base, DWHMixin):
    """Model for the grand_prix table in the database."""

    __tablename__ = "grand_prix"
    __table_args__ = (
        CheckConstraint("LEN(abbreviation) = 3", name="check_abbreviation_length"),
        CheckConstraint(
            "abbreviation LIKE '[A-Z0-9][A-Z0-9][A-Z0-9]'",
            name="check_abbreviation_format",
        ),
        CheckConstraint(
            "total_races_held >= 0", name="check_total_races_held_nonnegative"
        ),
        {"schema": "f1db", "comment": "Grand Prix information"},
    )

    id = Column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="The unique identifier for the grand prix.",
    )
    name = Column(
        String(100),
        nullable=False,
        comment="The name of the grand prix.",
        index=True,
    )
    full_name = Column(
        String(100),
        nullable=False,
        comment="The full name of the grand prix.",
        index=True,
    )
    short_name = Column(
        String(100),
        nullable=False,
        comment="The short name of the grand prix.",
        index=True,
    )
    abbreviation = Column(
        String(3),
        nullable=False,
        comment="The abbreviation of the grand prix.",
        index=True,
    )
    country_id = Column(
        String(100),
        ForeignKey(Country.id),
        comment="Reference to the country's identifier.",
        index=True,
    )
    total_races_held = Column(
        Integer,
        nullable=False,
        comment="Total races held for the grand prix.",
    )


class Season(Base, DWHMixin):
    """Model for the season table in the database."""

    __tablename__ = "season"
    __table_args__ = ({"schema": "f1db", "comment": "Season information"},)

    year = Column(Integer, primary_key=True, nullable=False, comment="The season year.")


class SeasonEntrant(Base, DWHMixin):
    """Model for the season_entrant table in the database."""

    __tablename__ = "season_entrant"
    __table_args__ = ({"schema": "f1db", "comment": "Season entrant information"},)

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    entrant_id = Column(
        String(100),
        ForeignKey(Entrant.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the entrant identifier.",
    )
    country_id = Column(
        String(100),
        ForeignKey(Country.id),
        nullable=False,
        index=True,
        comment="Reference to the country identifier.",
    )


class SeasonEntrantConstructor(Base, DWHMixin):
    """Model for the season_entrant_constructor table in the database."""

    __tablename__ = "season_entrant_constructor"
    __table_args__ = (
        CheckConstraint("year >= 1950", name="check_seasonentrant_year_valid"),
        {"schema": "f1db", "comment": "Season entrant constructor information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    entrant_id = Column(
        String(100),
        ForeignKey(Entrant.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the entrant identifier.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the constructor identifier.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the engine manufacturer identifier.",
    )


class SeasonEntrantChassis(Base, DWHMixin):
    """Model for the season_entrant_chassis table in the database."""

    __tablename__ = "season_entrant_chassis"
    __table_args__ = (
        {"schema": "f1db", "comment": "Season entrant chassis information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    entrant_id = Column(
        String(100),
        ForeignKey(Entrant.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the entrant identifier.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the constructor identifier.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the engine manufacturer identifier.",
    )
    chassis_id = Column(
        String(100),
        ForeignKey(Chassis.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the chassis identifier.",
    )


class SeasonEntrantEngine(Base, DWHMixin):
    """Model for the season_entrant_engine table in the database."""

    __tablename__ = "season_entrant_engine"
    __table_args__ = (
        {"schema": "f1db", "comment": "Season entrant engine information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    entrant_id = Column(
        String(100),
        ForeignKey(Entrant.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the entrant identifier.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the constructor identifier.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the engine manufacturer identifier.",
    )
    engine_id = Column(
        String(100),
        ForeignKey(Engine.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the engine identifier.",
    )


class SeasonEntrantTyreManufacturer(Base, DWHMixin):
    """Model for the season_entrant_tyre_manufacturer table in the database."""

    __tablename__ = "season_entrant_tyre_manufacturer"
    __table_args__ = (
        {"schema": "f1db", "comment": "Season entrant tyre manufacturer information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    entrant_id = Column(
        String(100),
        ForeignKey(Entrant.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the entrant identifier.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the constructor identifier.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the engine manufacturer identifier.",
    )
    tyre_manufacturer_id = Column(
        String(100),
        ForeignKey(TyreManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the tyre manufacturer identifier.",
    )


class SeasonEntrantDriver(Base, DWHMixin):
    """Model for the season_entrant_driver table in the database."""

    __tablename__ = "season_entrant_driver"
    __table_args__ = (
        CheckConstraint("year >= 1950", name="check_sed_year_valid"),
        CheckConstraint(
            "rounds_text NOT LIKE '%[^0-9,-]%' AND LEN(rounds_text) > 0",
            name="check_sed_rounds_text_format",
        ),
        UniqueConstraint(
            "year",
            "entrant_id",
            "constructor_id",
            "engine_manufacturer_id",
            "driver_id",
            name="uq_sed_composite",
        ),
        {"schema": "f1db", "comment": "Season entrant driver information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    entrant_id = Column(
        String(100),
        ForeignKey(Entrant.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the entrant identifier.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the constructor identifier.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the engine manufacturer identifier.",
    )
    driver_id = Column(
        String(100),
        ForeignKey(Driver.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the driver identifier.",
    )
    rounds = Column(
        String(100),
        nullable=True,
        comment="Rounds information.",
    )
    rounds_text = Column(
        String(100),
        nullable=True,
        comment="Text description of rounds.",
    )
    test_driver = Column(
        Boolean,
        nullable=False,
        comment="Indicates if the driver is a test driver.",
    )


class SeasonConstructor(Base, DWHMixin):
    """Model for the season_constructor table in the database."""

    __tablename__ = "season_constructor"
    __table_args__ = (
        CheckConstraint("year >= 1950", name="check_sc_year_valid"),
        CheckConstraint(
            (
                "(position_text NOT LIKE '%[^0-9]%' AND LEN(position_text) > 0) "
                "OR position_text IN ('DSQ', 'EX')"
            ),
            name="check_sc_position_text_format",
        ),
        CheckConstraint("total_points >= 0", name="check_sc_points_non_negative"),
        CheckConstraint(
            "total_points % 0.01 = 0", name="check_sc_points_multiple_of_0_01"
        ),
        {"schema": "f1db", "comment": "Season constructor information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the constructor identifier.",
    )
    position_number = Column(
        Integer, nullable=True, comment="Position number assigned."
    )
    position_text = Column(
        String(4), nullable=True, comment="Text description of the position."
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the constructor.",
    )
    best_race_result = Column(
        Integer,
        nullable=True,
        comment="Best race result achieved by the constructor.",
    )
    total_race_entries = Column(
        Integer,
        nullable=False,
        comment="Total race entries.",
    )
    total_race_starts = Column(
        Integer,
        nullable=False,
        comment="Total race starts.",
    )
    total_race_wins = Column(
        Integer,
        nullable=False,
        comment="Total race wins.",
    )
    total_1_and_2_finishes = Column(
        Integer,
        nullable=False,
        comment="Total 1 and 2 finishes.",
    )
    total_race_laps = Column(
        Integer,
        nullable=False,
        comment="Total race laps.",
    )
    total_podiums = Column(
        Integer,
        nullable=False,
        comment="Total podium finishes.",
    )
    total_podium_races = Column(
        Integer,
        nullable=False,
        comment="Total podium races.",
    )
    total_points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total points scored by the constructor.",
    )
    total_pole_positions = Column(
        Integer,
        nullable=False,
        comment="Total pole positions.",
    )
    total_fastest_laps = Column(
        Integer,
        nullable=False,
        comment="Total fastest laps.",
    )


class SeasonEngineManufacturer(Base, DWHMixin):
    """Model for the season_engine_manufacturer table in the database."""

    __tablename__ = "season_engine_manufacturer"
    __table_args__ = (
        CheckConstraint(
            "position_number IS NULL OR position_number >= 1",
            name="check_sem_position_number_min",
        ),
        CheckConstraint(
            "best_starting_grid_position IS NULL OR best_starting_grid_position >= 1",
            name="check_sem_best_start_grid_min",
        ),
        CheckConstraint(
            "best_race_result IS NULL OR best_race_result >= 1",
            name="check_sem_best_race_result_min",
        ),
        CheckConstraint(
            "(position_text LIKE '[0-9]%' OR position_text IN ('DSQ', 'EX'))",
            name="check_sem_position_text_format",
        ),
        CheckConstraint("total_points >= 0", name="check_sem_points_non_negative"),
        CheckConstraint(
            "total_points % 0.01 = 0", name="check_sem_points_multiple_of_0_01"
        ),
        {"schema": "f1db", "comment": "Season engine manufacturer information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the engine manufacturer identifier.",
    )
    position_number = Column(
        Integer,
        nullable=True,
        comment="Position number assigned.",
    )
    position_text = Column(
        String(4),
        nullable=True,
        comment="Text description of the position.",
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the engine manufacturer.",
    )
    best_race_result = Column(
        Integer,
        nullable=True,
        comment="Best race result achieved by the engine manufacturer.",
    )
    total_race_entries = Column(
        Integer,
        nullable=False,
        comment="Total race entries.",
    )
    total_race_starts = Column(
        Integer,
        nullable=False,
        comment="Total race starts.",
    )
    total_race_wins = Column(
        Integer,
        nullable=False,
        comment="Total race wins.",
    )
    total_race_laps = Column(
        Integer,
        nullable=False,
        comment="Total race laps.",
    )
    total_podiums = Column(
        Integer,
        nullable=False,
        comment="Total podium finishes.",
    )
    total_podium_races = Column(
        Integer,
        nullable=False,
        comment="Total podium races.",
    )
    total_points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total points scored by the engine manufacturer.",
    )
    total_pole_positions = Column(
        Integer,
        nullable=False,
        comment="Total pole positions.",
    )
    total_fastest_laps = Column(
        Integer,
        nullable=False,
        comment="Total fastest laps.",
    )


class SeasonTyreManufacturer(Base, DWHMixin):
    """Model for the season_tyre_manufacturer table in the database."""

    __tablename__ = "season_tyre_manufacturer"
    __table_args__ = (
        CheckConstraint(
            "best_starting_grid_position IS NULL OR best_starting_grid_position >= 1",
            name="check_stm_best_start_grid_min",
        ),
        CheckConstraint(
            "best_race_result IS NULL OR best_race_result >= 1",
            name="check_stm_best_race_result_min",
        ),
        CheckConstraint(
            "total_race_entries >= 0", name="check_stm_total_race_entries_non_negative"
        ),
        CheckConstraint(
            "total_race_starts >= 0", name="check_stm_total_race_starts_non_negative"
        ),
        CheckConstraint(
            "total_race_wins >= 0", name="check_stm_total_race_wins_non_negative"
        ),
        CheckConstraint(
            "total_race_laps >= 0", name="check_stm_total_race_laps_non_negative"
        ),
        CheckConstraint(
            "total_podiums >= 0", name="check_stm_total_podiums_non_negative"
        ),
        CheckConstraint(
            "total_podium_races >= 0", name="check_stm_total_podium_races_non_negative"
        ),
        CheckConstraint(
            "total_pole_positions >= 0",
            name="check_stm_total_pole_positions_non_negative",
        ),
        CheckConstraint(
            "total_fastest_laps >= 0", name="check_stm_total_fastest_laps_non_negative"
        ),
        {"schema": "f1db", "comment": "Season tyre manufacturer information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    tyre_manufacturer_id = Column(
        String(100),
        ForeignKey(TyreManufacturer.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the tyre manufacturer identifier.",
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the tyre manufacturer.",
    )
    best_race_result = Column(
        Integer,
        nullable=True,
        comment="Best race result achieved by the tyre manufacturer.",
    )
    total_race_entries = Column(
        Integer,
        nullable=False,
        comment="Total race entries by the tyre manufacturer.",
    )
    total_race_starts = Column(
        Integer,
        nullable=False,
        comment="Total race starts by the tyre manufacturer.",
    )
    total_race_wins = Column(
        Integer,
        nullable=False,
        comment="Total race wins by the tyre manufacturer.",
    )
    total_race_laps = Column(
        Integer,
        nullable=False,
        comment="Total race laps by the tyre manufacturer.",
    )
    total_podiums = Column(
        Integer,
        nullable=False,
        comment="Total podium finishes by the tyre manufacturer.",
    )
    total_podium_races = Column(
        Integer,
        nullable=False,
        comment="Total podium races by the tyre manufacturer.",
    )
    total_pole_positions = Column(
        Integer,
        nullable=False,
        comment="Total pole positions by the tyre manufacturer.",
    )
    total_fastest_laps = Column(
        Integer,
        nullable=False,
        comment="Total fastest laps by the tyre manufacturer.",
    )


class SeasonDriver(Base, DWHMixin):
    """Model for the season_driver table in the database."""

    __tablename__ = "season_driver"
    __table_args__ = (
        CheckConstraint(
            "position_number IS NULL OR position_number >= 1",
            name="check_sd_position_number_min",
        ),
        CheckConstraint(
            "best_starting_grid_position IS NULL OR best_starting_grid_position >= 1",
            name="check_sd_best_start_grid_min",
        ),
        CheckConstraint(
            "best_race_result IS NULL OR best_race_result >= 1",
            name="check_sd_best_race_result_min",
        ),
        CheckConstraint(
            "total_race_entries >= 0", name="check_sd_total_race_entries_min"
        ),
        CheckConstraint(
            "total_race_starts >= 0", name="check_sd_total_race_starts_min"
        ),
        CheckConstraint("total_race_wins >= 0", name="check_sd_total_race_wins_min"),
        CheckConstraint("total_race_laps >= 0", name="check_sd_total_race_laps_min"),
        CheckConstraint("total_podiums >= 0", name="check_sd_total_podiums_min"),
        CheckConstraint("total_points >= 0", name="check_sd_total_points_min"),
        CheckConstraint(
            "total_pole_positions >= 0", name="check_sd_total_pole_positions_min"
        ),
        CheckConstraint(
            "total_fastest_laps >= 0", name="check_sd_total_fastest_laps_min"
        ),
        CheckConstraint(
            "total_driver_of_the_day >= 0", name="check_sd_total_driver_of_the_day_min"
        ),
        CheckConstraint(
            "total_grand_slams >= 0", name="check_sd_total_grand_slams_min"
        ),
        {"schema": "f1db", "comment": "Season driver information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    driver_id = Column(
        String(100),
        ForeignKey(Driver.id),
        primary_key=True,
        nullable=False,
        comment="Reference to the driver identifier.",
    )
    position_number = Column(
        Integer,
        nullable=True,
        comment="Position number assigned.",
    )
    position_text = Column(
        String(4),
        nullable=True,
        comment="Text description of the position.",
    )
    best_starting_grid_position = Column(
        Integer,
        nullable=True,
        comment="Best starting grid position achieved by the driver.",
    )
    best_race_result = Column(
        Integer,
        nullable=True,
        comment="Best race result achieved by the driver.",
    )
    total_race_entries = Column(
        Integer,
        nullable=False,
        comment="Total race entries.",
    )
    total_race_starts = Column(
        Integer,
        nullable=False,
        comment="Total race starts.",
    )
    total_race_wins = Column(
        Integer,
        nullable=False,
        comment="Total race wins.",
    )
    total_race_laps = Column(
        Integer,
        nullable=False,
        comment="Total race laps.",
    )
    total_podiums = Column(
        Integer,
        nullable=False,
        comment="Total podium finishes.",
    )
    total_points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total points scored by the driver.",
    )
    total_pole_positions = Column(
        Integer,
        nullable=False,
        comment="Total pole positions.",
    )
    total_fastest_laps = Column(
        Integer,
        nullable=False,
        comment="Total fastest laps.",
    )
    total_driver_of_the_day = Column(
        Integer,
        nullable=False,
        comment="Total 'Driver of the Day' awards.",
    )
    total_grand_slams = Column(
        Integer,
        nullable=False,
        comment="Total grand slams achieved by the driver.",
    )


class SeasonDriverStanding(Base, DWHMixin):
    """Model for the season_driver_standing table in the database."""

    __tablename__ = "season_driver_standing"
    __table_args__ = (
        CheckConstraint(
            "position_display_order >= 1", name="check_sds_position_display_order_min"
        ),
        CheckConstraint(
            "position_number IS NULL OR position_number >= 1",
            name="check_sds_position_number_min",
        ),
        CheckConstraint("points >= 0", name="check_sds_points_min"),
        CheckConstraint(
            (
                "(position_text NOT LIKE '%[^0-9]%' AND LEN(position_text) > 0) "
                "OR position_text IN ('DSQ', 'EX')"
            ),
            name="check_sds_position_text_format",
        ),
        {"schema": "f1db", "comment": "Season driver standing information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    position_display_order = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Display order position.",
    )
    position_number = Column(
        Integer,
        nullable=True,
        index=True,
        comment="Position number.",
    )
    position_text = Column(
        String(4),
        nullable=False,
        index=True,
        comment="Text description of the position.",
    )
    driver_id = Column(
        String(100),
        ForeignKey(Driver.id),
        nullable=False,
        index=True,
        comment="Reference to the driver identifier.",
    )
    points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total points scored by the driver.",
    )


class SeasonConstructorStanding(Base, DWHMixin):
    """Model for the season_constructor_standing table in the database."""

    __tablename__ = "season_constructor_standing"
    __table_args__ = (
        CheckConstraint(
            "position_display_order >= 1", name="check_scs_position_display_order_min"
        ),
        CheckConstraint(
            "position_number IS NULL OR position_number >= 1",
            name="check_scs_position_number_min",
        ),
        CheckConstraint("points >= 0", name="check_scs_points_min"),
        CheckConstraint(
            (
                "(position_text NOT LIKE '%[^0-9]%' AND LEN(position_text) > 0) "
                "OR position_text IN ('DSQ', 'EX')"
            ),
            name="check_scs_position_text_format",
        ),
        {"schema": "f1db", "comment": "Season constructor standing information"},
    )

    year = Column(
        Integer,
        ForeignKey(Season.year),
        primary_key=True,
        nullable=False,
        comment="The season year.",
    )
    position_display_order = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Display order position.",
    )
    position_number = Column(
        Integer,
        nullable=True,
        index=True,
        comment="Position number.",
    )
    position_text = Column(
        String(4),
        nullable=False,
        index=True,
        comment="Text description of the position.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        nullable=False,
        index=True,
        comment="Reference to the constructor identifier.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        nullable=False,
        index=True,
        comment="Reference to the engine manufacturer identifier.",
    )
    points = Column(
        Numeric(8, 2),
        nullable=False,
        comment="Total points scored by the constructor.",
    )


class Race(Base, DWHMixin):
    """Model for the race table in the database."""

    __tablename__ = "race"
    __table_args__ = (
        CheckConstraint("year > 1900", name="check_year_positive"),
        CheckConstraint("round >= 1", name="check_round_positive"),
        CheckConstraint("course_length >= 0", name="check_course_length_positive"),
        CheckConstraint("turns >= 0", name="check_turns_positive"),
        CheckConstraint("laps >= 0", name="check_laps_positive"),
        CheckConstraint("distance >= 0", name="check_distance_positive"),
        CheckConstraint(
            "scheduled_laps >= 0 OR scheduled_laps IS NULL",
            name="check_scheduled_laps_null_or_positive",
        ),
        CheckConstraint(
            "scheduled_distance >= 0 OR scheduled_distance IS NULL",
            name="check_scheduled_distance_null_or_positive",
        ),
        CheckConstraint(
            "drivers_championship_decider IS NULL OR drivers_championship_decider IN (1, 0)",
            name="check_drivers_championship_decider",
        ),
        CheckConstraint(
            (
                "constructors_championship_decider IS NULL OR "
                "constructors_championship_decider IN (1, 0)"
            ),
            name="check_constructors_championship_decider",
        ),
        {"schema": "f1db", "comment": "Race information"},
    )

    id = Column(
        Integer, primary_key=True, nullable=False, comment="Unique race identifier."
    )
    year = Column(
        Integer,
        ForeignKey(Season.year),
        nullable=False,
        index=True,
        comment="Season year.",
    )
    round = Column(
        Integer, nullable=False, index=True, comment="Round number within the season."
    )
    date = Column(Date, nullable=False, index=True, comment="Date of the main race.")
    time = Column(Text, nullable=True, comment="Start time of the main race.")
    grand_prix_id = Column(
        String(100),
        ForeignKey(GrandPrix.id),
        nullable=False,
        index=True,
        comment="Grand Prix identifier.",
    )
    official_name = Column(
        String(100), nullable=False, index=True, comment="Official race name."
    )
    qualifying_format = Column(
        String(20), nullable=False, index=True, comment="Format of qualifying session."
    )
    sprint_qualifying_format = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Format of sprint qualifying session, if any.",
    )
    circuit_id = Column(
        String(100),
        ForeignKey(Circuit.id),
        nullable=False,
        index=True,
        comment="Circuit identifier.",
    )
    circuit_type = Column(
        String(6),
        nullable=False,
        index=True,
        comment="Type of circuit (e.g., street, road).",
    )
    direction = Column(
        String(14),
        nullable=False,
        index=True,
        comment="Race direction (e.g., clockwise).",
    )
    course_length = Column(
        DECIMAL(6, 3), nullable=False, comment="Length of the course in kilometers."
    )
    turns = Column(Integer, nullable=False, comment="Number of turns in the circuit.")
    laps = Column(Integer, nullable=False, comment="Scheduled number of laps.")
    distance = Column(
        DECIMAL(6, 3), nullable=False, comment="Total race distance in kilometers."
    )
    scheduled_laps = Column(
        Integer, nullable=True, comment="Originally scheduled number of laps."
    )
    scheduled_distance = Column(
        DECIMAL(6, 3), nullable=True, comment="Originally scheduled race distance."
    )
    drivers_championship_decider = Column(
        Boolean,
        nullable=True,
        comment="True if this race decided the drivers' championship.",
    )
    constructors_championship_decider = Column(
        Boolean,
        nullable=True,
        comment="True if this race decided the constructors' championship.",
    )
    pre_qualifying_date = Column(
        Date, nullable=True, comment="Date of pre-qualifying session."
    )
    pre_qualifying_time = Column(
        String(5), nullable=True, comment="Time of pre-qualifying session."
    )
    free_practice_1_date = Column(
        Date, nullable=True, comment="Date of Free Practice 1."
    )
    free_practice_1_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 1."
    )
    free_practice_2_date = Column(
        Date, nullable=True, comment="Date of Free Practice 2."
    )
    free_practice_2_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 2."
    )
    free_practice_3_date = Column(
        Date, nullable=True, comment="Date of Free Practice 3."
    )
    free_practice_3_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 3."
    )
    free_practice_4_date = Column(
        Date, nullable=True, comment="Date of Free Practice 4."
    )
    free_practice_4_time = Column(
        String(5), nullable=True, comment="Time of Free Practice 4."
    )
    qualifying_1_date = Column(
        Date, nullable=True, comment="Date of Qualifying 1 session."
    )
    qualifying_1_time = Column(
        String(5), nullable=True, comment="Time of Qualifying 1 session."
    )
    qualifying_2_date = Column(
        Date, nullable=True, comment="Date of Qualifying 2 session."
    )
    qualifying_2_time = Column(
        String(5), nullable=True, comment="Time of Qualifying 2 session."
    )
    qualifying_date = Column(
        Date, nullable=True, comment="Date of main qualifying session."
    )
    qualifying_time = Column(
        String(5), nullable=True, comment="Time of main qualifying session."
    )
    sprint_qualifying_date = Column(
        Date, nullable=True, comment="Date of sprint qualifying session."
    )
    sprint_qualifying_time = Column(
        String(5), nullable=True, comment="Time of sprint qualifying session."
    )
    sprint_race_date = Column(Date, nullable=True, comment="Date of sprint race.")
    sprint_race_time = Column(String(5), nullable=True, comment="Time of sprint race.")
    warming_up_date = Column(Date, nullable=True, comment="Date of warm-up session.")
    warming_up_time = Column(
        String(5), nullable=True, comment="Time of warm-up session."
    )


class RaceData(Base, DWHMixin):
    """Model representing detailed data for a specific race session and driver."""

    __tablename__ = "race_data"
    __table_args__ = ({"schema": "f1db", "comment": "Race data information"},)

    race_id = Column(
        Integer,
        ForeignKey(Race.id),
        primary_key=True,
        nullable=False,
        comment="Unique race identifier.",
    )
    type = Column(
        String(50),
        nullable=False,
        primary_key=True,
        comment="Session type (e.g., race, qualifying, practice).",
    )
    position_display_order = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Order to display results by position.",
    )
    position_number = Column(
        Integer, index=True, comment="Final classified position as a number."
    )
    position_text = Column(
        String(4),
        nullable=False,
        index=True,
        comment="Text version of the position (e.g., 'DNF', 'DSQ').",
    )
    driver_number = Column(
        String(3), nullable=False, index=True, comment="Car number of the driver."
    )
    driver_id = Column(
        String(100),
        ForeignKey(Driver.id),
        nullable=False,
        index=True,
        comment="Unique driver identifier.",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        nullable=False,
        index=True,
        comment="Constructor team identifier.",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        nullable=False,
        index=True,
        comment="Engine manufacturer identifier.",
    )
    tyre_manufacturer_id = Column(
        String(100),
        ForeignKey(TyreManufacturer.id),
        nullable=False,
        index=True,
        comment="Tyre manufacturer identifier.",
    )

    practice_time = Column(String(20), comment="Practice session lap time.")
    practice_time_millis = Column(Integer, comment="Practice time in milliseconds.")
    practice_gap = Column(String(20), comment="Gap to the session leader.")
    practice_gap_millis = Column(Integer, comment="Gap to the leader in milliseconds.")
    practice_interval = Column(String(20), comment="Gap to the previous driver.")
    practice_interval_millis = Column(
        Integer, comment="Interval in milliseconds to previous driver."
    )
    practice_laps = Column(Integer, comment="Number of laps completed in practice.")

    qualifying_time = Column(String(20), comment="Qualifying session best time.")
    qualifying_time_millis = Column(
        Integer, comment="Best qualifying time in milliseconds."
    )
    qualifying_q1 = Column(String(20), comment="Q1 session time.")
    qualifying_q1_millis = Column(Integer, comment="Q1 time in milliseconds.")
    qualifying_q2 = Column(String(20), comment="Q2 session time.")
    qualifying_q2_millis = Column(Integer, comment="Q2 time in milliseconds.")
    qualifying_q3 = Column(String(20), comment="Q3 session time.")
    qualifying_q3_millis = Column(Integer, comment="Q3 time in milliseconds.")
    qualifying_gap = Column(String(20), comment="Qualifying gap to fastest driver.")
    qualifying_gap_millis = Column(Integer, comment="Qualifying gap in milliseconds.")
    qualifying_interval = Column(
        String(20), comment="Qualifying gap to previous driver."
    )
    qualifying_interval_millis = Column(
        Integer, comment="Interval to previous driver in milliseconds."
    )
    qualifying_laps = Column(Integer, comment="Number of laps in qualifying.")

    starting_grid_position_qualification_position_number = Column(
        Integer, comment="Original qualifying position number."
    )
    starting_grid_position_qualification_position_text = Column(
        String(4), comment="Original qualifying position as text."
    )
    starting_grid_position_grid_penalty = Column(
        String(20), comment="Reason for grid penalty."
    )
    starting_grid_position_grid_penalty_positions = Column(
        Integer, comment="Number of grid positions penalized."
    )
    starting_grid_position_time = Column(String(20), comment="Grid position lap time.")
    starting_grid_position_time_millis = Column(
        Integer, comment="Grid time in milliseconds."
    )

    race_shared_car = Column(Boolean, comment="True if the driver shared the car.")
    race_laps = Column(Integer, comment="Number of laps completed in the race.")
    race_time = Column(String(20), comment="Total race time.")
    race_time_millis = Column(Integer, comment="Total race time in milliseconds.")
    race_time_penalty = Column(String(20), comment="Time penalty in race.")
    race_time_penalty_millis = Column(Integer, comment="Penalty in milliseconds.")
    race_gap = Column(String(20), comment="Gap to race winner.")
    race_gap_millis = Column(Integer, comment="Gap to winner in milliseconds.")
    race_gap_laps = Column(Integer, comment="Number of laps behind leader.")
    race_interval = Column(
        String(20), comment="Time difference to the previous driver."
    )
    race_interval_millis = Column(
        Integer, comment="Interval in milliseconds to previous driver."
    )
    race_reason_retired = Column(
        String(100), comment="Reason for not finishing the race."
    )
    race_points = Column(DECIMAL(8, 2), comment="Championship points awarded.")
    race_pole_position = Column(
        Boolean, comment="True if the driver started from pole."
    )
    race_qualification_position_number = Column(
        Integer, comment="Qualification-based race position (numeric)."
    )
    race_qualification_position_text = Column(
        String(4), comment="Qualification-based race position (text)."
    )
    race_grid_position_number = Column(
        Integer, comment="Final grid start position (numeric)."
    )
    race_grid_position_text = Column(
        String(2), comment="Final grid start position (text)."
    )
    race_positions_gained = Column(
        Integer, comment="Number of positions gained during the race."
    )
    race_pit_stops = Column(Integer, comment="Total number of pit stops made.")
    race_fastest_lap = Column(
        Boolean, comment="True if the driver had the fastest lap."
    )
    race_driver_of_the_day = Column(
        Boolean, comment="True if selected as Driver of the Day."
    )
    race_grand_slam = Column(
        Boolean,
        comment="True if achieved a Grand Slam (pole, win, lead all laps, fastest lap).",
    )

    fastest_lap_lap = Column(Integer, comment="Lap number with fastest lap.")
    fastest_lap_time = Column(String(20), comment="Fastest lap time.")
    fastest_lap_time_millis = Column(
        Integer, comment="Fastest lap time in milliseconds."
    )
    fastest_lap_gap = Column(String(20), comment="Gap to best lap time.")
    fastest_lap_gap_millis = Column(Integer, comment="Gap in milliseconds to best lap.")
    fastest_lap_interval = Column(
        String(20), comment="Interval to previous fastest lap."
    )
    fastest_lap_interval_millis = Column(
        Integer, comment="Interval in milliseconds to previous fastest lap."
    )

    pit_stop_stop = Column(Integer, comment="Pit stop sequence number.")
    pit_stop_lap = Column(Integer, comment="Lap number of pit stop.")
    pit_stop_time = Column(String(20), comment="Pit stop time duration.")
    pit_stop_time_millis = Column(Integer, comment="Pit stop duration in milliseconds.")

    driver_of_the_day_percentage = Column(
        DECIMAL(4, 1), comment="Percentage of votes for Driver of the Day."
    )


class RaceDriverStanding(Base, DWHMixin):
    """Model for the race_driver_standing table."""

    __tablename__ = "race_driver_standing"
    __table_args__ = (
        CheckConstraint(
            "position_display_order >= 1",
            name="check_rds_position_display_order_positive",
        ),
        CheckConstraint("points >= 0", name="check_rds_points_non_negative"),
        CheckConstraint(
            "position_number IS NULL OR position_number >= 1",
            name="check_rds_position_number_positive_or_null",
        ),
        CheckConstraint(
            (
                "(position_text NOT LIKE '%[^0-9]%' AND LEN(position_text) > 0) "
                "OR position_text IN ('DSQ', 'EX')"
            ),
            name="check_rds_position_text_pattern",
        ),
        {"schema": "f1db", "comment": "The driver standings after the race."},
    )

    race_id = Column(
        Integer,
        ForeignKey(Race.id),
        primary_key=True,
        nullable=False,
        comment="ID of the race",
    )
    position_display_order = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Order in which the driver appears in the standings",
    )
    position_number = Column(
        Integer,
        nullable=True,
        index=True,
        comment="Actual position number of the driver (may be null if not applicable)",
    )
    position_text = Column(
        String(4),
        nullable=False,
        index=True,
        comment="Position displayed as text (e.g., 'DNF', 'P1')",
    )
    driver_id = Column(
        String(100),
        ForeignKey(Driver.id),
        nullable=False,
        index=True,
        comment="ID of the driver",
    )
    points = Column(
        DECIMAL(8, 2), nullable=False, comment="Points scored by the driver in the race"
    )
    positions_gained = Column(
        Integer,
        nullable=True,
        comment="Number of positions gained compared to starting grid",
    )


class RaceConstructorStanding(Base, DWHMixin):
    """Model for the race_constructor_standing table."""

    __tablename__ = "race_constructor_standing"
    __table_args__ = (
        CheckConstraint(
            "position_display_order >= 1",
            name="check_rcs_position_display_order_positive",
        ),
        CheckConstraint("points >= 0", name="check_rcs_points_non_negative"),
        CheckConstraint(
            "position_number IS NULL OR position_number >= 1",
            name="check_rcs_position_number_positive_or_null",
        ),
        CheckConstraint(
            (
                "(position_text NOT LIKE '%[^0-9]%' AND LEN(position_text) > 0) "
                "OR position_text IN ('DSQ', 'EX')"
            ),
            name="check_rcs_position_text_pattern",
        ),
        {"schema": "f1db", "comment": "The constructor standings after the race."},
    )

    race_id = Column(
        Integer,
        ForeignKey(Race.id),
        primary_key=True,
        nullable=False,
        comment="ID of the race",
    )
    position_display_order = Column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
        comment="Display order of the constructor in standings",
    )
    position_number = Column(
        Integer, nullable=True, index=True, comment="Numerical finishing position"
    )
    position_text = Column(
        String(4),
        nullable=False,
        index=True,
        comment="Text representation of position (e.g., '1', 'DNF')",
    )
    constructor_id = Column(
        String(100),
        ForeignKey(Constructor.id),
        nullable=False,
        index=True,
        comment="ID of the constructor",
    )
    engine_manufacturer_id = Column(
        String(100),
        ForeignKey(EngineManufacturer.id),
        nullable=False,
        index=True,
        comment="ID of the engine manufacturer",
    )
    points = Column(DECIMAL(8, 2), nullable=False, comment="Points awarded in the race")
    positions_gained = Column(
        Integer, nullable=True, comment="Number of positions gained during the race"
    )


# in proper order to load
TABLES_MAP: Tuple[Tuple[str, DWHMixin]] = (
    (Continent.__tablename__, Continent),
    (Country.__tablename__, Country),
    (Driver.__tablename__, Driver),
    (DriverFamilyRelationship.__tablename__, DriverFamilyRelationship),
    (Constructor.__tablename__, Constructor),
    (ConstructorChronology.__tablename__, ConstructorChronology),
    (Chassis.__tablename__, Chassis),
    (EngineManufacturer.__tablename__, EngineManufacturer),
    (Engine.__tablename__, Engine),
    (TyreManufacturer.__tablename__, TyreManufacturer),
    (Entrant.__tablename__, Entrant),
    (Circuit.__tablename__, Circuit),
    (GrandPrix.__tablename__, GrandPrix),
    (Season.__tablename__, Season),
    (SeasonEntrant.__tablename__, SeasonEntrant),
    (SeasonEntrantConstructor.__tablename__, SeasonEntrantConstructor),
    (SeasonEntrantChassis.__tablename__, SeasonEntrantChassis),
    (SeasonEntrantEngine.__tablename__, SeasonEntrantEngine),
    (SeasonEntrantTyreManufacturer.__tablename__, SeasonEntrantTyreManufacturer),
    (SeasonEntrantDriver.__tablename__, SeasonEntrantDriver),
    (SeasonConstructor.__tablename__, SeasonConstructor),
    (SeasonEngineManufacturer.__tablename__, SeasonEngineManufacturer),
    (SeasonDriver.__tablename__, SeasonDriver),
    (SeasonDriverStanding.__tablename__, SeasonDriverStanding),
    (SeasonConstructorStanding.__tablename__, SeasonConstructorStanding),
    (Race.__tablename__, Race),
    (RaceData.__tablename__, RaceData),
    (RaceDriverStanding.__tablename__, RaceDriverStanding),
    (SeasonTyreManufacturer.__tablename__, SeasonTyreManufacturer),
    (RaceConstructorStanding.__tablename__, RaceConstructorStanding),
)
