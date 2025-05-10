"""
Prefect task to scrape circuits data from saved HTML files.
"""

from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from logging import Logger
from typing import Any, Dict, List, Tuple, cast
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag
from prefect import task
from prefect.logging import get_run_logger

from .utils import get_base_url, get_output_dir


class ScrapeError(Exception):
    """
    Custom exception for scraping errors.
    """


def _extract_lat_long(map_src: str) -> Tuple[float, float]:
    """
    Extract latitude and longitude from the Google Maps embed URL.

    Args:
        map_src (str): The src attribute of the Google Maps iframe.

    Returns:
        Tuple[float, float]: A tuple containing latitude and longitude.

    Raises:
        ValueError: If latitude and longitude cannot be extracted.
    """
    map_src = map_src.replace(" ", "")

    lon_match = re.search(r"!2d(-?\d+\.\d+)", map_src)
    lat_match = re.search(r"!3d(-?\d+\.\d+)", map_src)
    lon = float(lon_match.group(1)) if lon_match else None
    lat = float(lat_match.group(1)) if lat_match else None

    if lat is None or lon is None:
        lon_match = re.search(r"lng=(-?\d+\.\d+)", map_src)
        lat_match = re.search(r"lat=(-?\d+\.\d+)", map_src)
        lon = float(lon_match.group(1)) if lon_match else None
        lat = float(lat_match.group(1)) if lat_match else None

    if lat is None or lon is None:
        raise ValueError(
            f"Could not extract latitude and longitude from the map source : {map_src}."
        )
    return lat, lon


# for simplicity keep entire scraping logic in one function
# pylint: disable=too-many-locals
# pylint: disable=magic-value-comparison
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
def _scrape_individual_circuit(
    base_url: str, file_path: str, logger: Logger | None = None
) -> Dict[str, Any]:
    """
    Scrape individual circuit data from the provided HTML file.
    Data includes:
        - overview: text from the overview section
        - history: text from the history section
        - location: address from the circuit info
        - phone: phone number from the circuit info
        - email: contact email (if present)
        - website: website URL (if present)
        - latitude: from the Google Maps iframe URL (if present)
        - longitude: from the Google Maps iframe URL (if present)
        - photos: a list of local paths where photos have been downloaded

    Args:
        base_url (str): The base URL for the circuits website.
        file_path (str): The path to the HTML file containing circuit data.
        logger (Logger, optional): Logger instance for logging messages.

    Returns:
        Dict[str, Any]: A dictionary containing the scraped data.

    Raises:
        ScrapeError: If there is an error while scraping the data.
        ValueError: If any required section is not found in the HTML file.
        TypeError: If the HTML structure is not as expected.
        AttributeError: If an expected attribute is not found in the HTML elements.
        KeyError: If a required key is not found in the dictionary.
    """
    if logger:
        logger.debug("Aggregating data from: %s", file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    data: Dict[str, Any] = {
        "overview": None,
        "history": None,
        "location": None,
        "phone": None,
        "email": None,
        "website": None,
        "latitude": None,
        "longitude": None,
        "maps": [],
        "rating": None,
        "reviews_num": None,
        "tags": [],
    }

    try:
        # Extract overview text using case-insensitive search
        overview_heading = soup.find("h2", string=re.compile("Circuit Overview", re.I))
        if overview_heading:
            overview_text = []

            p = overview_heading.parent
            if p is None:
                raise ValueError("No parent found for the overview heading.")
            pp = p.parent
            if pp is None:
                raise ValueError("No parent found for the overview heading's parent.")

            for sibling in pp.find_next_siblings():
                if not hasattr(sibling, "name"):
                    raise ValueError("Sibling does not have a name attribute.")

                if sibling.name and sibling.name.startswith("h"):
                    break
                if sibling.name == "p":
                    overview_text.append(sibling.get_text(" ", strip=True))
            data["overview"] = " ".join(overview_text).strip()
        else:
            raise ValueError("No overview section found.")

        # Extract history from the section with id "history"
        history_section = soup.find("section", id="history")
        if history_section:
            history_segments_raw: Dict[str, List[str]] = {}
            # Start with the intro paragraphs before any h3
            current_key = "Intro"
            history_segments_raw[current_key] = []
            for child in cast(Tag, history_section).find_all(recursive=False):
                if not isinstance(child, Tag):
                    continue
                if child.name == "h3":
                    # Use the h3 tag text as the key
                    current_key = child.get_text(strip=True)
                    history_segments_raw[current_key] = []
                elif child.name == "p":
                    history_segments_raw[current_key].append(
                        child.get_text(" ", strip=True)
                    )
            # Merge paragraphs in each segment
            history_segments: Dict[str, str] = {}
            for key, val in history_segments_raw.items():
                history_segments[key] = " ".join(val).strip()
            data["history"] = history_segments
        else:
            raise ValueError("No history section found.")

        # Extract location, phone and email from the "Circuit info" section (using the dl element)
        info_section = soup.find("dl")
        if info_section:
            dt_tags = cast(Tag, info_section).find_all("dt")
            dd_tags = cast(Tag, info_section).find_all("dd")

            for dt, dd in zip(dt_tags, dd_tags):
                dt = cast(Tag, dt)
                dd = cast(Tag, dd)

                i_tag = cast(Tag, dt.find("i"))
                if not i_tag:
                    continue

                classes = i_tag.get("class")
                if classes:
                    if "fa-map-marker-alt" in classes:
                        data["location"] = dd.get_text(" ", strip=True)
                    elif "fa-phone" in classes:
                        data["phone"] = dd.get_text(" ", strip=True)
                    elif "fa-envelope" in classes:
                        a_tag = cast(Tag, dd.find("a"))
                        if a_tag:
                            data["email"] = (
                                str(a_tag.get("href")).replace("mailto:", "").strip()
                            )
                    elif "fa-globe-americas" in classes:
                        a_tag = cast(Tag, dd.find("a"))
                        if a_tag:
                            data["website"] = str(a_tag.get("href")).strip()

                # Not all pages have all the info, so we log warnings if any are missing
                if not data["location"] and logger:
                    logger.warning(
                        "No location found in the circuit info for %s", file_path
                    )
                if not data["phone"] and logger:
                    logger.warning(
                        "No phone number found in the circuit info for %s", file_path
                    )
                if not data["email"] and logger:
                    logger.warning(
                        "No email found in the circuit info for %s", file_path
                    )
                if not data["website"] and logger:
                    logger.warning(
                        "No website found in the circuit info for %s", file_path
                    )

        # Extract latitude & longitude from the Google Map iframe
        map_iframe = soup.find(
            "iframe", src=re.compile(r"(google\.com/maps/embed|www\.stay22\.com)")
        )
        if map_iframe:
            map_src = str(cast(Tag, map_iframe).get("src"))
            lat, lon = _extract_lat_long(map_src)
            data["latitude"] = lat
            data["longitude"] = lon
        else:
            raise ValueError("No Google Maps iframe found.")

        # Extract maps data from the section with id "maps"
        map_entries = []
        maps_section = cast(Tag, soup.find("section", id="maps"))
        if maps_section:
            list_ul = cast(Tag, maps_section.find("ul"))
            if list_ul:
                anchors = list_ul.find_all(
                    "a", class_="nav-link", attrs={"role": "tab"}
                )
                for a in anchors:
                    a = cast(Tag, a)

                    entry: Dict[str, str | None] = {}
                    # Get the text from the list item (you may modify the separator as needed)
                    entry["title"] = a.get_text(separator=" ", strip=True)
                    # Get the target id from the anchor's href (e.g. "#map_2003todate_1")
                    target_id = a.get("href")
                    if target_id:
                        # Remove the '#' prefix
                        target_id = str(target_id).lstrip("#")
                        # Find the corresponding div by id.
                        toggled_div = cast(Tag, maps_section.find(id=target_id))
                        if toggled_div:
                            inner_anchors = toggled_div.find_all("a", href=True)

                            for inner_a in inner_anchors:
                                inner_a = cast(Tag, inner_a)

                                if inner_a.strong:
                                    entry["subtitle"] = inner_a.strong.get_text(
                                        strip=True
                                    )
                                else:
                                    raise ValueError(
                                        f"No strong tag found in the inner anchor: {inner_a}"
                                    )

                                if inner_a.small:
                                    entry["distance"] = inner_a.small.get_text(
                                        strip=True
                                    )
                                else:
                                    raise ValueError(
                                        f"No small tag found in the inner anchor: {inner_a}",
                                    )

                                sub_target_id = inner_a.get("href")
                                if sub_target_id:
                                    # Remove the '#' prefix
                                    sub_target_id = str(sub_target_id).lstrip("#")
                                    # Find the corresponding div by id.
                                    sub_toggled_div = maps_section.find(
                                        id=sub_target_id
                                    )
                                    if sub_toggled_div:
                                        toggled_div_img = cast(
                                            Tag, sub_toggled_div
                                        ).find("img")
                                        if toggled_div_img:
                                            toggled_div_img = cast(Tag, toggled_div_img)
                                            entry["img_src"] = str(
                                                toggled_div_img.get("src")
                                            )
                                            entry["img_alt"] = str(
                                                toggled_div_img.get("alt")
                                            )
                                            entry["absolute_img_src"] = (
                                                urljoin(base_url, entry["img_src"])
                                                if entry["img_src"]
                                                else None
                                            )
                                            map_entries.append(deepcopy(entry))
                                        else:
                                            raise ValueError(
                                                "No img tag found in the "
                                                f"sub-toggled div: {sub_toggled_div}",
                                            )
                                    else:
                                        raise ValueError(
                                            f"Sub-toggled div with id '{sub_target_id}' not found",
                                        )
                                else:
                                    raise ValueError(
                                        f"Sub-target id not found in the inner anchor: {inner_a}",
                                    )
                        else:
                            raise ValueError(
                                f"Toggled div with id '{target_id}' not found",
                            )
                    else:
                        raise ValueError(f"Target id not found in the anchor: {a}")
            else:
                raise ValueError("No list found in the maps section")
        else:
            raise ValueError("No maps section found")
        data["maps"] = map_entries

        # Extract rating and number of reviews from the "Rate This Circuit" section
        rating_section = soup.find(
            lambda tag: tag.name == "h3"
            and "rate this circuit" in tag.get_text(strip=True).lower()
        )
        if rating_section:
            # Find the rating list (assumed to have class similar to "star-rating-default")
            rating_list = rating_section.find_next(
                "ul", class_=re.compile("star-rating-default", re.I)
            )
            if rating_list:
                current_rating_li = cast(Tag, rating_list).find(
                    "li", class_="current-rating"
                )
                if current_rating_li:
                    # You may convert this to a float/int as needed
                    data["rating"] = current_rating_li.get_text(strip=True)
                else:
                    raise ValueError("No current rating found in the rating list")
            else:
                raise ValueError(
                    "No rating list found in the 'Rate This Circuit' section"
                )

            # Find the reviews span; expected format "Votes: 7689" or similar
            reviews_span = rating_section.find_next(
                "span", class_=re.compile("totalvotes", re.I)
            )
            if reviews_span:
                reviews_text = reviews_span.get_text(strip=True)
                match = re.search(r"(\d+)", reviews_text)
                data["reviews_num"] = int(match.group(1)) if match else None
            else:
                raise ValueError(
                    "No reviews span found in the 'Rate This Circuit' section"
                )
        else:
            raise ValueError("No rating section found")

        # Extract tags from the page
        chips = soup.select("div.chip a")
        data["tags"] = [chip.get_text(strip=True) for chip in chips]
    except ValueError as e:
        raise ScrapeError(f"Error while scraping {file_path}") from e

    return data


@task
def scrape_data_from_circuits(circuits_meta_df_path: str) -> str:
    """
    Scrape circuits data from saved HTML files and save them to a CSV file.

    Args:
        circuits_meta_df_path (str): Path to the CSV file containing circuit metadata.
    Returns:
        str: Path to the CSV file containing the scraped data.
    """
    logger = cast(Logger, get_run_logger())
    base_url = get_base_url()

    # Read the circuit links CSV file
    logger.info("Reading circuit links from: %s...", circuits_meta_df_path)
    circuit_meta_df = pd.read_csv(circuits_meta_df_path)
    # scrape individual circuit data
    logger.info("Scraping individual circuit data...")
    circuits_data = []
    with ThreadPoolExecutor() as executor:
        circuits_data = list(
            executor.map(
                lambda row: {
                    **_scrape_individual_circuit(
                        base_url, row["file_path"], logger=logger
                    ),
                    "circuit_name": row["Circuit Name"],
                    "url": row["URL"],
                },
                circuit_meta_df.to_dict("records"),
            )
        )

    # Save the scraped data to a CSV file
    logger.info("Completed scraping individual circuit data (%d)", len(circuits_data))

    circuits_df = pd.DataFrame(circuits_data)
    circuits_df_path = os.path.join(get_output_dir(), "circuit_data.csv")
    circuits_df.to_csv(circuits_df_path, index=False, encoding="utf-8")
    logger.info("Scraped data saved to: %s", circuits_df_path)

    return circuits_df_path


if __name__ == "__main__":
    scrape_data_from_circuits(
        os.path.join(get_output_dir(), "circuits_meta.csv"),
    )
