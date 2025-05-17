# Util files are very simmilar
# pylint: disable=duplicate-code

"""Utility functions for the f1db flow."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import TYPE_CHECKING

from prefect.variables import Variable

# workaround for import issue in prefect
if TYPE_CHECKING:
    pass
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


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
def get_extraction_dir() -> str:
    """Get the directory for extracting zip files."""
    path = os.path.join(get_output_dir(), "data")
    os.makedirs(path, exist_ok=True)
    return path
