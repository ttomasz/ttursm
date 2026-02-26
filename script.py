# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx>=0.28.1",
#     "osm2geojson>=0.3.1",
#     "retryhttp[httpx]>=1.4.0",
# ]
# [tool.uv]
# exclude-newer = "2026-02-22T00:00:00Z"
# ///

from collections import defaultdict
from datetime import datetime
import json
import time
from typing import Literal, TypedDict, cast, DefaultDict

import httpx
from retryhttp import retry
import osm2geojson


HTTPX_TIMEOUT = httpx.Timeout(90.0)

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OVERPASS_SEARCH_AREA = """area["boundary"="administrative"]["admin_level"="9"]["teryt:terc"~"1465"]["name"="Ursus"](20.804329,52.156874,20.971184,52.239785)"""
OVERPASS_QUERY_PARKING = f"""
[out:json][timeout:90];
{OVERPASS_SEARCH_AREA}->.searchArea;
nwr["amenity"="parking"](area.searchArea);
out geom;
"""
OVERPASS_QUERY_PARKING_SPACES = f"""
[out:json][timeout:90];
{OVERPASS_SEARCH_AREA}->.searchArea;
way["amenity"="parking_space"](area.searchArea);
out skel geom;
"""
OVERPASS_QUERY_POI = f"""
[out:json][timeout:90];
{OVERPASS_SEARCH_AREA}->.searchArea;
(
  nwr[shop](area.searchArea);
  nwr[amenity~"bar|cafe|fast_food|ice_cream|pub|restaurant|veterinary|pharmacy|dentist"](area.searchArea);
);
out center;
"""
OVERPASS_QUERY_POI_OUT_LINES = f"""
[out:json][timeout:90];
{OVERPASS_SEARCH_AREA}->.searchArea;
(
  wr[shop](area.searchArea);
  wr[amenity~"bar|cafe|fast_food|ice_cream|pub|restaurant|veterinary|pharmacy|dentist"](area.searchArea);
);
out skel geom;
"""

CATEGORY_TYPE = Literal[
    "medyczne",
    "gastronomia",
    "sklep",
    "usluga",
    "pusty",
    None,
]
SUBCATEGORY_TYPE = Literal[
    "dentysta",
    "weterynarz",
    "optyk",
    "apteka",
    "piekarnia_cukiernia",
    "drogeria",
    "odziez_obuwie",
    "dzieciecy",
    "market",
    "osiedlowy",
    "warzywniak",
    "rzeznik",
    "kwiaciarnia",
    "monopolowy",
    "sklepy_pozostale",
    "beauty",
    "mechanik",
    "krawiec_szewc",
    "uslugi_pozostale",
    "optyk",
    "dentysta",
    "weterynarz",
    "ch",
    "fryzjer",
    None,
]


class Summary(TypedDict):
    download_dt: str
    ground_parking_capacity: int
    ground_parking_capacity_for_disabled: int
    shops: int
    services: int
    med: int
    vacant: int
    food: int
    uncategorized: int
    uncategorized_ids: list[str]
    poi_subcategories: DefaultDict


def flatten_properties(properties: dict) -> None:
    if "nodes" in properties:
        del properties["nodes"]
    properties["@type"] = properties["type"]
    del properties["type"]
    properties["@id"] = properties["id"]
    del properties["id"]
    for k, v in properties["tags"].items():
        properties[k] = v
    del properties["tags"]
    properties["@url"] = f"https://osm.org/{properties['@type']}/{properties['@id']}"


def classify(properties: dict) -> None:
    category: CATEGORY_TYPE = None
    subcategory: SUBCATEGORY_TYPE = None
    match properties.get("amenity"):
        case None:
            pass
        case "bar":
            category = "gastronomia"
        case "cafe":
            category = "gastronomia"
        case "fast_food":
            category = "gastronomia"
        case "ice_cream":
            category = "gastronomia"
        case "pub":
            category = "gastronomia"
        case "restaurant":
            category = "gastronomia"
        case "bar":
            category = "gastronomia"
        case "pharmacy":
            category = "medyczne"
            subcategory = "apteka"
        case "veterinary":
            category = "medyczne"
            subcategory = "weterynarz"
        case "dentist":
            category = "medyczne"
            subcategory = "dentysta"
    match properties.get("shop"):
        case None:
            pass
        case "vacant":
            category = "pusty"
        case "alcohol" | "wine":
            category = "sklep"
            subcategory = "monopolowy"
        case "bakery" | "pastry":
            category = "sklep"
            subcategory = "piekarnia_cukiernia"
        case "butcher":
            category = "sklep"
            subcategory = "rzeznik"
        case "chemist" | "cosmetics":
            category = "sklep"
            subcategory = "drogeria"
        case "clothes" | "shoes":
            category = "sklep"
            subcategory = "odziez_obuwie"
        case "baby_goods" | "toys":
            category = "sklep"
            subcategory = "dzieciecy"
        case "supermarket" | "department_store":
            category = "sklep"
            subcategory = "market"
        case "convenience":
            category = "sklep"
            subcategory = "osiedlowy"
        case "greengrocer":
            category = "sklep"
            subcategory = "warzywniak"
        case "florist":
            category = "sklep"
            subcategory = "kwiaciarnia"
        case "mall":
            category = "sklep"
            subcategory = "ch"
        case (
            "antiques" | "appliance" | "bag" | "bicycle" | "books" |
            "business_machines" | "car" | "car_parts" | "chocolate" |
            "coffee" | "confectionery" | "deli" | "doityourself" | "e-cigarette" |
            "electronics" | "farm" | "fashion_accessories" | "frozen_food" | "furniture" |
            "furniture_parts" | "games" | "garden_centre" | "gas" | "general" |
            "gift" | "hairdresser_supply" | "hardware" | "health_food" | "herbalist" |
            "household_linen" | "houseware" | "interior_decoration" | "jewelry" | "kiosk" |
            "kitchen" | "medical_supply" | "mobile_phone" | "newsagent" | "outdoor" |
            "paint" | "party" | "pawnbroker" | "perfumery" | "pet" |
            "printer_ink" | "seafood" | "sewing" | "sports" | "stationery" |
            "tea" | "tobacco" | "tyres" | "variety_store" | "video_games" |
            "watches"
        ):
            category = "sklep"
            subcategory = "sklepy_pozostale"
        case "beauty":
            category = "usluga"
            subcategory = "beauty"
        case "hairdresser":
            category = "usluga"
            subcategory = "fryzjer"
        case "car_repair":
            category = "usluga"
            subcategory = "mechanik"
        case "tailor" | "shoe_repair":
            category = "usluga"
            subcategory = "krawiec_szewc"
        case (
            "bookmaker" | "copyshop" | "dry_cleaning" | "locksmith" | "lottery" |
            "laundry" | "pet_grooming" | "repair" | "tool_hire" | "travel_agency" |
            "massage" | "tattoo"
        ):
            category = "usluga"
            subcategory = "uslugi_pozostale"
        case "optician":
            category = "medyczne"
            subcategory = "optyk"
    properties["@kategoria"] = category
    properties["@podkategoria"] = subcategory


def prepare_summary(geojson_poi: dict, download_dt: datetime) -> Summary:
    result = Summary(
        download_dt=download_dt.isoformat(sep=" ", timespec="minutes"),
        ground_parking_capacity=0,
        ground_parking_capacity_for_disabled=0,
        shops=0,
        services=0,
        med=0,
        vacant=0,
        food=0,
        uncategorized=0,
        uncategorized_ids=[],
        poi_subcategories=defaultdict(int)
    )
    for feature in geojson_poi["features"]:
        properties = feature["properties"]
        kategoria = cast(CATEGORY_TYPE, properties["@kategoria"])
        match kategoria:
            case "gastronomia":
                result["food"] += 1
            case "medyczne":
                result["med"] += 1
            case "pusty":
                result["vacant"] += 1
            case "sklep":
                result["shops"] += 1
            case "usluga":
                result["services"] += 1
            case _:
                result["uncategorized"] += 1
                result["uncategorized_ids"].append(f"{properties['@type']}/{properties['@id']}")
        podkategoria = cast(SUBCATEGORY_TYPE, properties["@podkategoria"])
        if podkategoria:
            result["poi_subcategories"][podkategoria] += 1
    return result


@retry
def get_parking(overpass_url: str) -> dict:
    response = httpx.post(url=overpass_url, data={"data": OVERPASS_QUERY_PARKING}, timeout=HTTPX_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    geojson = osm2geojson.json2geojson(data=data, raise_on_failure=True, filter_used_refs=True)
    for feature in geojson["features"]:
        p = feature["properties"]
        flatten_properties(p)
    return geojson


@retry
def get_parking_spaces(overpass_url: str) -> dict:
    response = httpx.post(url=overpass_url, data={"data": OVERPASS_QUERY_PARKING_SPACES}, timeout=HTTPX_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    geojson = osm2geojson.json2geojson(data=data, raise_on_failure=True, filter_used_refs=True)
    return geojson


@retry
def get_poi_outlines(overpass_url: str) -> dict:
    response_outlines = httpx.post(url=overpass_url, data={"data": OVERPASS_QUERY_POI_OUT_LINES}, timeout=HTTPX_TIMEOUT)
    response_outlines.raise_for_status()
    data_outlines = response_outlines.json()
    geojson_outlines = osm2geojson.json2geojson(data=data_outlines, raise_on_failure=True, filter_used_refs=True)
    return geojson_outlines


@retry
def get_poi(overpass_url: str) -> dict:
    response_points = httpx.post(url=overpass_url, data={"data": OVERPASS_QUERY_POI}, timeout=HTTPX_TIMEOUT)
    response_points.raise_for_status()
    data_points = response_points.json()
    geojson_points = osm2geojson.json2geojson(data=data_points, raise_on_failure=True, filter_used_refs=True)
    for feature in geojson_points["features"]:
        p = feature["properties"]
        flatten_properties(p)
        classify(p)
    return geojson_points


def main() -> None:
    print("Hello from script.py!")
    start_dt = datetime.now()
    # ---
    geojson_parking = get_parking(overpass_url=OVERPASS_URL)
    num_parking = len(geojson_parking["features"])
    print(f"amenity=parking elements: {num_parking}")
    if num_parking > 0:
        with open("web/data/parking.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_parking, fp=f)
    time.sleep(2.0)
    # ---
    geojson_parking_spaces = get_parking_spaces(overpass_url=OVERPASS_URL)
    num_parking_spaces = len(geojson_parking_spaces["features"])
    print(f"amenity=parking_space elements: {num_parking_spaces}")
    if num_parking_spaces > 0:
        with open("web/data/parking_spaces.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_parking_spaces, fp=f)
    time.sleep(2.0)
    # ---
    geojson_poi = get_poi(overpass_url=OVERPASS_URL)
    num_shops_and_food_points = len(geojson_poi["features"])
    print(f"shops and food point elements: {num_shops_and_food_points}")
    if num_shops_and_food_points > 0:
        with open("web/data/shops_and_food_points.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_poi, fp=f)
    summary = prepare_summary(geojson_poi=geojson_poi, download_dt=start_dt)
    with open("web/data/summary.json", "w", encoding="utf-8") as f:
        json.dump(obj=summary, fp=f, indent=2)
    time.sleep(2.0)
    # ---
    geojson_poi_outlines = get_poi_outlines(overpass_url=OVERPASS_URL)
    num_shops_and_food_outlines = len(geojson_poi_outlines["features"])
    print(f"shops and food outline elements: {num_shops_and_food_outlines}")
    if num_shops_and_food_outlines > 0:
        with open("web/data/shops_and_food_polygons.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_poi_outlines, fp=f)
    # ---
    print("Done.")


if __name__ == "__main__":
    main()
