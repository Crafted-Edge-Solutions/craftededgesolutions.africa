/* =====================================================
   motion.js — Crafted Edge Solutions
   Awwwards-tier motion layer
   ===================================================== */

(function() {
  'use strict';

  /* ============ LENIS SMOOTH SCROLL ============ */
  let lenis;

  function initLenis() {
    if (typeof Lenis === 'undefined') return;

    lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 1.5,
    });

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // Anchor link smoothness
    document.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', (e) => {
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
          e.preventDefault();
          lenis.scrollTo(target, { offset: -80, duration: 1.6 });
        }
      });
    });
  }

  /* ============ HERO REVEAL ============ */
  function heroReveal() {
    // Split hero title into reveal lines
    const heroTitle = document.querySelector('.hero-title, .page-hero h1');
    if (!heroTitle) return;

    // Already wrapped? Skip.
    if (heroTitle.dataset.revealed) return;
    heroTitle.dataset.revealed = 'true';

    // Wrap each existing line in overflow:hidden and animate up
    const lines = heroTitle.querySelectorAll('.line, br');
    if (lines.length === 0) {
      // No explicit lines — split by <br/>
      const innerHTML = heroTitle.innerHTML;
      const parts = innerHTML.split(/<br\s*\/?>/i);
      heroTitle.innerHTML = parts
        .map(part => `<span class="reveal-line"><span class="reveal-line-inner">${part}</span></span>`)
        .join('');
    } else {
      // Wrap explicit .line elements
      heroTitle.querySelectorAll('.line').forEach(line => {
        const html = line.innerHTML;
        line.innerHTML = `<span class="reveal-line-inner">${html}</span>`;
        line.classList.add('reveal-line');
      });
    }

    // Animate in
    const allLines = heroTitle.querySelectorAll('.reveal-line-inner');
    allLines.forEach((line, i) => {
      line.style.transform = 'translateY(110%)';
      line.style.opacity = '0';
      requestAnimationFrame(() => {
        setTimeout(() => {
          line.style.transition = 'transform 1.2s cubic-bezier(0.22, 1, 0.36, 1), opacity 1.2s ease';
          line.style.transform = 'translateY(0)';
          line.style.opacity = '1';
        }, 100 + i * 140);
      });
    });
  }

  /* ============ SCROLL REVEALS ============ */
  function initScrollReveals() {
    if (typeof IntersectionObserver === 'undefined') return;

    const revealEls = document.querySelectorAll(`
      h2, h3, .numbered-row, .stat-cell, .work-row, .principle-row,
      .cap-block-inner, .sector-cell, .stack-cat, .tier, .contact-list-row,
      .cap-includes li, .pos-body p, .manifesto-body p, .lead, p.intro
    `);

    revealEls.forEach(el => {
      if (el.classList.contains('reveal-init')) return;
      el.classList.add('reveal-init');
    });

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-in');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -8% 0px',
    });

    revealEls.forEach(el => observer.observe(el));
  }

  /* ============ STAT COUNTER ============ */
  function initStatCounter() {
    const statNums = document.querySelectorAll('.stat-num');
    if (!statNums.length || typeof IntersectionObserver === 'undefined') return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const fullText = el.textContent.trim();

        // Extract leading number
        const match = fullText.match(/^(\d+)/);
        if (!match) return;
        const target = parseInt(match[1], 10);
        const suffix = el.querySelector('em')?.textContent || '';
        const pad = match[1].length;

        let current = 0;
        const duration = 1200;
        const start = performance.now();

        function tick(now) {
          const t = Math.min(1, (now - start) / duration);
          const eased = 1 - Math.pow(1 - t, 3);
          current = Math.floor(eased * target);
          el.innerHTML = String(current).padStart(pad, '0') + (suffix ? `<em>${suffix}</em>` : '');
          if (t < 1) requestAnimationFrame(tick);
          else el.innerHTML = match[1] + (suffix ? `<em>${suffix}</em>` : '');
        }

        requestAnimationFrame(tick);
        observer.unobserve(el);
      });
    }, { threshold: 0.5 });

    statNums.forEach(el => observer.observe(el));
  }

  /* ============ MAGNETIC HOVER ============ */
  function initMagnetic() {
    const magnetTargets = document.querySelectorAll('.btn-primary, .nav-cta');

    magnetTargets.forEach(el => {
      const strength = 0.25;
      let bounds;

      function onEnter() { bounds = el.getBoundingClientRect(); }
      function onMove(e) {
        if (!bounds) bounds = el.getBoundingClientRect();
        const x = (e.clientX - bounds.left - bounds.width / 2) * strength;
        const y = (e.clientY - bounds.top - bounds.height / 2) * strength;
        el.style.transform = `translate(${x}px, ${y}px)`;
      }
      function onLeave() {
        el.style.transform = '';
      }

      el.addEventListener('mouseenter', onEnter);
      el.addEventListener('mousemove', onMove);
      el.addEventListener('mouseleave', onLeave);
    });
  }

  /* ============ CUSTOM CURSOR ============ */
  function initCursor() {
    // Skip on touch devices
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) return;

    const dot = document.createElement('div');
    const ring = document.createElement('div');
    dot.className = 'cursor-dot';
    ring.className = 'cursor-ring';
    document.body.appendChild(dot);
    document.body.appendChild(ring);

    let mouseX = 0, mouseY = 0;
    let ringX = 0, ringY = 0;
    let dotX = 0, dotY = 0;

    document.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    function tick() {
      // Dot — follows fast
      dotX += (mouseX - dotX) * 0.5;
      dotY += (mouseY - dotY) * 0.5;
      dot.style.transform = `translate(${dotX}px, ${dotY}px)`;

      // Ring — follows slower
      ringX += (mouseX - ringX) * 0.15;
      ringY += (mouseY - ringY) * 0.15;
      ring.style.transform = `translate(${ringX}px, ${ringY}px)`;

      requestAnimationFrame(tick);
    }
    tick();

    // Hover state on interactive elements
    const hoverables = 'a, button, .btn, input, textarea, select, [data-hover]';
    document.querySelectorAll(hoverables).forEach(el => {
      el.addEventListener('mouseenter', () => {
        ring.classList.add('hover');
        dot.classList.add('hover');
      });
      el.addEventListener('mouseleave', () => {
        ring.classList.remove('hover');
        dot.classList.remove('hover');
      });
    });

    // Hide cursor when leaving window
    document.addEventListener('mouseleave', () => {
      dot.style.opacity = '0';
      ring.style.opacity = '0';
    });
    document.addEventListener('mouseenter', () => {
      dot.style.opacity = '1';
      ring.style.opacity = '1';
    });
  }

  /* ============ NAV SCROLL STATE ============ */
  function initNavScroll() {
    const nav = document.querySelector('nav');
    if (!nav) return;
    let last = 0;
    function update() {
      const y = window.scrollY;
      if (y > 60) nav.classList.add('nav-scrolled');
      else nav.classList.remove('nav-scrolled');
      last = y;
    }
    update();
    window.addEventListener('scroll', update, { passive: true });
  }

  /* ============ PAGE LOADER ============ */
  function pageLoader() {
    const loader = document.createElement('div');
    loader.className = 'page-loader';
    loader.innerHTML = `
      <div class="loader-mark">
        <img src="/static/img/logo.png" alt="Crafted Edge" class="loader-logo" />
        <span class="loader-text">Crafted Edge<span class="loader-dot">.</span></span>
        <div class="loader-bar"><div class="loader-bar-fill"></div></div>
      </div>
    `;
    document.body.appendChild(loader);

    window.addEventListener('load', () => {
      setTimeout(() => {
        loader.classList.add('loader-done');
        setTimeout(() => loader.remove(), 1100);
      }, 600);
    });
  }

  /* ============ INIT ALL ============ */
  function init() {
    pageLoader();
    initCursor();
    initNavScroll();
    initLenis();
    heroReveal();
    initScrollReveals();
    initStatCounter();
    initMagnetic();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
