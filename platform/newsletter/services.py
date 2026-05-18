import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import base64
import json

from django.conf import settings

logger = logging.getLogger(__name__)


def _listmonk_request(path, payload=None, method="GET"):
    base = settings.LISTMONK_BASE_URL.rstrip("/")
    url = urljoin(base + "/", f"api/{path.lstrip('/')}")
    credentials = base64.b64encode(
        f"{settings.LISTMONK_USERNAME}:{settings.LISTMONK_PASSWORD}".encode()
    ).decode()

    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        logger.error("Listmonk API error %s: %s", exc.code, detail)
        return None
    except URLError as exc:
        logger.error("Listmonk connection error: %s", exc)
        return None


def sync_subscriber_to_listmonk(*, email, name=""):
    """
    Add or update a subscriber in Listmonk and add them to the Insights list.
    Silently logs errors — never raises, so payment flow is never interrupted.
    """
    list_id = settings.LISTMONK_LIST_ID_INSIGHTS
    if not list_id:
        logger.warning("LISTMONK_LIST_ID_INSIGHTS not configured, skipping sync for %s", email)
        return

    payload = {
        "email": email,
        "name": name or email,
        "status": "enabled",
        "lists": [list_id],
    }
    result = _listmonk_request("subscribers", payload=payload, method="POST")
    if result is None:
        # Subscriber may already exist — try updating via query
        _add_existing_subscriber_to_list(email=email, list_id=list_id)
    else:
        logger.info("Listmonk: subscribed %s to Insights list", email)


def _add_existing_subscriber_to_list(*, email, list_id):
    """Find existing subscriber by email and add them to the Insights list."""
    result = _listmonk_request(f"subscribers?query=subscribers.email='{email}'&page=1&per_page=1")
    if not result:
        return
    data = result.get("data", {})
    results = data.get("results", [])
    if not results:
        return

    subscriber_id = results[0].get("id")
    if not subscriber_id:
        return

    _listmonk_request(
        f"subscribers/{subscriber_id}/lists",
        payload={"ids": [list_id], "action": "add", "status": "confirmed"},
        method="PUT",
    )
    logger.info("Listmonk: added existing subscriber %s to Insights list", email)


def unsubscribe_from_listmonk(*, email):
    """Disable a subscriber's Insights list membership on cancellation."""
    list_id = settings.LISTMONK_LIST_ID_INSIGHTS
    if not list_id:
        return

    result = _listmonk_request(f"subscribers?query=subscribers.email='{email}'&page=1&per_page=1")
    if not result:
        return
    results = result.get("data", {}).get("results", [])
    if not results:
        return

    subscriber_id = results[0].get("id")
    if subscriber_id:
        _listmonk_request(
            f"subscribers/{subscriber_id}/lists",
            payload={"ids": [list_id], "action": "remove"},
            method="PUT",
        )
        logger.info("Listmonk: removed %s from Insights list", email)
