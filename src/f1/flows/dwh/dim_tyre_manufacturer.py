"""dim_tyre_manufacturer model for the data warehouse."""

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
class DimTyreManufacturer(Base, DWHMixin):
    """Model for the tyre manufacturer dimension table in the data warehouse."""

    __tablename__ = "dim_tyre_manufacturer"
    __table_args__ = (
        {
            "schema": "DWH",
            "comment": "Source tables: f1db.tyre_manufacturer. Business key is tyre_manufacturer_name.",
        },
    )

    tyre_manufacturer_name = Column(
        String(100),
        nullable=False,
        comment="The name of the tyre manufacturer. From f1db.tyre_manufacturer. Can't be modified on source.",
        index=True,
    )
    country_id = Column(
        BigInteger,
        ForeignKey(DimCountry.dwh_id),
        nullable=False,
        comment="Foreign key to dim_country. Can't be modified on source.",
        index=True,
    )
