from config.celery_app import celery
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@celery.task(
    name="analitic.tasks.process_low_stock",
    queue="analytics",
    routing_key="analytics.low_stock",
)
def process_low_stock(payload=None, **kwargs):
    """
    Test consumer: receives low-stock notifications from product-service.
    Do the logic in this function as needed.

    Accepts either:
      - a single positional payload dict (payload=<dict>)
      - or keyword arguments (e.g. sku='...', amount=5)

    This function normalizes the input into a dict and appends a JSON line to
    `/tmp/analytic_received.jsonl` for quick verification. UUID and other
    non-JSON-native types are converted using `str` during serialization.
    """
    # Normalize payload input: prefer explicit payload, else take kwargs
    data = payload if payload is not None else kwargs

    logger.info("analytics: received payload: %s", data)

    # Persist to a small file for quick verification (non-critical)
    try:
        with open("/tmp/analytic_received.jsonl", "a", encoding="utf-8") as fh:
            # Use default=str so UUID and other objects become strings
            fh.write(json.dumps({"ts": datetime.utcnow().isoformat(), "payload": data}, default=str) + "\n")
    except Exception:
        logger.exception("Failed to write payload to /tmp/analytic_received.jsonl")

    return {"status": "ok", "received": data}