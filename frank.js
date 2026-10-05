// Frank sips his coffee now and then, wherever he appears, and keeps sipping while an
// answer loads. One sprite holds his frames (see build_frank_sprite.py): 0-4 are his
// faces, 5-11 the sip. A sip steps --frame through sip frames and then lets his face come back.
// Idle sips: one Frank at a time, only on screen, never in a background tab, and never
// for people who've asked for reduced motion.
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // Each sip starts and ends looking at the text beside him (data-look), using only frames
  // whose eyes point that way:
  //  left:  rest -> lift (eyes left) -> sip over the mug (eyes forward) -> lift -> rest
  //  right: rest (frame 11) -> 10 -> 9 -> 8 -> sip on 7 (eyes right) -> 8 -> 9 -> 10 -> rest
  var SIPS = {
    left:  { frames: [5, 6, 5],                     times: [200, 950, 200] },
    right: { frames: [10, 9, 8, 7, 8, 9, 10],       times: [140, 150, 170, 850, 170, 150, 140] }
  };
  // Franks looking at you (data-look="you") glance right at their text while they sip, then look back at you
  function sipFor(f) { var l = f.getAttribute("data-look"); return SIPS[l === "right" || l === "you" ? "right" : "left"]; }

  function stop(f) {
    if (!f) return;
    if (f._sip) clearTimeout(f._sip);
    f._sip = null;
    f.style.removeProperty("--frame");
    f.classList.remove("is-sipping");
  }

  function play(f, loop) {
    stop(f);
    var i = 0, s = sipFor(f);
    f.classList.add("is-sipping");
    function step() {
      if (i >= s.frames.length) {
        // back to his resting face (CSS picks it from his mood and gaze); on a loop, pause and go again
        f.style.removeProperty("--frame");
        if (loop) { i = 0; f._sip = setTimeout(step, 900); return; }
        stop(f); return;
      }
      f.style.setProperty("--frame", s.frames[i]);
      f._sip = setTimeout(step, s.times[i]);
      i++;
    }
    f._sip = setTimeout(step, 0);
  }

  // used while an answer loads (app.js); a still Frank for reduced motion
  window.frankLoop = function (f) { if (f && !reduce) play(f, true); };
  window.frankStop = stop;
  if (reduce) return;

  var onScreen = new Set();
  var frogs = function () { return Array.prototype.slice.call(document.querySelectorAll(".frank.can-sip")); };
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) onScreen.add(e.target); else onScreen.delete(e.target); });
  }) : null;
  frogs().forEach(function (f) { if (io) io.observe(f); else onScreen.add(f); });

  function pick() {
    var ready = frogs().filter(function (f) { return onScreen.has(f) && !f._sip && !f.closest(".is-loading"); });
    return ready[Math.floor(Math.random() * ready.length)];
  }
  function next(delay) {
    setTimeout(function () {
      if (!document.hidden) { var f = pick(); if (f) play(f, false); }
      next(9000 + Math.random() * 14000);                 // every 9 to 23 seconds
    }, delay);
  }
  next(5000 + Math.random() * 5000);                      // first sip within 5 to 10 seconds
  window.frankSip = function () { var f = pick(); if (f) play(f, false); return !!f; };   // handy for testing
})();
