"""Main entrypoint for the Flask app."""

import structlog
from flask import Flask

import config
from views.export import Export

config.configure_structlog()
logger = structlog.get_logger()

app = Flask(__name__)

app.add_url_rule("/export", view_func=Export.as_view("export"))
