from django.shortcuts import render


INSIGHTS_PERKS = [
    "Full access to all premium Insights reports (10+ and growing)",
    "Implementation deep-dives from live production systems",
    "Business intelligence specific to East African markets",
    "M-Pesa, Paystack, and fintech integration guides",
    "AI and automation playbooks for African-context problems",
    "New reports published monthly",
]

FAQS = [
    (
        "Do you work with early-stage startups?",
        "Yes — we work with founders at any stage. A Discovery Sprint is often the right starting point: "
        "it gives you a clear technical roadmap without committing to a full build.",
    ),
    (
        "What currencies do you accept for studio work?",
        "We invoice in KES for East African clients and USD for international engagements. "
        "Paystack and M-Pesa are both supported.",
    ),
    (
        "How does Insights billing work?",
        "Insights subscriptions are billed monthly via Paystack. "
        "You can cancel any time — access continues until the end of your billing period.",
    ),
    (
        "Can I cancel my Insights subscription?",
        "Yes. Email hello@craftededgesolutions.africa with your cancellation request "
        "and we'll process it immediately. No questions asked.",
    ),
    (
        "Do you offer custom enterprise pricing?",
        "For teams of five or more, or bespoke licensing arrangements, "
        "reach out to us directly and we'll put together a custom proposal.",
    ),
]


def pricing(request):
    return render(request, "pricing.html", {
        "insights_perks": INSIGHTS_PERKS,
        "faqs": FAQS,
    })
