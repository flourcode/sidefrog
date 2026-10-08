// SideFrog analytics (Google Analytics 4).
//
// To turn it on: paste your GA4 measurement ID below, e.g. "G-ABC123XYZ".
// Until then this file does nothing. It also does nothing when you open the
// files from your desktop, or on any address not listed in LIVE_HOSTS, so
// testing never pollutes your numbers.
//
// What it never sends: the idea someone typed. "We don't save your idea" stays true.
// In GA, under Admin > Data streams > Enhanced measurement, turn OFF
// "Outbound clicks": those record full link addresses, and the Google search
// links contain search phrases. This file counts those clicks without the text.
(function () {
  var GA_ID = "G-MZ6BMZ84Y2";                                        // <- your GA4 ID goes here
  var LIVE_HOSTS = ["sidefrog.com", "www.sidefrog.com"]; // only count real visits

  window.sfTrack = function () {};                       // safe no-op until GA is on
  if (!GA_ID || location.protocol === "file:" || LIVE_HOSTS.indexOf(location.hostname) === -1) return;

  // Google's script (about 175KB) waits until the page has loaded, so on a slow phone it doesn't
  // compete with what the visitor came to see. Everything below queues in dataLayer meanwhile
  // (the page view included) and is sent once it arrives.
  function loadGtag() {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID);
    document.head.appendChild(s);
  }
  function whenIdle() { (window.requestIdleCallback || function (f) { setTimeout(f, 1); })(loadGtag, { timeout: 2000 }); }
  if (document.readyState === "complete") whenIdle(); else window.addEventListener("load", whenIdle);
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", GA_ID, { page_location: location.origin + location.pathname + location.search });   // never the #, where shared verdicts live

  // Events with no personal text in them.
  window.sfTrack = function (name, params) { gtag("event", name, params || {}); };

  // Clicks that leave the site, counted by destination type only.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var h = a.href;
    var u = null;
    try { u = new URL(h, location.href); } catch (err) { /* not a link we count */ }
    if (u && u.origin === location.origin) {
      // A "Check an idea" button that leads to the checker, and the page it was on (not the logo)
      if (u.pathname === "/" && a.classList.contains("plate-btn")) window.sfTrack("check_cta_click", { from: location.pathname });
      // The Jumpstart: which link led to its page (home offer, answer nudge, About...)
      else if (u.pathname === "/jumpstart/" && location.pathname !== "/jumpstart/") window.sfTrack("jumpstart_click", { from: a.classList.contains("js-home-link") ? "home_offer" : a.closest(".js-nudge") ? "answer_nudge" : location.pathname });
      // Side Kit downloads: the meeting backgrounds and the worksheet PDF, by file name
      else if (/^\/side-kit\/.+\.(png|pdf)$/i.test(u.pathname)) window.sfTrack("kit_download", { item: u.pathname.split("/").pop() });
      return;
    }
    // Frank's Shorts and the channel: which one (the video's id, or "channel")
    if (/youtube\.com|youtu\.be/.test(h)) { var vid = (h.match(/shorts\/([\w-]+)/) || [])[1]; window.sfTrack("youtube_click", { video: vid || "channel" }); return; }
    if (/buy\.stripe\.com|checkout\.stripe\.com/.test(h)) { window.sfTrack("jumpstart_checkout", { from: location.pathname }); return; }
    if (/tally\.so|docs\.google\.com\/forms|forms\.gle/.test(h)) { window.sfTrack("jumpstart_form_click"); return; }
    if (/calendly\.com/.test(h)) window.sfTrack("help_click", { via: "calendly" });
    else if (/linkedin\.com\/sharing/.test(h)) window.sfTrack("guide_share", { method: "linkedin" });
    else if (/linkedin\.com/.test(h)) window.sfTrack("help_click", { via: "linkedin" });
    else if (/porkbun\.com/.test(h)) window.sfTrack("register_click");
    else if (/google\.com\/search/.test(h)) window.sfTrack("search_click");
    else if (/quotabird\.com/.test(h)) window.sfTrack("quotabird_click");
  }, true);
})();
