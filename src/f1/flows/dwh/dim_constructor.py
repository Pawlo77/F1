"""dim_constructor model for the data warehouse."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    String,
)

from .base import DWHMixin
from .dim_country import DimCountry

# workaround for import issue in prefect
if TYPE_CHECKING:
    from ..flows_utils import Base
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from flows_utils import Base


# pylint: disable=too-few-public-methods, duplicate-code
class DimConstructor(Base, DWHMixin):
    """Model for the constructor dimension table in the data warehouse."""

    __tablename__ = "dim_constructor"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": "Source tables: f1db.construct. Business key is constructor_name.",
        },
    )

    constructor_name = Column(
        String(100),
        nullable=False,
        comment="Short name of the constructor. From f1db.construct. Can't be modified on source.",
        index=True,
    )
    constructor_full_name = Column(
        String(100),
        nullable=False,
        comment="Full official name of the constructor. From f1db.construct. Can be modified on source.",
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        index=True,
        comment="Foreign key to dim_country. Can be modified on source.",
    )
