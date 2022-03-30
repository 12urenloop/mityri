#!/bin/sh

jq '.detections | map( .mac ) | .[]' | sort | uniq
