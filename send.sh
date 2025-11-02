#!/bin/bash
# ./control.sh <username> <command> '<params_json>'

USERNAME=${1:?Username required}
COMMAND=${2:?Command required}
PARAMS_JSON=${3:?Params JSON required}

URL="http://127.0.0.1:8080/control"

curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"command\":\"$COMMAND\",\"params\":$PARAMS_JSON}"
