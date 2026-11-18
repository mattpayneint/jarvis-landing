/* Booking source tag (2026-11-18).
   Stamps every Calendly link on the page with utm_medium=website.<page>.<where the visitor came from>
   so each booking in Supabase calendly_booking_sources shows its source.
   Uses utm_medium ONLY: utm_source / utm_content / utm_term / utm_campaign are reserved for the
   Meta ad id / fbc / fbp / event id (see assets/fbc-fbp.js). Changes nothing visible on the page. */
(function () {
  function clean(s) {
    return (s || '').toString().toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40);
  }
  function param(name) {
    var m = new RegExp('[?&]' + name + '=([^&#]*)').exec(window.location.search);
    return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : '';
  }
  function store(v) {
    try { window.localStorage.setItem('mpc_from', v); } catch (e) {}
    try { document.cookie = 'mpc_from=' + encodeURIComponent(v) + ';path=/;max-age=' + (30 * 86400) + ';SameSite=Lax'; } catch (e) {}
  }
  function stored() {
    try { var v = window.localStorage.getItem('mpc_from'); if (v) return v; } catch (e) {}
    var m = /(?:^|; )mpc_from=([^;]*)/.exec(document.cookie || '');
    return m ? decodeURIComponent(m[1]) : '';
  }

  var host = window.location.hostname.replace(/^www\./, '');
  var ref = '';
  try { ref = document.referrer ? new URL(document.referrer).hostname.replace(/^www\./, '') : ''; } catch (e) {}
  if (ref === host) ref = '';
  var arrived = clean(param('src') || param('utm_source') || (param('adid') || param('fbclid') ? 'meta' : '') || ref);
  if (arrived) store(arrived);

  window.mpcSourceTag = function () {
    var page = clean((window.location.pathname.split('/').pop() || 'index').replace(/\.html$/, '')) || 'index';
    return 'website.' + page + '.' + (arrived || clean(stored()) || 'direct');
  };

  window.mpcTagCalendlyLink = function (link) {
    if (!link || link.indexOf('calendly.com') === -1 || link.indexOf('utm_medium=') !== -1) return link;
    return link + (link.indexOf('?') === -1 ? '?' : '&') + 'utm_medium=' + encodeURIComponent(window.mpcSourceTag());
  };

  function tagAll() {
    var links = document.querySelectorAll('a[href*="calendly.com"]');
    for (var i = 0; i < links.length; i++) {
      links[i].setAttribute('href', window.mpcTagCalendlyLink(links[i].getAttribute('href')));
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', tagAll);
  else tagAll();
})();
