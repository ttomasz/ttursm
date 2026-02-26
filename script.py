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

import json
import time

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
out geom;
"""
OVERPASS_QUERY_SHOPS_AND_FOOD_POINTS = f"""
[out:json][timeout:90];
{OVERPASS_SEARCH_AREA}->.searchArea;
(
  nwr[shop](area.searchArea);
  nwr[amenity~"bar|cafe|fast_food|ice_cream|pub|restaurant"](area.searchArea);
);
out center;
"""
OVERPASS_QUERY_SHOPS_AND_FOOD_OUTLINES = f"""
[out:json][timeout:90];
{OVERPASS_SEARCH_AREA}->.searchArea;
(
  wr[shop](area.searchArea);
  wr[amenity~"bar|cafe|fast_food|ice_cream|pub|restaurant"](area.searchArea);
);
out skel geom;
"""


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
    for feature in geojson["features"]:
        p = feature["properties"]
        flatten_properties(p)
    return geojson


@retry
def get_shops_and_food_outlines(overpass_url: str) -> dict:
    response_outlines = httpx.post(url=overpass_url, data={"data": OVERPASS_QUERY_SHOPS_AND_FOOD_OUTLINES}, timeout=HTTPX_TIMEOUT)
    response_outlines.raise_for_status()
    data_outlines = response_outlines.json()
    geojson_outlines = osm2geojson.json2geojson(data=data_outlines, raise_on_failure=True, filter_used_refs=True)
    return geojson_outlines


@retry
def get_shops_and_food_points(overpass_url: str) -> dict:
    response_points = httpx.post(url=overpass_url, data={"data": OVERPASS_QUERY_SHOPS_AND_FOOD_POINTS}, timeout=HTTPX_TIMEOUT)
    response_points.raise_for_status()
    data_points = response_points.json()
    geojson_points = osm2geojson.json2geojson(data=data_points, raise_on_failure=True, filter_used_refs=True)
    for feature in geojson_points["features"]:
        p = feature["properties"]
        flatten_properties(p)
    return geojson_points


def main() -> None:
    print("Hello from script.py!")
    # ---
    geojson_parking = get_parking(overpass_url=OVERPASS_URL)
    num_parking = len(geojson_parking["features"])
    print(f"amenity=parking elements: {num_parking}")
    if num_parking > 0:
        with open("web/data/parking.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_parking, fp=f)
    time.sleep(1.0)
    # ---
    geojson_parking_spaces = get_parking_spaces(overpass_url=OVERPASS_URL)
    num_parking_spaces = len(geojson_parking_spaces["features"])
    print(f"amenity=parking_space elements: {num_parking_spaces}")
    if num_parking_spaces > 0:
        with open("web/data/parking_spaces.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_parking_spaces, fp=f)
    time.sleep(1.0)
    # ---
    geojson_shops_and_food_points = get_shops_and_food_points(overpass_url=OVERPASS_URL)
    num_shops_and_food_points = len(geojson_shops_and_food_points["features"])
    print(f"shops and food point elements: {num_shops_and_food_points}")
    if num_shops_and_food_points > 0:
        with open("web/data/shops_and_food_points.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_shops_and_food_points, fp=f)
    time.sleep(1.0)
    # ---
    geojson_shops_and_food_outlines = get_shops_and_food_outlines(overpass_url=OVERPASS_URL)
    num_shops_and_food_outlines = len(geojson_shops_and_food_outlines["features"])
    print(f"shops and food outline elements: {num_shops_and_food_outlines}")
    if num_shops_and_food_outlines > 0:
        with open("web/data/shops_and_food_polygons.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_shops_and_food_outlines, fp=f)
    # ---
    print("Done.")


if __name__ == "__main__":
    main()
