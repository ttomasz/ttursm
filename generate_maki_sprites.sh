#!/usr/bin/env bash

set -e

~/Downloads/spreet --ratio 2 ./web/maki-icons/svgs/ ./web/sprites/maki
~/Downloads/spreet --ratio 4 ./web/maki-icons/svgs/ ./web/sprites/maki@2x
