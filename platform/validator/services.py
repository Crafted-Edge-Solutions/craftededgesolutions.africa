import json
import logging
import os
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-r1-distill-llama-70b"

BASIC_SYSTEM = """You are a veteran entrepreneur and analyst based in Nairobi, Kenya with 15 years of experience evaluating startups across East Africa. You are honest to the point of being blunt. You don't coddle founders with vague encouragement.

Output a JSON object only — no markdown fences, no preamble — with this exact structure:
{
  "score": integer from 1 to 10,
  "verdict": one of exactly: "build_now", "strong_foundation", "refine_first", "validate_harder", "wrong_market",
  "headline": "one bold, direct sentence capturing your overall take (max 120 chars)",
  "analysis": "3-4 paragraphs of honest critique. Cover: the strongest thing about this idea, the biggest risk or challenge specific to the Kenyan/East African market, and one concrete thing they must validate before going further. Be specific — name real market conditions, real competitors, real cultural or infrastructure constraints in Kenya. Total 200-280 words."
}

Never be generic. Reference Kenya/East Africa specifically. Score 1-4 = serious problems, 5-6 = needs work, 7-8 = promising, 9-10 = rare."""

DEEP_SYSTEM = """You are a senior venture analyst with deep knowledge of Kenya and East Africa. You've evaluated 400+ ideas. You are analytically rigorous and refuse to give generic feedback.

Output a JSON object only — no markdown fences, no preamble — with this exact structure:
{
  "score": integer from 1 to 10,
  "verdict": one of exactly: "build_now", "strong_foundation", "refine_first", "validate_harder", "wrong_market",
  "headline": "one bold, direct sentence (max 120 chars)",
  "market_analysis": {
    "size": "estimated addressable market in Kenya/East Africa — give a number or range",
    "timing": "is the market ready now? what infrastructure or behavior makes this the right or wrong time?",
    "growth": "what drives growth and what could stall it?"
  },
  "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
  "risks": ["critical risk 1 — specific to Kenya/EA", "critical risk 2", "critical risk 3"],
  "competitors": ["real competitor or substitute 1 already operating in Kenya/EA", "competitor or substitute 2"],
  "what_to_do_next": ["specific, actionable step 1", "specific step 2", "specific step 3"],
  "the_hard_truth": "2-3 sentences of what most advisors won't tell them. The uncomfortable thing they need to hear."
}

Every field must be specific to the Kenyan/East African market. Name real companies. Cite real market conditions. No generic startup advice."""


class GroqError(RuntimeError):
    pass


def _call_groq(messages: list, max_tokens: int = 1500) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise GroqError("GROQ_API_KEY not set")

    payload = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.6,
    }).encode()

    req = Request(
        GROQ_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CraftedEdgeSolutions/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except HTTPError as exc:
        raise GroqError(f"Groq HTTP {exc.code}: {exc.read().decode()}") from exc
    except URLError as exc:
        raise GroqError(str(exc)) from exc


def _strip_fences(text: str) -> str:
    import re
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Strip DeepSeek <think>...</think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def _parse_verdict(raw: str) -> str:
    valid = {"build_now", "strong_foundation", "refine_first", "validate_harder", "wrong_market"}
    return raw if raw in valid else "refine_first"


def run_basic_analysis(submission) -> None:
    user_msg = (
        f"Idea name: {submission.idea_name}\n"
        f"Description: {submission.idea_description}\n"
        f"Target market: {submission.target_market}\n"
        f"Problem being solved: {submission.problem_solved}"
    )
    messages = [
        {"role": "system", "content": BASIC_SYSTEM},
        {"role": "user", "content": user_msg},
    ]
    try:
        raw = _call_groq(messages, max_tokens=900)
        data = json.loads(_strip_fences(raw))
        submission.score = int(data.get("score", 5))
        submission.verdict = _parse_verdict(data.get("verdict", ""))
        submission.headline = data.get("headline", "")[:400]
        submission.basic_analysis = data.get("analysis", "")
        submission.analysis_done = True
        submission.save()
    except Exception as exc:
        logger.error("Basic analysis failed for %s: %s", submission.uid, exc)
        submission.basic_analysis = "Analysis could not be completed. Please contact us at hello@craftededgesolutions.africa."
        submission.analysis_done = True
        submission.save()


def run_deep_analysis(submission) -> None:
    user_msg = (
        f"Idea name: {submission.idea_name}\n"
        f"Description: {submission.idea_description}\n"
        f"Target market: {submission.target_market}\n"
        f"Problem being solved: {submission.problem_solved}"
    )
    messages = [
        {"role": "system", "content": DEEP_SYSTEM},
        {"role": "user", "content": user_msg},
    ]
    try:
        raw = _call_groq(messages, max_tokens=2000)
        data = json.loads(_strip_fences(raw))
        submission.score = int(data.get("score", submission.score or 5))
        submission.verdict = _parse_verdict(data.get("verdict", submission.verdict))
        submission.headline = data.get("headline", submission.headline)[:400]
        submission.deep_data = data
        submission.is_paid = True
        submission.analysis_done = True
        submission.save()
    except Exception as exc:
        logger.error("Deep analysis failed for %s: %s", submission.uid, exc)
        submission.analysis_done = True
        submission.save()


# ---------------------------------------------------------------------------
# Paystack one-time payment
# ---------------------------------------------------------------------------

PAYSTACK_BASE = "https://api.paystack.co"
VALIDATOR_AMOUNT_KOBO = 50000  # KES 500


class PaystackError(RuntimeError):
    pass


def _paystack_request(path: str, payload: dict | None = None, method: str = "GET") -> dict:
    key = getattr(settings, "PAYSTACK_SECRET_KEY", "")
    if not key:
        raise PaystackError("PAYSTACK_SECRET_KEY not configured")

    body = json.dumps(payload).encode() if payload else None
    req = Request(
        f"{PAYSTACK_BASE}{path}",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        raise PaystackError(exc.read().decode()) from exc
    except URLError as exc:
        raise PaystackError(str(exc)) from exc


def initialize_validator_payment(submission, callback_url: str) -> str:
    ref = f"CES-VAL-{uuid.uuid4().hex[:12].upper()}"
    result = _paystack_request("/transaction/initialize", {
        "email": submission.email,
        "amount": VALIDATOR_AMOUNT_KOBO,
        "currency": "KES",
        "reference": ref,
        "callback_url": callback_url,
        "metadata": {
            "idea_name": submission.idea_name,
            "submission_uid": str(submission.uid),
            "custom_fields": [
                {"display_name": "Idea", "variable_name": "idea_name", "value": submission.idea_name},
            ],
        },
    }, method="POST")

    if not result.get("status"):
        raise PaystackError(result.get("message", "Paystack init failed"))

    submission.paystack_ref = ref
    submission.save(update_fields=["paystack_ref"])
    return result["data"]["authorization_url"]


def verify_validator_payment(reference: str) -> dict:
    result = _paystack_request(f"/transaction/verify/{reference}")
    if not result.get("status"):
        raise PaystackError(result.get("message", "Verify failed"))
    return result["data"]
