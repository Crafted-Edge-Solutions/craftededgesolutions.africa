import logging

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import IdeaSubmission
from .services import (
    PaystackError,
    GroqError,
    initialize_validator_payment,
    run_basic_analysis,
    run_deep_analysis,
    verify_validator_payment,
)

logger = logging.getLogger(__name__)

FREE_LIMIT_PER_EMAIL = 3


FREE_ITEMS = [
    "Score out of 10",
    "Verdict label",
    "3-paragraph honest critique",
    "Kenya-market specific feedback",
    "Shareable results link",
]

PAID_ITEMS = [
    "Market size estimate",
    "Timing analysis",
    "3 real competitors in Kenya",
    "Top 3 risks + strengths",
    "Specific next steps",
    "The hard truth",
]

UPGRADE_ITEMS = [
    "Market size estimate for Kenya / East Africa",
    "Real timing analysis — is the market ready?",
    "3 actual competitors already operating here",
    "Top 3 risks and strengths (specific)",
    "What to do next — 3 concrete steps",
    "The hard truth most advisors won't tell you",
]

CONSULTING_OFFERS = [
    {"label": "AI Audit — KES 50K", "desc": "Structured review of your business processes and a written AI implementation plan."},
    {"label": "Agent Build — From KES 80K", "desc": "Custom AI agent for your customer service, lead generation, or internal ops."},
    {"label": "AI Lead Gen — KES 30K/mo", "desc": "We build and run a prospecting agent that fills your pipeline automatically."},
]


def validator_home(request):
    return render(request, "validator/home.html", {
        "free_items": FREE_ITEMS,
        "paid_items": PAID_ITEMS,
    })


@require_http_methods(["POST"])
def validator_submit(request):
    email = request.POST.get("email", "").strip().lower()
    idea_name = request.POST.get("idea_name", "").strip()
    idea_description = request.POST.get("idea_description", "").strip()
    target_market = request.POST.get("target_market", "").strip()
    problem_solved = request.POST.get("problem_solved", "").strip()

    errors = []
    if not email:
        errors.append("Email is required.")
    if not idea_name:
        errors.append("Idea name is required.")
    if not idea_description or len(idea_description) < 50:
        errors.append("Please describe your idea in at least 50 characters.")
    if not target_market:
        errors.append("Target market is required.")
    if not problem_solved:
        errors.append("Please describe the problem your idea solves.")

    if not errors:
        recent_count = IdeaSubmission.objects.filter(email=email).count()
        if recent_count >= FREE_LIMIT_PER_EMAIL:
            errors.append(
                f"You've used all {FREE_LIMIT_PER_EMAIL} free analyses for this email. "
                "Upgrade to a paid deep analysis or contact us."
            )

    if errors:
        return render(request, "validator/home.html", {
            "errors": errors,
            "form_data": request.POST,
            "free_items": FREE_ITEMS,
            "paid_items": PAID_ITEMS,
        })

    submission = IdeaSubmission.objects.create(
        email=email,
        idea_name=idea_name,
        idea_description=idea_description,
        target_market=target_market,
        problem_solved=problem_solved,
    )

    run_basic_analysis(submission)

    return redirect("validator_results", uid=submission.uid)


def validator_results(request, uid):
    submission = get_object_or_404(IdeaSubmission, uid=uid)
    return render(request, "validator/results.html", {
        "s": submission,
        "upgrade_items": UPGRADE_ITEMS,
        "consulting_offers": CONSULTING_OFFERS,
    })


@require_http_methods(["POST"])
def validator_upgrade(request, uid):
    submission = get_object_or_404(IdeaSubmission, uid=uid)

    if submission.is_paid:
        return redirect("validator_results", uid=uid)

    callback_url = request.build_absolute_uri(
        f"/validate/callback/{submission.uid}/"
    )

    try:
        auth_url = initialize_validator_payment(submission, callback_url)
    except PaystackError as exc:
        logger.error("Paystack error for validator %s: %s", uid, exc)
        return render(request, "validator/results.html", {
            "s": submission,
            "upgrade_items": UPGRADE_ITEMS,
            "consulting_offers": CONSULTING_OFFERS,
            "payment_error": "Could not initiate payment. Please try again or contact us.",
        })

    return redirect(auth_url)


def validator_callback(request, uid):
    submission = get_object_or_404(IdeaSubmission, uid=uid)
    reference = request.GET.get("reference", submission.paystack_ref)

    if not submission.is_paid and reference:
        try:
            data = verify_validator_payment(reference)
            if data.get("status") == "success":
                run_deep_analysis(submission)
        except (PaystackError, GroqError) as exc:
            logger.error("Payment/analysis error for %s: %s", uid, exc)

    return redirect("validator_results", uid=uid)
