#!/usr/bin/bash

mkdir -p ./tmp
tangoctl -K integration -d -q |  tail -n +2 | while read DEVICE STATE ADMIN VERSION CLASS
do
	echo "Read device ${DEVICE} for class ${CLASS}"
	FNAME=$(echo "$DEVICE" | tr "/" "+")
	echo
	tangoctl -v -K integration -D "${DEVICE}" -jq -O "./tmp/${FNAME}.json"
	echo
	tangoctl -v -K integration -D "${DEVICE}" -mq -O "./tmp/${FNAME}.md"
	echo
	tangoctl -v -K integration -D "${DEVICE}" -q -O "./tmp/${FNAME}.txt"
	echo
	echo "_____________________________________________________________________________________________"
	echo
done
