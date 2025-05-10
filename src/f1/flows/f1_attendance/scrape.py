"""
Prefect task to scrape circuits data from saved HTML files.
"""

from __future__ import annotations

import os
import sys
from logging import Logger
from typing import TYPE_CHECKING, Any, Dict, List, cast

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag
from prefect import task
from prefect.logging import get_run_logger

from .utils import get_output_dir

# workaround for import issue in prefect
if TYPE_CHECKING:
    pass
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# for simplicity keep entire scraping logic in one function
# pylint: disable=magic-value-comparison
def _scrape_attendance(
    file_path: str, logger: Logger | None = None
) -> List[Dict[str, Any]]:
    """
    Scrape Race Track Weekend Attendance from the provided HTML file.
    Expected data:
        - attendance: dict mapping each year to its attendance figure.

    Args:
        file_path (str): Path to the HTML file containing attendance data.
        logger (Logger, optional): Logger for logging messages.

    Returns:
        Dict[str, Any]: A dictionary with an "attendance" key.

    Raises:
        ScrapeError: If the attendance table or required data is not found.
    """
    if logger:
        logger.debug("Scraping attendance data from: %s", file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, "html.parser")

    data = []
    # Find all year headers (e.g., h2 tags with text like '2024 F1 Attendance Figures')
    for header in soup.find_all(["h2", "h3"]):
        if header.text.strip().endswith("F1 Attendance Figures"):
            year = header.text.strip().split()[0]
            # The next sibling after the header is expected to be the table
            table = header.find_next_sibling("table")
            if table:
                table = cast(Tag, table)

                for row in table.find_all("tr")[1:]:  # Skip header row
                    cells = cast(Tag, row).find_all("td")

                    if len(cells) >= 3:
                        race = cells[0].get_text(strip=True)
                        track = cells[1].get_text(strip=True)
                        attendance = cells[2].get_text(strip=True).replace(",", "")
                        data.append(
                            {
                                "year": year,
                                "race": race,
                                "track": track,
                                "weekend_attendance": int(attendance)
                                if attendance.isdigit()
                                else pd.NA,
                            }
                        )

    return data


@task
def scrape_data_from_f1destinations(attendance_data_path: str) -> str:
    """
    Scrape attendance data from the F1 Destinations website.

    Args:
        attendance_data_path (str): Path to the HTML file containing attendance data.
    Returns:
        str: Path to the CSV file containing the scraped data.
    """
    logger = cast(Logger, get_run_logger())

    # Read the circuit links CSV file
    logger.info("Scraping attendance data...")
    attendance_data = _scrape_attendance(attendance_data_path, logger=logger)

    attendance_df = pd.DataFrame(attendance_data)
    attendance_df_path = os.path.join(get_output_dir(), "attendance_data.csv")
    attendance_df.to_csv(attendance_df_path, index=False, encoding="utf-8")
    logger.info("Scraped data saved to: %s", attendance_df_path)

    return attendance_df_path


if __name__ == "__main__":
    scrape_data_from_f1destinations(
        os.path.join(get_output_dir(), "attendance.html"),
    )
