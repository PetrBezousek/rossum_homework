import base64

import requests
import structlog
from flask import g
from lxml import etree
from lxml.etree import Element

logger = structlog.get_logger()


class ClientPostbin:
    """Client to communicate with postbin.

    On init, create a bin for sending data.
    """

    URL = "https://www.postb.in"
    bin_id: str

    def __init__(self):
        response = requests.post(f"{self.URL}/api/bin")
        response.raise_for_status()
        self.bin_id = response.json()["binId"]

    def send_annotation(self, xml: Element) -> None:
        """Send POST request with given XML there encoded via b64."""
        data = {
            "annotation_id": g.data["annotation_id"],
            "content": base64.b64encode(etree.tostring(xml, pretty_print=True)).decode("ascii"),
        }
        logger.info("client_postbin.send_annotation", bin_id=self.bin_id, data=data)
        response = requests.post(f"{self.URL}/{self.bin_id}", json=data)
        response.raise_for_status()
