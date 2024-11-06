from base64 import b64encode

from flask import jsonify


def get_basic_auth_header(username, password):
    # Helper function to generate the Authorization header for basic auth
    credentials = f"{username}:{password}"
    base64_credentials = b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {base64_credentials}"}

def test_happy_path(client):
    headers = get_basic_auth_header("user", "password")
    data = {
        "annotation_id": 1,
        "queue_id": 1,
    }
    response = client.post("/export", headers=headers, json=data)

    assert response.status_code == 200
    assert response.json == {
        "success": True,
    }