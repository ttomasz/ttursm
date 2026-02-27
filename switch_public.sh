#!/usr/bin/env bash

set -e

sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/index.html
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/style.css
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/site.js
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/osm.json
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/aerial.json
