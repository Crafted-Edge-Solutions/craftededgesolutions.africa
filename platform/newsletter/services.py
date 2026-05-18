import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Zoho Campaigns
# ---------------------------------------------------------------------------
# Setup (one-time, 10 minutes):
#   1. Go to https://api-console.zoho.com/ → Create a "Self Client"
#   2. Scope: ZohoCampaigns.contact.CREATE,ZohoCampaigns.contact.UPDATE
#   3. Generate code → exchange for tokens once:
#      POST https://accounts.zoho.com/oauth/v2/token
#        ?grant_type=authorization_code&client_id=...&client_secret=...&code=...&redirect_uri=...
#   4. Save refresh_token to Railway env var ZOHO_CAMPAIGNS_REFRESH_TOKEN
#   5. In Zoho Campaigns → Contacts → Lists → copy the list key to ZOHO_CAMPAIGNS_LIST_KEY
# ---------------------------------------------------------------------------

_zoho_token_cache = {"token": None, "expires_at": 0}


def _get_zoho_access_token():
    """Return a valid Zoho access token, refreshing if expired."""
    now = time.time()
    if _zoho_token_cache["token"] and now < _zoho_token_cache["expires_at"] - 60:
        return _zoho_token_cache["token"]

    dc = getattr(settings, "ZOHO_CAMPAIGNS_DC", "com")
    data = urlencode({
        "grant_type": "refresh_token",
        "client_id": settings.ZOHO_CAMPAIGNS_CLIENT_ID,
        "client_secret": settings.ZOHO_CAMPAIGNS_CLIENT_SECRET,
        "refresh_token": settings.ZOHO_CAMPAIGNS_REFRESH_TOKEN,
    }).encode()

    req = Request(
        f"https://accounts.zoho.{dc}/oauth/v2/token",
        data=data,
        method="POST",
    )
    try:
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
        token = result.get("access_token")
        expires_in = int(result.get("expires_in", 3600))
        _zoho_token_cache["token"] = token
        _zoho_token_cache["expires_at"] = now + expires_in
        return token
    except Exception as exc:
        logger.error("Zoho token refresh failed: %s", exc)
        return None


def _zoho_configured():
    return all([
        getattr(settings, "ZOHO_CAMPAIGNS_CLIENT_ID", ""),
        getattr(settings, "ZOHO_CAMPAIGNS_CLIENT_SECRET", ""),
        getattr(settings, "ZOHO_CAMPAIGNS_REFRESH_TOKEN", ""),
        getattr(settings, "ZOHO_CAMPAIGNS_LIST_KEY", ""),
    ])


def sync_subscriber_to_zoho(*, email, name="", list_key=None):
    """
    Add or update a subscriber in Zoho Campaigns.
    Silently logs errors — never raises.
    """
    if not _zoho_configured():
        logger.debug("Zoho Campaigns not configured, skipping sync for %s", email)
        return

    token = _get_zoho_access_token()
    if not token:
        return

    dc = getattr(settings, "ZOHO_CAMPAIGNS_DC", "com")
    key = list_key or settings.ZOHO_CAMPAIGNS_LIST_KEY

    contact_info = json.dumps({"Contact Email": email, "First Name": name or ""})
    body = urlencode({
        "resfmt": "JSON",
        "listkey": key,
        "contactinfo": contact_info,
    }).encode()

    req = Request(
        f"https://campaigns.zoho.{dc}/api/v1.1/json/listsubscribeall",
        data=body,
        method="POST",
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
    )
    try:
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
        status = result.get("status", "")
        if status == "success":
            logger.info("Zoho Campaigns: subscribed %s", email)
        else:
            logger.warning("Zoho Campaigns subscribe response: %s", result)
    except Exception as exc:
        logger.error("Zoho Campaigns subscribe failed for %s: %s", email, exc)


def unsubscribe_from_zoho(*, email, list_key=None):
    """Remove a subscriber from the Zoho Campaigns list on cancellation."""
    if not _zoho_configured():
        return

    token = _get_zoho_access_token()
    if not token:
        return

    dc = getattr(settings, "ZOHO_CAMPAIGNS_DC", "com")
    key = list_key or settings.ZOHO_CAMPAIGNS_LIST_KEY

    body = urlencode({
        "resfmt": "JSON",
        "listkey": key,
        "emailids": email,
    }).encode()

    req = Request(
        f"https://campaigns.zoho.{dc}/api/v1.1/json/listunsubscribe",
        data=body,
        method="POST",
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
    )
    try:
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
        logger.info("Zoho Campaigns: unsubscribed %s — %s", email, result.get("status"))
    except Exception as exc:
        logger.error("Zoho Campaigns unsubscribe failed for %s: %s", email, exc)


# ---------------------------------------------------------------------------
# Public interface — used by views and subscription signals
# ---------------------------------------------------------------------------

def sync_subscriber(*, email, name=""):
    """Add subscriber to Zoho Campaigns. Call from newsletter signup and Paystack webhook."""
    sync_subscriber_to_zoho(email=email, name=name)


def remove_subscriber(*, email):
    """Remove subscriber from Zoho Campaigns. Call on subscription cancellation."""
    unsubscribe_from_zoho(email=email)


# ---------------------------------------------------------------------------
# Legacy Listmonk shim — kept so existing call sites don't break
# ---------------------------------------------------------------------------

def sync_subscriber_to_listmonk(*, email, name=""):
    sync_subscriber(email=email, name=name)


def unsubscribe_from_listmonk(*, email):
    remove_subscriber(email=email)
