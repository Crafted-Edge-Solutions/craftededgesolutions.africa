import json

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


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

HOW_WE_WORK = [
    ("Project-based contracts", "We bring you in for specific client engagements — a build, a launch, a production problem that needs solving. You're not on the bench waiting for work."),
    ("Remote-first", "We work async-first with clear briefs. No daily standups unless the engagement calls for it. We trust our collaborators to own their slice."),
    ("Principal-led", "Every engagement is overseen by a senior engineer. You'll get context, clear direction, and meaningful feedback — not just a Jira board."),
    ("Craft over speed", "We move fast but we don't cut corners. Quality code, clean interfaces, systems that last. We expect the same standard from everyone we work with."),
]

VALUES = [
    ("Ownership", "We want people who see a problem and fix it without being asked. If it's broken and you notice it, it's yours to surface."),
    ("Clarity", "Write clearly, communicate early, ask before you assume. Ambiguity compounds fast on small teams."),
    ("Depth", "We'd rather you know one thing exceptionally well than six things superficially. Specialists ship better software."),
    ("Honesty", "If a deadline is unrealistic, say so. If the architecture is wrong, say so. We make better decisions with real information."),
]

OPEN_ROLES = [
    {
        "title": "Contract Backend Engineer",
        "type": "Contract · Remote",
        "description": "Django/Python engineers who've shipped production APIs. You'll work alongside the principal on client builds — integrations, platform architecture, data pipelines.",
        "skills": ["Python", "Django", "PostgreSQL", "REST APIs", "Docker"],
    },
    {
        "title": "Frontend / Full-Stack Engineer",
        "type": "Contract · Remote",
        "description": "Engineers comfortable owning the full UI layer — ideally with experience in vanilla JS, Alpine, or React. We build fast, clean interfaces. No bloat.",
        "skills": ["HTML/CSS", "JavaScript", "React or Alpine", "Git"],
    },
    {
        "title": "DevOps / Infrastructure Engineer",
        "type": "Contract · Remote",
        "description": "Cloud infrastructure experience (AWS, GCP, or Railway/Fly.io). CI/CD, Terraform, container orchestration. We provision serious systems for serious clients.",
        "skills": ["Linux", "Docker", "CI/CD", "AWS or GCP", "Terraform"],
    },
    {
        "title": "Technical Writer / Content Strategist",
        "type": "Part-time · Remote",
        "description": "You write clearly about engineering and systems. You'll contribute to Insights — our premium technical publication — and help shape studio content.",
        "skills": ["Technical writing", "Engineering background", "Markdown"],
    },
]


def pricing(request):
    return render(request, "pricing.html", {
        "insights_perks": INSIGHTS_PERKS,
        "faqs": FAQS,
    })


def careers(request):
    return render(request, "careers.html", {
        "roles": OPEN_ROLES,
        "how_we_work": HOW_WE_WORK,
        "values": VALUES,
    })


@csrf_exempt
@require_POST
def contact_api(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = {}

    if data.get("_gotcha"):
        return JsonResponse({"ok": True})

    name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    business = data.get("business", "").strip()
    service = data.get("service", "").strip()
    message = data.get("message", "").strip()
    timeline = data.get("timeline", "").strip()

    if not email:
        return JsonResponse({"ok": False, "error": "Email required."}, status=400)

    body = f"""New project enquiry — craftededgesolutions.africa

Name:     {name}
Email:    {email}
Phone:    {phone}
Business: {business}
Service:  {service}
Timeline: {timeline}

Message:
{message}
"""
    send_mail(
        subject=f"Enquiry: {service or 'General'} — {name or email}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["hello@craftededgesolutions.africa"],
        fail_silently=True,
    )

    return JsonResponse({"ok": True})


@cache_control(max_age=86400)
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /cms/",
        "Disallow: /django-admin/",
        "Disallow: /dashboard/",
        "Disallow: /accounts/",
        "Disallow: /subscriptions/",
        "Disallow: /documents/",
        "",
        "# AI crawlers — welcome, see /llms.txt for structured context",
        "User-agent: GPTBot",
        "Allow: /",
        "Disallow: /dashboard/",
        "Disallow: /cms/",
        "",
        "User-agent: ClaudeBot",
        "Allow: /",
        "Disallow: /dashboard/",
        "Disallow: /cms/",
        "",
        "User-agent: anthropic-ai",
        "Allow: /",
        "",
        "Sitemap: https://craftededgesolutions.africa/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@cache_control(max_age=86400)
def llms_txt(request):
    content = """\
# Crafted Edge Solutions

> A principal-led product engineering studio based in Nairobi, Kenya.
> We build software platforms, AI-powered systems, and scalable digital
> infrastructure for ambitious businesses in East Africa and globally.

## About

Crafted Edge Solutions is a boutique engineering studio founded by Meshack,
a senior software engineer based in Nairobi. We operate at the intersection
of technical rigour and business outcomes — taking on five high-impact
partnerships at a time. We are not an agency. We are engineers who run a studio.

## Services

- **Fixed-scope builds** — Web platforms, API backends, mobile integrations, AI systems
- **Discovery Sprint** — 2-week technical roadmap engagement (from KES 120,000)
- **Monthly Retainer** — Embedded principal engineering (from KES 300,000/month)
- **Insights Membership** — Premium engineering reports and business intelligence (KES 499/month or USD 4.99/month)

## Key pages

- / — Studio index
- /services/ — Full capabilities
- /solutions/ — Case studies and past work
- /insights/ — Premium technical publication
- /pricing/ — Engagement tiers and Insights pricing
- /about/ — Studio background and process
- /contact/ — Start a project
- /careers/ — Work with the studio

## Insights publication

Insights is a premium technical publication covering:
- M-Pesa and East African fintech integrations
- Django, Python, and full-stack engineering
- AI and automation for African-context problems
- Infrastructure and DevOps on tight budgets
- Product engineering and DX intelligence

Free posts are publicly accessible. Premium posts require an Insights membership.

## Contact

Email: hello@craftededgesolutions.africa
Phone: +254 769 071 925
Location: Nairobi, Kenya · Operating globally
"""
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
