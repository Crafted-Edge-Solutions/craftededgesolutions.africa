/* ─── Custom Cursor ───────────────────────────────── */
const dot  = document.querySelector('.cursor-dot');
const ring = document.querySelector('.cursor-ring');
let mx = window.innerWidth / 2, my = window.innerHeight / 2;
let rx = mx, ry = my;

document.addEventListener('mousemove', e => {
  mx = e.clientX; my = e.clientY;
  if (dot) dot.style.transform = `translate(calc(${mx}px - 50%), calc(${my}px - 50%))`;
});

function lerp(a, b, n) { return (1 - n) * a + n * b; }
(function lerpLoop() {
  rx = lerp(rx, mx, 0.1); ry = lerp(ry, my, 0.1);
  if (ring) ring.style.transform = `translate(calc(${rx}px - 50%), calc(${ry}px - 50%))`;
  requestAnimationFrame(lerpLoop);
})();

document.querySelectorAll('a, button, .btn-primary, .btn-secondary, .nav-cta, .nav-hamburger, .whatsapp-float').forEach(el => {
  el.addEventListener('mouseenter', () => ring?.classList.add('link-hover'));
  el.addEventListener('mouseleave', () => ring?.classList.remove('link-hover'));
});
document.querySelectorAll('p, h1, h2, h3, h4').forEach(el => {
  el.addEventListener('mouseenter', () => ring?.classList.add('text-hover'));
  el.addEventListener('mouseleave', () => ring?.classList.remove('text-hover'));
});

/* ─── Page Transitions ────────────────────────────── */
const curtain = document.getElementById('curtain');

function revealPage() {
  if (!curtain) return;
  gsap.fromTo(curtain,
    { scaleY: 1, transformOrigin: 'top' },
    { scaleY: 0, duration: 0.65, ease: 'power3.out', delay: 0.05,
      onComplete: () => { curtain.style.transform = ''; } }
  );
}

function exitPage(href) {
  if (!curtain) { window.location.href = href; return; }
  gsap.fromTo(curtain,
    { scaleY: 0, transformOrigin: 'bottom' },
    { scaleY: 1, duration: 0.45, ease: 'power3.in',
      onComplete: () => { window.location.href = href; } }
  );
}

window.addEventListener('DOMContentLoaded', revealPage);

document.querySelectorAll('a[href]').forEach(link => {
  const href = link.getAttribute('href');
  if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto') || href.startsWith('tel') || href.startsWith('//')) return;
  link.addEventListener('click', e => { e.preventDefault(); exitPage(href); });
});

/* ─── Active Nav ─────────────────────────────────── */
(function setActive() {
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(a => {
    const h = a.getAttribute('href');
    if (!h) return;
    if ((page === '' || page === 'index.html') && (h === 'index.html' || h === './' || h === '/')) {
      a.classList.add('active');
    } else if (h === page) {
      a.classList.add('active');
    }
  });
})();

/* ─── Nav Scroll ─────────────────────────────────── */
const nav = document.querySelector('nav');
const scrollTopBtn = document.getElementById('scrollTop');
window.addEventListener('scroll', () => {
  nav?.classList.toggle('scrolled', window.scrollY > 40);
  scrollTopBtn?.classList.toggle('show', window.scrollY > 500);
}, { passive: true });

/* ─── Mobile Nav ─────────────────────────────────── */
window.toggleMenu = function() {
  document.getElementById('mobileMenu')?.classList.toggle('open');
};

/* ─── GSAP Scroll Reveals ─────────────────────────── */
window.addEventListener('DOMContentLoaded', () => {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger);

  gsap.utils.toArray('.card, .cards-grid-3 > *, .cards-grid-2 > *').forEach((el, i) => {
    if (el.hasAttribute('data-aos')) return;
    gsap.from(el, {
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
      opacity: 0, y: 28, duration: 0.65, ease: 'power3.out', delay: (i % 3) * 0.07
    });
  });

  gsap.utils.toArray('.why-pt, .step, .builder-feat-card, .intern-card, .intern-perk').forEach((el, i) => {
    if (el.hasAttribute('data-aos')) return;
    gsap.from(el, {
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      opacity: 0, y: 24, duration: 0.6, ease: 'power3.out', delay: i * 0.05
    });
  });
});
