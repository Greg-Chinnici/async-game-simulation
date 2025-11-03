#!/bin/bash

userNumber="user"$RANDOM
repsonse=$(./sendCreate.sh "$userNumber")
username=$(echo $repsonse | jq -r '.username')

json1='{"movement":"forward","duration":5}'
json2='{"movement":"backward","duration":3}'
json3='{"fly":"diagonal","duration":2}'
json4='{"voice":"soft","emotion":"mad"}'


# send multiple commands using send with generic command
sleep 0.5
./send.sh "$username" "move" "$json1" | jq
echo ''
sleep 0.5
./send.sh "$username" "move" "$json2" | jq
echo '' 
sleep 0.75
./send.sh "$username" "fly" "$json3" | jq
echo ''
sleep 1
./send.sh "$username" "speak" "$json4" | jq
echo ''
