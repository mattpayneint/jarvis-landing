// Meta click-ID capture + Calendly link enrichment (wired 2026-09-13, closes the
// "nothing is measurable" gap from the 9/13 Meta ads audit).
//
// _fbp is set automatically by fbevents.js on any page with a Pixel base snippet.
// _fbc is normally built by fbevents.js too, but ONLY when it sees a `fbclid` URL
// param on the page the ad click actually lands on. This runs that same construction
// independently of fbevents.js (Meta's documented fb.<subdomain_index>.<ms_timestamp>.
// <fbclid> format) so click-ID capture survives fbevents.js being blocked by a tracker/
// ad blocker, and works even before a real Pixel ID exists.
//
// Include this on every funnel page, before any script that needs to read _fbc/_fbp.
(function () {
  function getParam(name) {
    var m = new RegExp('[?&]' + name + '=([^&]+)').exec(window.location.search);
    return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : null;
  }
  function readCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
  }
  function setCookie(name, value, days) {
    var expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/; SameSite=Lax';
  }

  var fbclid = getParam('fbclid');
  if (fbclid && !readCookie('_fbc')) {
    setCookie('_fbc', 'fb.1.' + Date.now() + '.' + fbclid, 90);
  }

  // Shared helper: append fbc/fbp (and an optional CAPI dedup event ID) onto a Calendly
  // link as utm_content/utm_term/utm_campaign. Calendly passes utm_* straight through,
  // untouched, into the webhook payload's "tracking" object -- no native fbc/fbp field
  // exists on Calendly, so these three otherwise-unused-here UTM slots carry them to the
  // n8n "Calendly -> Meta Conversions API" workflow. Real utm_source/utm_medium from an
  // ad's own destination URL are left alone so genuine ad-campaign attribution isn't
  // clobbered.
  window.mpcMetaParams = function (link, eventId) {
    var fbc = readCookie('_fbc');
    var fbp = readCookie('_fbp');
    var params = [];
    if (fbc) params.push('utm_content=' + encodeURIComponent(fbc));
    if (fbp) params.push('utm_term=' + encodeURIComponent(fbp));
    if (eventId) params.push('utm_campaign=' + encodeURIComponent(eventId));
    if (!params.length) return link;
    var sep = link.indexOf('?') === -1 ? '?' : '&';
    return link + sep + params.join('&');
  };

  window.mpcNewEventId = function () {
    if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
    return 'evt-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
  };

  // Auto-enrich any static Calendly links already in the DOM (vc/advisor/attorney pages'
  // "Schedule A Call" buttons) -- also stamps a fresh eventID onto each for CAPI dedup and
  // fires the matching client-side Pixel event through the existing onclick handler's
  // fbq('track','Schedule') by leaving the eventID recoverable on the element itself.
  document.addEventListener('DOMContentLoaded', function () {
    var links = document.querySelectorAll('a[href*="calendly.com"]');
    for (var i = 0; i < links.length; i++) {
      var eventId = window.mpcNewEventId();
      links[i].dataset.mpcEventId = eventId;
      links[i].setAttribute('href', window.mpcMetaParams(links[i].getAttribute('href'), eventId));
    }
  });
})();
