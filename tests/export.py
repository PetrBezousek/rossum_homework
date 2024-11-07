from base64 import b64encode

from flask.testing import FlaskClient

import config


def get_basic_auth_header(username: str, password: str) -> dict[str, str]:
    # Helper function to generate the Authorization header for basic auth
    credentials = f"{username}:{password}"
    base64_credentials = b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {base64_credentials}"}


def test_happy_path(client: FlaskClient) -> None:
    """E2E test using input data that result in a successful responses from 3rd party."""
    headers = get_basic_auth_header(config.EXPORT_USERNAME, config.EXPORT_PASSWORD)
    data = {
        "annotation_id": 4843589,
        "queue_id": 1411574,
    }
    response = client.post("/export", headers=headers, json=data)

    assert response.status_code == 200
    assert response.json == {
        "success": True,
    }
