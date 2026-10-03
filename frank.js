// Frank sips his coffee now and then, wherever he appears.
// One Frank at a time, only when he's on screen, never in a background tab,
// and never for people who've asked for reduced motion. CSS does the animation;
// this file only decides who sips and when.
(function () {
  if (!window.matchMedia || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var SIP_MS = 2600;
  var onScreen = new Set();
  var frogs = function () { return Array.prototype.slice.call(document.querySelectorAll(".frog.can-sip")); };

  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) onScreen.add(e.target); else onScreen.delete(e.target); });
  }) : null;
  frogs().forEach(function (f) { if (io) io.observe(f); else onScreen.add(f); });

  function busy(f) {
    if (f.classList.contains("is-idle-sip")) return true;
    var mug = f.querySelector(".mug");
    return !!(mug && mug.getAnimations && mug.getAnimations().some(function (a) { return a.playState === "running"; }));
  }

  function pick() {
    var ready = frogs().filter(function (f) { return onScreen.has(f) && !busy(f); });
    return ready[Math.floor(Math.random() * ready.length)];
  }

  function sip(f) {
    var sticker = f.closest(".sticker");
    if (sticker) sticker.classList.remove("is-sipping");   // the landing sip is done; don't replay it
    f.classList.add("is-idle-sip");
    setTimeout(function () { f.classList.remove("is-idle-sip"); }, SIP_MS + 50);
  }

  function next(delay) {
    setTimeout(function () {
      if (!document.hidden) { var f = pick(); if (f) sip(f); }
      next(9000 + Math.random() * 14000);                 // every 9 to 23 seconds
    }, delay);
  }
  next(5000 + Math.random() * 5000);                      // first sip within 5 to 10 seconds

  window.frankSip = function () { var f = pick(); if (f) sip(f); return !!f; };   // handy for testing
})();
