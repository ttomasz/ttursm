#!/usr/bin/env bash

set -e

sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/index.html
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/style.css
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/site.js
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/osm.json
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/aerial.json
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/protomaps-black.json
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/protomaps-dark.json
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/protomaps-grayscale.json
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/protomaps-light.json
sed -i 's/http:\/\/localhost:8000\/web/https:\/\/ttomasz\.github\.io\/ttursm/g' ./web/styles/protomaps-white.json
