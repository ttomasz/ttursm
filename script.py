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
OVERPASS_QUERY_SHOPS_AND_FOOD = f"""
[out:json][timeout:90];
{OVERPASS_SEARCH_AREA}->.searchArea;
(
  nwr[shop](area.searchArea);
  nwr[amenity~"bar|cafe|fast_food|ice_cream|pub|restaurant"](area.searchArea);
);
out geom;
"""


def flatten_properties(p: dict) -> None:
    if "nodes" in p:
        del p["nodes"]
    p["@type"] = p["type"]
    del p["type"]
    p["@id"] = p["id"]
    del p["id"]
    for k, v in p["tags"].items():
        p[k] = v
    del p["tags"]
    p["@url"] = f"https://osm.org/{p['@type']}/{p['@id']}"


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
def get_shops_and_food(overpass_url: str) -> dict:
    response = httpx.post(url=overpass_url, data={"data": OVERPASS_QUERY_SHOPS_AND_FOOD}, timeout=HTTPX_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    geojson = osm2geojson.json2geojson(data=data, raise_on_failure=True, filter_used_refs=True)
    for feature in geojson["features"]:
        p = feature["properties"]
        flatten_properties(p)
    return geojson


def main() -> None:
    print("Hello from script.py!")
    # ---
    # geojson_parking = get_parking(overpass_url=OVERPASS_URL)
    # num_parking = len(geojson_parking["features"])
    # print(f"amenity=parking elements: {num_parking}")
    # if num_parking > 0:
    #     with open("web/parking.geojson", "w", encoding="utf-8") as f:
    #         json.dump(obj=geojson_parking, fp=f)
    # time.sleep(1.0)
    # # ---
    # geojson_parking_spaces = get_parking_spaces(overpass_url=OVERPASS_URL)
    # num_parking_spaces = len(geojson_parking_spaces["features"])
    # print(f"amenity=parking_space elements: {num_parking_spaces}")
    # if num_parking_spaces > 0:
    #     with open("web/parking_spaces.geojson", "w", encoding="utf-8") as f:
    #         json.dump(obj=geojson_parking_spaces, fp=f)
    # time.sleep(1.0)
    # ---
    geojson_shops_and_food = get_shops_and_food(overpass_url=OVERPASS_URL)
    num_shops_and_food = len(geojson_shops_and_food["features"])
    print(f"shops and food elements: {num_shops_and_food}")
    if num_shops_and_food > 0:
        with open("web/shops_and_food.geojson", "w", encoding="utf-8") as f:
            json.dump(obj=geojson_shops_and_food, fp=f)
    time.sleep(1.0)
    # ---
    print("Done.")


if __name__ == "__main__":
    main()
