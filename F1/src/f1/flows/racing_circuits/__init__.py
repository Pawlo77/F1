"""Racing circuits webpage ETL flow."""

from __future__ import annotations

import os

from prefect.variables import Variable

# Define output directories
OUTPUT_DIR_PATH: str = os.path.join(
    str(Variable.get("output_dir", default="output")),
    os.path.basename(os.path.dirname(os.path.abspath(__file__))),
)
CIRCUIT_DIR_PATH: str = os.path.join(OUTPUT_DIR_PATH, "circuits")
os.makedirs(OUTPUT_DIR_PATH, exist_ok=True)
os.makedirs(CIRCUIT_DIR_PATH, exist_ok=True)

BASE_URL = str(
    Variable.get("circuits_base_url", default="https://www.racingcircuits.info")
)
