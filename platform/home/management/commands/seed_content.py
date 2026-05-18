"""
Seed sample Insights posts and Solutions/Case Studies into the Wagtail page tree.
Safe to re-run — skips existing pages by title.
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page
from wagtail.rich_text import RichText


class Command(BaseCommand):
    help = "Seed sample Insights posts and case studies"

    def handle(self, *args, **options):
        self._seed_insights()
        self._seed_solutions()
        self.stdout.write("Seeding complete.")

    # ------------------------------------------------------------------ #
    # Insights posts
    # ------------------------------------------------------------------ #
    def _seed_insights(self):
        from insights.models import InsightsIndexPage, InsightsPostPage

        try:
            index = InsightsIndexPage.objects.live().first()
        except Exception:
            self.stdout.write("No InsightsIndexPage found — run bootstrap_pages first.")
            return

        posts = [
            # --- FREE TEASERS ---
            dict(
                title="Why Most African Startups Overpay for Cloud Infrastructure",
                category="infrastructure",
                summary="A breakdown of the most common cloud cost traps — and the self-hosted alternatives that save 60–80% without sacrificing reliability.",
                estimated_read_minutes=6,
                is_premium=False,
                body_html="""<p>Cloud infrastructure is eating African startup margins. AWS, GCP, and Azure are optimised for enterprises with procurement teams and reserved-instance commitments — not lean startups running on runway.</p>
<p>Here is what we see consistently across clients:</p>
<ul>
<li><b>Elastic IPs and load balancers</b> billing even when idle</li>
<li><b>Database instances</b> sized for peak load that never comes</li>
<li><b>Egress fees</b> that multiply every time the product finds traction</li>
</ul>
<p>The alternative is not complicated. A <b>Hetzner CX22</b> (2 vCPU, 4 GB RAM) costs €3.29/month. With Docker and nginx it runs a Django application serving tens of thousands of requests per day. The same workload on a comparable AWS EC2 instance costs $35–60/month.</p>
<p>The argument against self-hosting — "you need DevOps expertise" — is weaker than it was three years ago. Tools like Coolify and Railway bring one-click deploys to bare metal. You keep the economics of a VPS with something close to the developer experience of a managed platform.</p>
<p><i>This post is a free teaser. The full infrastructure guide (including our exact Hetzner + Cloudflare + Docker setup for production Django apps) is available to Insights members.</i></p>""",
            ),
            dict(
                title="The M-Pesa Integration Guide Nobody Wrote",
                category="architecture",
                summary="STK Push, C2B, B2C, and webhooks — a practical implementation guide covering the Daraja API quirks that the official docs skip.",
                estimated_read_minutes=8,
                is_premium=False,
                body_html="""<p>Safaricom's Daraja API is the entry point to M-Pesa for every developer building in East Africa. It is also, to put it charitably, a documentation challenge.</p>
<p>The official docs describe the happy path. This post covers what happens when you leave it.</p>
<h2>STK Push: the timeout problem</h2>
<p>STK Push initiates a payment prompt on the customer's phone. The callback fires when the transaction completes — or fails. What the docs don't say clearly: <b>callbacks can arrive seconds or minutes later</b>, and they can arrive out of order.</p>
<p>The correct implementation uses idempotent webhook handlers keyed on <code>MpesaReceiptNumber</code>, not on the checkout request ID. We have seen duplicate callbacks arrive for the same transaction in production.</p>
<h2>The sandbox vs production gap</h2>
<p>Sandbox and production behave differently in ways that are not documented. Phone number validation is stricter in production. Timeout windows differ. Some callback fields present in sandbox responses are absent in production ones.</p>
<p><i>The full guide — including our complete Django implementation with error handling, idempotency, and retry logic — is available to Insights members.</i></p>""",
            ),
            dict(
                title="Building AI Agents That Actually Work in Production",
                category="ai",
                summary="Most AI agent demos look impressive and collapse in production. Here is what separates the ones that ship from the ones that stall.",
                estimated_read_minutes=7,
                is_premium=False,
                body_html="""<p>The pattern is familiar by now. A founder sees a demo of an AI agent that books meetings, writes emails, and manages a calendar — all from a single natural language prompt. They hire a team to build one. Six months later, it works in demos and not much else.</p>
<p>The gap between demo and production comes down to three things:</p>
<h2>1. Tool design, not model selection</h2>
<p>The model matters less than the tools it is given. An agent with well-scoped, well-documented tools running on GPT-3.5 will outperform a poorly-tooled agent running on GPT-4. Most failed agent projects fail here — they give the model too much access and not enough structure.</p>
<h2>2. Failure modes are the product</h2>
<p>A production agent needs explicit handling for every failure case: API timeouts, ambiguous instructions, missing context, out-of-scope requests. An agent that says "I cannot help with that, but here is what I can do" is more valuable than one that hallucinates a confident answer.</p>
<h2>3. Human handoff is not optional</h2>
<p>Every production agent needs a clear escalation path to a human. Not as a fallback for failures — as a designed feature. The businesses that get the most value from agents are the ones that use them to handle volume and route exceptions to people.</p>
<p><i>The full implementation guide — covering MCP protocol, tool architecture, observability, and our production deployment pattern — is available to Insights members.</i></p>""",
            ),

            # --- PREMIUM POSTS ---
            dict(
                title="Full WhatsApp Business API Implementation: From Sandbox to Production",
                category="architecture",
                summary="Everything we learned building WhatsApp integrations for three production systems — Meta's API, webhooks, message templates, and the approval process.",
                estimated_read_minutes=15,
                is_premium=True,
                body_html="""<p>WhatsApp Business API is the highest-ROI communication channel for businesses operating in East Africa. Open rates exceed 90%. Response rates are 10–15× email. And it is the channel your customers already live in.</p>
<p>This is the implementation guide we wish existed when we started.</p>
<h2>Prerequisites</h2>
<p>You need a Meta Business Account, a dedicated phone number (not currently on WhatsApp), and a Facebook App with the WhatsApp product added. The onboarding takes 1–3 business days for approval.</p>
<h2>Message Templates</h2>
<p>All outbound messages outside the 24-hour customer service window must use pre-approved templates. Template approval takes 24–48 hours. Design your templates to be specific enough to be useful but generic enough to cover multiple use cases. Rejections are common and the feedback is minimal.</p>
<p>Our approved template set for a typical business:</p>
<ul>
<li>Order confirmation: <code>Your order {{1}} has been confirmed. Total: {{2}}. We'll update you when it ships.</code></li>
<li>Payment received: <code>Payment of {{1}} received. Reference: {{2}}. Thank you.</code></li>
<li>Appointment reminder: <code>Reminder: your appointment on {{1}} at {{2}}. Reply CONFIRM or CANCEL.</code></li>
<li>Support ticket: <code>Hi {{1}}, your support request has been received. Reference: {{2}}. We'll respond within {{3}}.</code></li>
</ul>
<h2>Webhook Architecture</h2>
<p>Meta sends all events (incoming messages, status updates, template delivery receipts) to a single webhook endpoint. The payload structure is deeply nested and not particularly intuitive. Here is our production handler structure:</p>
<p>The key insight: process webhook events asynchronously. The Meta API expects a 200 response within 5 seconds. Queue heavy processing for a background worker.</p>
<h2>The 24-hour window</h2>
<p>When a customer messages you, you have 24 hours to respond with any message — templates are not required. After 24 hours, you are back to templates only. Build your flows to maximise use of the open window: confirm, follow up, and collect information while you can send freely.</p>
<h2>Rate limits and production behaviour</h2>
<p>The API rate limits are per phone number, not per account. For high-volume sending (10,000+ messages/day), you need to apply for higher tiers through Meta's business support. Start this process early — it can take weeks.</p>
<h2>Cost model</h2>
<p>Meta charges per conversation, not per message. A conversation is a 24-hour window starting from either a business-initiated or customer-initiated message. Rates vary by country. For Kenya, expect approximately $0.02–0.04 per conversation.</p>""",
            ),
            dict(
                title="How We Built a Multi-Tenant SaaS in 6 Weeks",
                category="architecture",
                summary="Architecture decisions, trade-offs, and the exact tech stack behind a production multi-tenant Django platform — from schema design to deployment.",
                estimated_read_minutes=18,
                is_premium=True,
                body_html="""<p>Six weeks from initial brief to production deploy. Here is the complete architecture behind a multi-tenant SaaS platform we shipped for a client in the logistics sector.</p>
<h2>The brief</h2>
<p>A fleet management company needed a platform where each of their enterprise clients could log in to a separate, isolated dashboard — their drivers, routes, and trip history — while the operator could see across all accounts. Standard multi-tenancy problem.</p>
<h2>Schema strategy: shared database, row-level isolation</h2>
<p>We chose a shared database over separate schemas per tenant. The reasons: simpler migrations, easier cross-tenant analytics for the operator, and no connection pool explosion at scale. The trade-off is that every query must filter by tenant — we enforced this at the model layer with a custom Manager that automatically scopes querysets.</p>
<p>Every model that holds tenant data inherits from a <code>TenantModel</code> base class. The manager's <code>get_queryset()</code> reads the current tenant from a thread-local set by middleware. If tenant context is missing, queries raise rather than leak cross-tenant data.</p>
<h2>Authentication and tenant resolution</h2>
<p>Users belong to one tenant. Tenant resolution happens at login: the user's tenant is stored in the session and loaded into thread-local context on every request by middleware. Subdomain routing (<code>clientname.platform.com</code>) provides a second layer of tenant isolation — a user can only authenticate on their tenant's subdomain.</p>
<h2>The stack</h2>
<ul>
<li>Django 5.2 with a custom User model (email auth, no username)</li>
<li>PostgreSQL with row-level security as a defence-in-depth measure</li>
<li>React frontend consuming a DRF API — the dashboard is too dynamic for server-rendered HTML</li>
<li>Redis for session storage and background task queues (Celery)</li>
<li>Hetzner CX32 (4 vCPU, 8 GB) — handles 50 concurrent tenants with room to spare</li>
</ul>
<h2>Deployment</h2>
<p>Nginx proxies to Gunicorn (8 workers, gevent worker class for async I/O). Static files on Cloudflare R2. Daily Postgres backups to S3-compatible storage with 30-day retention.</p>
<h2>What we'd do differently</h2>
<p>We underestimated the complexity of the notification system. Real-time updates (driver location, trip status) were added in week 5, and we should have designed for them from day 1. The WebSocket architecture was retrofitted — it works, but the seams show.</p>""",
            ),
            dict(
                title="AI Agents for East African Businesses: Architecture, Costs, and Real Numbers",
                category="ai",
                summary="The real cost of running an AI agent in production — token costs, infrastructure, maintenance — and the business cases where the numbers actually work.",
                estimated_read_minutes=12,
                is_premium=True,
                body_html="""<p>Everyone is building AI agents. Very few are sharing what they actually cost to run. This post covers the economics of three production agent deployments and what we have learned about where the value is.</p>
<h2>The three models</h2>
<p><b>Cloud API agents</b> (OpenAI, Claude, Groq) are the fastest to build and the easiest to scale. Cost is variable — you pay per token. For a customer service agent handling 200 conversations/day at ~2,000 tokens per conversation, expect $15–40/month at current pricing.</p>
<p><b>Local inference agents</b> (Ollama, llama.cpp) have zero per-token cost but require hardware. A server with a consumer GPU (RTX 3090 or 4090) handles 10–50 requests/second on 7B models. Upfront hardware cost is $1,500–2,500 plus hosting. Breakeven vs cloud API is typically 4–6 months at moderate volume.</p>
<p><b>Hybrid agents</b> route routine queries to a local model and complex queries to a cloud API. This is our recommended architecture for most East African businesses — local handles 70–80% of queries at near-zero cost, cloud handles the edge cases.</p>
<h2>Real deployment costs</h2>
<p>Customer service agent for an e-commerce client (Kenya, ~500 conversations/day):</p>
<ul>
<li>Claude Haiku for routine queries: ~$12/month</li>
<li>Claude Sonnet for complex queries (escalated ~15%): ~$28/month</li>
<li>Infrastructure (Railway, 2GB RAM): $10/month</li>
<li>Total: ~$50/month replacing 1.5 FTE customer service hours</li>
</ul>
<h2>Where the numbers work</h2>
<p>The business cases with the strongest ROI are not the obvious ones. Customer service works, but the margins are moderate because good human customer service in Kenya is not expensive.</p>
<p>The cases with exceptional ROI:</p>
<ul>
<li><b>Lead qualification</b>: replacing human SDRs for initial qualification. Payback in weeks.</li>
<li><b>Document processing</b>: invoices, contracts, forms. 100× throughput at 5% of human cost.</li>
<li><b>Internal knowledge bases</b>: employees querying company documentation. High value, low volume.</li>
</ul>
<h2>What we are watching</h2>
<p>Local model quality is improving faster than cloud pricing is falling. In 18 months, we expect the economics of local inference to look substantially better than they do today — particularly for African deployments where latency to US/EU cloud regions is a real product issue.</p>""",
            ),
            dict(
                title="The Paystack + Django Integration Guide: Subscriptions, Webhooks, and Edge Cases",
                category="architecture",
                summary="A production-grade Paystack integration in Django — initializing transactions, verifying webhooks, handling subscription lifecycle events, and the edge cases Paystack's docs gloss over.",
                estimated_read_minutes=14,
                is_premium=True,
                body_html="""<p>Paystack is the best payment infrastructure for East African businesses. This is the guide to integrating it properly in Django — not just making a payment work, but building a subscription system that handles the full lifecycle.</p>
<h2>Transaction initialization</h2>
<p>Every Paystack transaction starts with an initialization API call that returns an <code>authorization_url</code>. The user is redirected there to complete payment. On return, you receive a reference parameter and verify the transaction.</p>
<p>The important non-obvious point: <b>initialize the transaction server-side</b>. Never pass your secret key to the frontend. The public key is for Paystack.js only — for direct API calls, always use the secret key server-side.</p>
<h2>Webhook verification</h2>
<p>Paystack sends event notifications to your webhook URL signed with HMAC-SHA512. Verify every webhook before processing it. Do not trust the payload without verifying the signature. The signing secret is your Paystack secret key.</p>
<p>Webhook processing must be idempotent. The same event can be delivered multiple times. Key every event on its ID and skip processing if already handled.</p>
<h2>Subscription lifecycle</h2>
<p>The events you must handle for a complete subscription system:</p>
<ul>
<li><code>charge.success</code>: payment completed (fires for both one-time and subscription charges)</li>
<li><code>subscription.create</code>: new subscription activated</li>
<li><code>subscription.disable</code>: subscription cancelled by customer</li>
<li><code>subscription.not_renew</code>: renewal failed (card expired, insufficient funds)</li>
<li><code>invoice.payment_failed</code>: retry attempt failed</li>
</ul>
<h2>The currency problem</h2>
<p>Paystack plans are currency-specific. A KES plan cannot charge USD. If you want to accept both KES and USD, you need separate plans and separate checkout flows. Track which plan a subscriber is on so you know which currency to show in your UI.</p>
<h2>Testing webhooks locally</h2>
<p>Use ngrok or Cloudflare Tunnel to expose your local server. Paystack's dashboard lets you send test events to any URL. Always test every event type before going to production — the payload schemas are not identical across event types.</p>""",
            ),
        ]

        import re

        def slugify(s):
            s = s.lower()
            s = re.sub(r"[^\w\s-]", "", s)
            s = re.sub(r"[\s_]+", "-", s)
            return s[:80].strip("-")

        for data in posts:
            if InsightsPostPage.objects.filter(title=data["title"]).exists():
                self.stdout.write(f"  Skipping (exists): {data['title'][:60]}")
                continue

            post = InsightsPostPage(
                title=data["title"],
                slug=slugify(data["title"]),
                category=data["category"],
                summary=data["summary"],
                estimated_read_minutes=data["estimated_read_minutes"],
                is_premium=data["is_premium"],
                body=[("paragraph", RichText(data["body_html"]))],
            )
            index.add_child(instance=post)
            post.save_revision().publish()
            tier = "PREMIUM" if data["is_premium"] else "free"
            self.stdout.write(f"  Created [{tier}]: {data['title'][:60]}")

    # ------------------------------------------------------------------ #
    # Case studies
    # ------------------------------------------------------------------ #
    def _seed_solutions(self):
        from home.models import SolutionsIndexPage, CaseStudyPage

        try:
            index = SolutionsIndexPage.objects.live().first()
        except Exception:
            self.stdout.write("No SolutionsIndexPage — run bootstrap_pages first.")
            return

        if not index:
            self.stdout.write("No SolutionsIndexPage found — skipping case studies.")
            return

        studies = [
            dict(
                title="M-Pesa Payment Infrastructure for a Logistics Platform",
                client_name="Confidential — Logistics sector",
                sector="Logistics & Supply Chain",
                outcome_tag="payment",
                timeline="3 weeks",
                is_featured=True,
                summary="Built a complete M-Pesa STK Push and B2C payment system for a last-mile logistics platform, handling driver payouts, customer payments, and automated reconciliation.",
                challenge="<p>The client was processing payments manually — drivers were paid via manual M-Pesa sends, customers paid via bank transfer, and reconciliation took a full day each month. The platform needed to automate the full payment cycle without disrupting 200+ active drivers.</p>",
                solution="<p>We implemented the full Daraja API stack: STK Push for customer payments, B2C for driver disbursements, and a webhook-driven reconciliation engine. All transactions are logged with idempotent processing to handle the duplicate callbacks that Daraja occasionally sends in production.</p><p>The system handles peak loads of 300 transactions per hour without manual intervention. Reconciliation is automatic and auditable.</p>",
                results="<p><strong>98% reduction</strong> in payment processing time. Reconciliation dropped from 8 hours to 12 minutes. Driver complaints about payment delays dropped to zero within the first month.</p>",
                stack="Django, Celery, PostgreSQL, M-Pesa Daraja API, Redis",
            ),
            dict(
                title="AI Customer Service Agent for an E-Commerce Platform",
                client_name="Confidential — E-commerce sector",
                sector="E-Commerce / Retail",
                outcome_tag="ai",
                timeline="4 weeks",
                is_featured=True,
                summary="Deployed a multi-channel AI agent handling order status queries, return requests, and product questions across WhatsApp and web chat — processing 500+ conversations daily.",
                challenge="<p>A growing e-commerce business was spending 40% of their operational budget on customer service for largely repetitive queries: order status, delivery estimates, return policy, product availability. Human agents were bottlenecked and response times were suffering.</p>",
                solution="<p>We built a hybrid AI agent using Claude Haiku for routine queries and Claude Sonnet for complex escalations. The agent has access to live order data via tool calls, can process return requests, and knows when to hand off to a human. Deployed on WhatsApp Business API and a web chat widget.</p><p>Human agents now only handle genuine edge cases — disputes, damaged goods, complaints requiring judgment.</p>",
                results="<p><strong>73% of queries resolved without human intervention.</strong> Average response time dropped from 4 hours to 90 seconds. Customer service headcount held flat while order volume grew 60%.</p>",
                stack="Python, Claude API, WhatsApp Business API, Django, PostgreSQL",
            ),
            dict(
                title="Automation Infrastructure for a Professional Services Firm",
                client_name="Confidential — Professional services",
                sector="Professional Services",
                outcome_tag="ai",
                timeline="2 weeks",
                is_featured=False,
                summary="Connected CRM, invoicing, and email into a single automated workflow — eliminating 15 hours of manual data entry per week and reducing invoice-to-payment time by 40%.",
                challenge="<p>The firm was running on three disconnected tools: a CRM, an invoicing platform, and email. Every client update required manual data entry in all three. Invoices were sent manually. Payment follow-ups were manual. An estimated 15 hours per week went to administrative overhead that generated no value.</p>",
                solution="<p>We built an n8n automation layer connecting all three systems. New CRM contacts automatically create invoicing profiles. Completed projects trigger invoice generation. Overdue invoices trigger escalating follow-up sequences. Payment confirmations update the CRM and trigger onboarding sequences.</p>",
                results="<p><strong>15 hours/week recovered.</strong> Invoice-to-payment time reduced from 22 days to 13 days. Zero missed follow-ups since deployment.</p>",
                stack="n8n, Stripe, HubSpot API, Resend, PostgreSQL",
            ),
            dict(
                title="Self-Hosted Infrastructure Migration: Cloud to Hetzner",
                client_name="Confidential — SaaS startup",
                sector="SaaS / Technology",
                outcome_tag="infra",
                timeline="1 week",
                is_featured=False,
                summary="Migrated a 3-service Django application from AWS to Hetzner, reducing monthly infrastructure costs by 74% with zero downtime and improved performance.",
                challenge="<p>A SaaS startup was paying $340/month for AWS infrastructure that was 80% idle. The application — a Django API, a PostgreSQL database, and a Celery worker — was running on EC2 instances sized for traffic projections that never materialised.</p>",
                solution="<p>We migrated the full stack to a Hetzner CX32 (€14.39/month) with Docker Compose orchestration, Cloudflare as the CDN and DDoS layer, and daily encrypted backups to Hetzner's object storage. Zero-downtime migration using DNS-level traffic switching.</p>",
                results="<p><strong>74% cost reduction</strong> — from $340 to $89/month (Hetzner + Cloudflare + backups). P95 response time improved by 30% due to lower network latency. System has run without incident for 8 months.</p>",
                stack="Docker, Nginx, Gunicorn, PostgreSQL, Cloudflare, Hetzner",
            ),
        ]

        import re

        def slugify(s):
            s = s.lower()
            s = re.sub(r"[^\w\s-]", "", s)
            s = re.sub(r"[\s_]+", "-", s)
            return s[:80].strip("-")

        for data in studies:
            if CaseStudyPage.objects.filter(title=data["title"]).exists():
                self.stdout.write(f"  Skipping (exists): {data['title'][:60]}")
                continue

            study = CaseStudyPage(
                title=data["title"],
                slug=slugify(data["title"]),
                client_name=data["client_name"],
                sector=data["sector"],
                outcome_tag=data["outcome_tag"],
                timeline=data.get("timeline", ""),
                is_featured=data.get("is_featured", False),
                summary=data["summary"],
                challenge=data.get("challenge", ""),
                solution=data.get("solution", ""),
                results=data.get("results", ""),
                stack=data.get("stack", ""),
            )
            index.add_child(instance=study)
            study.save_revision().publish()
            self.stdout.write(f"  Created case study: {data['title'][:60]}")
