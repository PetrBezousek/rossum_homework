import requests
import structlog
from flask import g

logger = structlog.get_logger()


class ClientRossum:
    """Client to communicate with rossum.

    For simplicity, assume only the bezza.rossum.app domain.
    """

    username: str
    password: str

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_auth_header(self) -> dict:
        """Get necessary headers for rossum API request.

        Get credentials from env variables.
        """
        rossum_login = {
            "username": self.username,
            "password": self.password,
        }
        response = requests.post("https://bezza.rossum.app/api/v1/auth/login", json=rossum_login)
        response.raise_for_status()
        headers = {"Authorization": f"Bearer {response.json()['key']}"}
        return headers

    def get_annotation_content(self) -> bytes:
        params = {
            "format": "xml",
            "id": g.data["annotation_id"],
        }
        logger.info(
            "client_rossum.get_annotation",
            queue_id=g.data["queue_id"],
            annotation_id=g.data["annotation_id"],
        )
        rossum_export_data = requests.get(
            f'https://bezza.rossum.app/api/v1/queues/{g.data["queue_id"]}/export',
            params=params,
            headers=self.get_auth_header(),
        )
        rossum_export_data.raise_for_status()
        return rossum_export_data.content
