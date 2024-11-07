# Rossum homework

Here is a result of my work on the Rossum assignment.

## 🧪 How to run

### Locally

- Use poetry to install dependencies
- Validate the `.env` contents
- `poetry run python -m flask -e .env --debug run --host=0.0.0.0`

### Docker

- Validate the `.env` contents
- `docker build -t rossum-homework . && docker run rossum-homework`

### Testing the endpoint

- `curl http://127.0.0.1:5000/export -d '{"annotation_id": 4843589, "queue_id": 1411574}' -H "Authorization: Basic bXlVc2VyMTIzOnNlY3JldFNlY3JldA==" -H "Content-Type: application/json"`
    - Note: The IP address might be different (e.g. http://172.17.0.3:5000), check the startup logs of the server

## 📝 Dev notes

As every project can be iterated upon infinitely, there is still some space for improvements.

### Testing

- Right now there is a single e2e test with no mocking
- I would do also a test that mocks 3rd party calls so it won't fail on CI due to 3rd party

### Authentication

- Credentials are in the repo 🫣
- I would e.g. use some placeholders and then have CI runner that has access to secure storage with credential replace these placeholders before deployment

### Formating XML

- For some cases, I only assume where the necessary data is or what is its `schema_id`
- I would create some agreed upon schema as a source of truth of what can I expect in these annotations

### Flask server

- I would use some UWSGI (e.g. gunicorn) to run it with multiple workers
