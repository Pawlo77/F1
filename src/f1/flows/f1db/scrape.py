"""
Prefect task to scrape f1db data from the SQL file.
"""

from __future__ import annotations

import os
import re
import sys
from logging import Logger
from typing import TYPE_CHECKING, Any, Dict, List, cast

import pandas as pd
from prefect import task
from prefect.logging import get_run_logger

from .utils import get_extraction_dir, get_output_dir

# workaround for import issue in prefect
if TYPE_CHECKING:
    pass
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _parse_insert_statements(statements: List[str]) -> Dict[str, List[pd.DataFrame]]:
    """
    Parse INSERT statements from SQL file and return a dictionary of DataFrames.

    Args:
        statements (List[str]): List of SQL INSERT statements to parse.

    Returns:
        Dict[str, List[pd.DataFrame]]: Dictionary where keys are
            table names and values are lists of DataFrames.
    """
    dfs: Dict[str, List[pd.DataFrame]] = {}

    for stmt in statements:
        match = re.search(
            r"INSERT INTO\s+`?(\w+)`?\s+\((.*?)\)\s+VALUES\s+(.*)",
            stmt,
            flags=re.DOTALL,
        )
        if not match:
            continue

        table, columns_str, values_block = match.groups()
        values_block = values_block.strip().rstrip(";")  # clean end semicolon
        columns = [col.strip(" `") for col in columns_str.split(",")]

        # Extract all tuples of values while respecting quoted strings
        value_tuples = re.findall(r"\((?:[^()']+|'(?:\\'|[^'])*')+\)", values_block)

        rows = []
        for val in value_tuples:
            parts: List[Any] = []
            for x in re.split(r",\s*(?=(?:[^']*'[^']*')*[^']*$)", val.strip("()")):
                x = x.strip()
                if x.upper() == "NULL" or x == "":  # pylint: disable=magic-value-comparison
                    parts.append(None)
                elif x.startswith("'") and x.endswith("'"):
                    parts.append(x[1:-1].replace("\\'", "'").replace("''", "'"))
                elif re.match(r"^-?\d+\.\d+$", x):
                    parts.append(float(x))
                elif re.match(r"^-?\d+$", x):
                    parts.append(int(x))
                else:
                    parts.append(x)

            # data issue
            if parts == ["bar-007", "bar", "006", "BAR 006"]:
                parts = ["bar-007", "bar", "007", "BAR 007"]
            rows.append(parts)

        df = pd.DataFrame(rows, columns=columns)

        if table not in dfs:
            dfs[table] = []
        dfs[table].append(df)

    return dfs


@task
def scrape_data_from_f1db(sql_file_path: str) -> str:
    """
    Scrape f1db data from sql file.

    Args:
        sql_file_path (str): Path to the SQL file containing data.
    Returns:
        str: Path to directory containing scraped data in csv format.
    """
    logger = cast(Logger, get_run_logger())
    extraction_dir = get_extraction_dir()

    # Read the SQL file
    with open(sql_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    statements = [
        line.strip() for line in lines if line.strip().startswith("INSERT INTO")
    ]

    data = _parse_insert_statements(statements)
    logger.info("Parsed data from SQL file into DataFrames...")

    # Save the scraped data to a CSV file
    saved_files_num = 0
    for table, dfs in data.items():
        for i, df in enumerate(dfs):
            filename = os.path.join(extraction_dir, f"{table}_{i}.csv")
            df.to_csv(filename, index=False)
            saved_files_num += 1
    logger.info("Saved %d CSV files...", saved_files_num)

    return extraction_dir


if __name__ == "__main__":
    scrape_data_from_f1db(
        os.path.join(get_output_dir(), "f1db-sql-sqlite-single-inserts.sql"),
    )
