# rossum_homework

- https://gist.github.com/soof-golan/6ebb97a792ccd87816c0bda1e6e8b8c2


## Run locally

- `poetry run python -m flask --debug run --host=0.0.0.0`
curl http://127.0.0.1:5000/export -d "" -H "Authorization: Basic dXNlcjpwYXNzd29yZA=="
- curl http://127.0.0.1:5000/export -d '{"annotation_id": 1, "queue_id": 2}' -H "Authorization: Basic cGV0cjpwYXNzd29yZA==" -H "Content-Type: application/json"
- {'key': '78f7ce6be68b1c9b74c41a662bb0cdfd0a514019', 'domain': 'bezza.rossum.app'}
- curl -H 'Authorization: Bearer 78f7ce6be68b1c9b74c41a662bb0cdfd0a514019'   'https://bezza.rossum.app/api/v1/annotations'
- 4843589 anotation, queue id 1411574