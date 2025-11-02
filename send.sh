curl -X POST http://127.0.0.1:8080/control \
-H "Content-Type: application/json" \
-d '{"username":"greg6","command":"move_to","params":{"destination":[5,0,0],"duration":2}}'
