import structlog
from flask import g, jsonify
from flask.views import MethodView
from flask_expects_json import expects_json
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from clients.postbin import ClientPostbin
from clients.rossum import ClientRossum
from config import EXPORT_PASSWORD, EXPORT_USERNAME, ROSSUM_PASSWORD, ROSSUM_USERNAME
from formatters.xml import reformat_xml

logger = structlog.get_logger()
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username: str, password: str) -> bool | None:
    if username == EXPORT_USERNAME and check_password_hash(generate_password_hash(EXPORT_PASSWORD), password):
        return True
    return None


class Export(MethodView):
    """/export"""

    SCHEMA = {
        "type": "object",
        "properties": {
            "annotation_id": {"type": "integer"},
            "queue_id": {"type": "integer"},
        },
        "required": ["annotation_id", "queue_id"],
    }

    @auth.login_required
    @expects_json(SCHEMA)
    def post(self):
        logger.info("export.request", data=g.data)
        is_success = True
        try:
            client_rossum = ClientRossum(ROSSUM_USERNAME, ROSSUM_PASSWORD)
            content = client_rossum.get_annotation_content()
            generated_xml = reformat_xml(content)
            ClientPostbin().send_annotation(generated_xml)
        except Exception:
            logger.exception("export.exception")
            is_success = False

        return jsonify(
            {
                "success": is_success,
            }
        )
