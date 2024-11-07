import logging
import os
import sys

import structlog

EXPORT_USERNAME = os.getenv("EXPORT_USERNAME")
EXPORT_PASSWORD = os.getenv("EXPORT_PASSWORD")

ROSSUM_USERNAME = os.getenv("ROSSUM_USERNAME")
ROSSUM_PASSWORD = os.getenv("ROSSUM_PASSWORD")


def configure_structlog():
    # Configure basic logging for structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Structlog configuration
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),  # Adds an ISO timestamp
            structlog.processors.JSONRenderer(),  # Renders logs as JSON
        ],
        context_class=dict,  # Use dictionaries for context
        logger_factory=structlog.stdlib.LoggerFactory(),  # Use standard library logger
        wrapper_class=structlog.stdlib.BoundLogger,  # Wrap logger for better compatibility
        cache_logger_on_first_use=True,  # Cache logger for performance
    )
