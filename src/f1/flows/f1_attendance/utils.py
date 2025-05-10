"""Utility functions for the racing circuits flow."""

from __future__ import annotations

import os
from functools import lru_cache

from prefect.variables import Variable


@lru_cache(maxsize=1)
def get_output_dir() -> str:
    """Get the output directory for the flow."""
    path = os.path.join(
        str(Variable.get("output_dir", default="output")),
        os.path.basename(os.path.dirname(os.path.abspath(__file__))),
    )
    os.makedirs(path, exist_ok=True)
    return path


@lru_cache(maxsize=1)
def get_circuit_dir() -> str:
    """Get the directory for circuit HTML files."""
    path = os.path.join(get_output_dir(), "circuits")
    os.makedirs(path, exist_ok=True)
    return path


@lru_cache(maxsize=1)
def get_base_url() -> str:
    """Get the base URL for the circuits website."""
    return str(
        Variable.get(
            "attendance_base_url",
            default="https://f1destinations.com/resources/f1-attendance-figures/",
        )
    )
