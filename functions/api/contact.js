// ============================================================
// Crafted Edge Solutions — Contact Form Handler
// Cloudflare Pages Function
// Path: /functions/api/contact.js
// Endpoint: POST /api/contact
// ============================================================
//
// SETUP (one-time, in Cloudflare dashboard):
// 1. Pages → your project → Settings → Environment variables
// 2. Add these (Production + Preview):
//    - RESEND_API_KEY     (get from resend.com, 3000 free emails/month)
//    - TO_EMAIL           = admin@craftededgesolutions.africa
//    - FROM_EMAIL         = noreply@craftededgesolutions.africa
//    - TURNSTILE_SECRET   (optional — for spam protection)
//
// 3. In Resend dashboard → Domains → add craftededgesolutions.africa
//    → add the DNS records they give you (Cloudflare auto-suggests them)
//
// ============================================================

export async function onRequestPost(context) {
  const { request, env } = context;

  // CORS preflight
  const corsHeaders = {
    'Access-Control-Allow-Origin': 'https://craftededgesolutions.africa',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  try {
    const formData = await request.formData();

    // Honeypot — if filled, it's a bot
    if (formData.get('_gotcha')) {
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    const data = {
      firstName: (formData.get('firstName') || '').toString().trim(),
      lastName:  (formData.get('lastName')  || '').toString().trim(),
      email:     (formData.get('email')     || '').toString().trim(),
      phone:     (formData.get('phone')     || '').toString().trim(),
      business:  (formData.get('business')  || '').toString().trim(),
      service:   (formData.get('service')   || '').toString().trim(),
      timeline:  (formData.get('timeline')  || '').toString().trim(),
      message:   (formData.get('message')   || '').toString().trim(),
    };

    // Validation
    if (!data.firstName || !data.email || !data.service) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Missing required fields' }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } }
      );
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Invalid email' }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } }
      );
    }

    // Email to admin
    const adminBody = `
      <div style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;background:#0d1a2e;color:#e8f0ff;padding:32px;border-radius:12px">
        <h2 style="color:#60a5fa;margin:0 0 24px">New Enquiry — Crafted Edge Solutions</h2>
        <table style="width:100%;border-collapse:collapse">
          <tr><td style="padding:8px 0;color:#8da0bf;width:120px">Name:</td><td style="padding:8px 0">${escapeHtml(data.firstName)} ${escapeHtml(data.lastName)}</td></tr>
          <tr><td style="padding:8px 0;color:#8da0bf">Email:</td><td style="padding:8px 0"><a href="mailto:${escapeHtml(data.email)}" style="color:#60a5fa">${escapeHtml(data.email)}</a></td></tr>
          <tr><td style="padding:8px 0;color:#8da0bf">Phone:</td><td style="padding:8px 0">${escapeHtml(data.phone) || '—'}</td></tr>
          <tr><td style="padding:8px 0;color:#8da0bf">Business:</td><td style="padding:8px 0">${escapeHtml(data.business) || '—'}</td></tr>
          <tr><td style="padding:8px 0;color:#8da0bf">Service:</td><td style="padding:8px 0;color:#19c2ff;font-weight:600">${escapeHtml(data.service)}</td></tr>
          <tr><td style="padding:8px 0;color:#8da0bf">Timeline:</td><td style="padding:8px 0">${escapeHtml(data.timeline) || '—'}</td></tr>
        </table>
        <div style="margin-top:24px;padding:18px;background:rgba(255,255,255,0.05);border-radius:8px;border-left:3px solid #2f7df6">
          <div style="color:#8da0bf;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px">Message</div>
          <div style="line-height:1.6;white-space:pre-wrap">${escapeHtml(data.message) || '(no message)'}</div>
        </div>
        <div style="margin-top:24px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.1);font-size:12px;color:#4f6380">
          Submitted from craftededgesolutions.africa · ${new Date().toISOString()}
        </div>
      </div>
    `;

    // Autoresponder to user
    const userBody = `
      <div style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h2 style="color:#0d1a2e">Thanks for reaching out, ${escapeHtml(data.firstName)}.</h2>
        <p style="line-height:1.7;color:#444">We've received your enquiry about <strong>${escapeHtml(data.service)}</strong>. A member of our team will respond within 24 hours on business days.</p>
        <p style="line-height:1.7;color:#444">If your enquiry is urgent, feel free to WhatsApp us on <a href="https://wa.me/254769071925">+254 769 071 925</a>.</p>
        <hr style="border:none;border-top:1px solid #eee;margin:32px 0" />
        <p style="font-size:13px;color:#888;line-height:1.6">
          <strong>Crafted Edge Solutions</strong><br/>
          Software · Automation · AI · Systems Integration<br/>
          Nairobi, Kenya<br/><br/>
          <a href="https://craftededgesolutions.africa" style="color:#2f7df6">craftededgesolutions.africa</a>
        </p>
      </div>
    `;

    // Send via Resend
    const fromEmail = env.FROM_EMAIL || 'noreply@craftededgesolutions.africa';
    const toEmail = env.TO_EMAIL || 'admin@craftededgesolutions.africa';

    const sendEmail = async (to, subject, html, replyTo) => {
      return fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: `Crafted Edge Solutions <${fromEmail}>`,
          to: [to],
          subject,
          html,
          ...(replyTo ? { reply_to: replyTo } : {}),
        }),
      });
    };

    const [adminRes, userRes] = await Promise.all([
      sendEmail(
        toEmail,
        `New enquiry from ${data.firstName} — ${data.service}`,
        adminBody,
        data.email
      ),
      sendEmail(
        data.email,
        'Thanks for reaching out — Crafted Edge Solutions',
        userBody
      ),
    ]);

    if (!adminRes.ok) {
      const err = await adminRes.text();
      console.error('Admin email failed:', err);
      return new Response(
        JSON.stringify({ ok: false, error: 'Email delivery failed' }),
        { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } }
      );
    }

    return new Response(
      JSON.stringify({ ok: true, message: 'Message sent successfully' }),
      { status: 200, headers: { 'Content-Type': 'application/json', ...corsHeaders } }
    );

  } catch (err) {
    console.error('Form handler error:', err);
    return new Response(
      JSON.stringify({ ok: false, error: 'Server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } }
    );
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': 'https://craftededgesolutions.africa',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
