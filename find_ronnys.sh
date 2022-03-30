#!/bin/sh

JQ_ONLY_IP='.[] | .Containers[].IPv4Address' 
JQ_QUERY='[.[] | .Containers[] | [.Name, .IPv4Address]] | map(@tsv)|.[]'

docker network inspect mityri_telsysteem | jq -r "${JQ_QUERY}" | grep -e "ronny" | sort # | cut -d'/' -f1
