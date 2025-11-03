#!/bin/bash

USERNAME=${1:?Username required}

URL="http://127.0.0.1:8080/remove"

curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\"}"