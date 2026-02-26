#!/usr/bin/env bash

set -e

sed -i 's/https:\/\/ttomasz\.github\.io\/ttursm/http:\/\/localhost:8000\/web/g' ./web/index.html
sed -i 's/https:\/\/ttomasz\.github\.io\/ttursm/http:\/\/localhost:8000\/web/g' ./web/style.css
sed -i 's/https:\/\/ttomasz\.github\.io\/ttursm/http:\/\/localhost:8000\/web/g' ./web/site.js
sed -i 's/https:\/\/ttomasz\.github\.io\/ttursm/http:\/\/localhost:8000\/web/g' ./web/styles/map_style.json
