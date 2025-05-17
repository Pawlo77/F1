"""dim_circuit model for the data warehouse."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)

from .base import Base, DWHMixin
from .dim_country import DimCountry


# pylint: disable=too-few-public-methods, duplicate-code
class DimCircuit(Base, DWHMixin):
    """Model for the circuit dimension table in the data warehouse."""

    __tablename__ = "dim_circuit"
    __table_args__ = (
        {"schema": "DWH", "comment": "Source tables: f1.country, f1.continent"},
    )

    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country. From f1db.circuit.",
    )

    circuit_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The name of the circuit. From f1db.circuit.",
    )
    circuit_full_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The full name of the circuit. From f1db.circuit.",
    )

    circuit_type = Column(
        String(6),
        nullable=False,
        index=True,
        comment="Type of the circuit. From f1db.circuit.",
    )
    circuit_direction = Column(
        String(14),
        nullable=False,
        index=True,
        comment="The direction for the circuit. From f1db.circuit.",
    )
    circuit_place_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="The place name of the circuit. From f1db.circuit.",
    )
    circuit_latitude = Column(
        Numeric(10, 6),
        nullable=False,
        comment="The latitude coordinate of the circuit. From f1db.circuit.",
    )
    circuit_longitude = Column(
        Numeric(10, 6),
        nullable=False,
        comment="The longitude coordinate of the circuit. From f1db.circuit.",
    )
    circuit_length = Column(
        Numeric(6, 3),
        nullable=False,
        comment="The length of the circuit. From f1db.circuit.",
    )

    circuit_rating = Column(
        Float,
        nullable=True,
        comment="Rating of the circuit. From web.circuits_details.",
    )
    circuit_reviews_num = Column(
        Integer, nullable=False, comment="Number of reviews. From web.circuits_details."
    )
    circuit_website = Column(
        String(510),
        nullable=True,
        comment="Website of the circuit. From web.circuits_details.",
    )
