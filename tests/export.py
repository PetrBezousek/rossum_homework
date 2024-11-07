from base64 import b64encode

from _pytest.logging import LogCaptureFixture
from flask.testing import FlaskClient

import config
from tests.constants import EXPORT_FORMATED_CONTENT_B64


def get_basic_auth_header(username: str, password: str) -> dict[str, str]:
    """Get authorization header for the test."""
    credentials = f"{username}:{password}"
    base64_credentials = b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {base64_credentials}"}


def test_happy_path(client: FlaskClient, caplog: LogCaptureFixture) -> None:
    """E2E test using input data that result in a successful responses from 3rd party."""
    # Given
    headers = get_basic_auth_header(config.EXPORT_USERNAME, config.EXPORT_PASSWORD)
    data = {
        "annotation_id": 4843589,
        "queue_id": 1411574,
    }

    # When
    response = client.post("/export", headers=headers, json=data)

    # Then
    assert response.status_code == 200
    assert response.json == {
        "success": True,
    }
    assert len(caplog.messages) == 3  # export.request, client_rossum.get_annotation, client_postbin.send_annotation
    for message in caplog.messages:
        if "client_postbin.send_annotation" in message:
            assert EXPORT_FORMATED_CONTENT_B64 in message
