// Shared motion system for the landing-page family (optin/vc/advisor/attorney).
// Scroll-reveal + word-stagger headlines + card tilt — same techniques used
// across matthewpayneconsulting.com's main site, kept in one file so all
// four pages stay in sync instead of drifting apart.

(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Word-stagger: wraps each word of an element's current text in its own
  // span with an incrementing transition-delay, so a parent .is-visible
  // class (added by the reveal observer below) fires them in sequence.
  function staggerWords(el) {
    if (!el || el.dataset.staggered === '1') return;
    var text = el.textContent.trim();
    if (!text) return;
    var words = text.split(/\s+/);
    el.innerHTML = words.map(function (w, i) {
      return '<span class="aw" style="transition-delay:' + (i * 70) + 'ms">' + w + '</span>';
    }).join(' ');
    el.dataset.staggered = '1';
  }
  document.querySelectorAll('.stagger').forEach(staggerWords);

  // Scroll-reveal: .reveal and .stagger sections fade/lift into place as
  // they enter view. No-op entirely under reduced-motion — everything just
  // stays visible with no transition.
  if (!reduced && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal, .stagger').forEach(function (el, i) {
      if (!el.style.transitionDelay) el.style.transitionDelay = (i % 4) * 70 + 'ms';
      observer.observe(el);
    });
  } else {
    document.querySelectorAll('.reveal, .stagger').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  // Mouse-responsive 3D tilt on any [data-tilt] card. Mouse-only, skipped
  // under reduced-motion.
  if (!reduced && window.matchMedia('(hover: hover)').matches) {
    document.querySelectorAll('[data-tilt]').forEach(function (card) {
      card.addEventListener('mousemove', function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform =
          'perspective(1000px) rotateY(' + (x * 5) + 'deg) rotateX(' + (-y * 5) + 'deg) translateZ(0)';
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform = '';
      });
    });
  }
})();
