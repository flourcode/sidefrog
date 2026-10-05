// Viewing the site from your desktop (file://): folder links open their index.html.
// Does nothing on the live site. Kept in a file (not inline) so the site's
// Content-Security-Policy can forbid inline scripts.
if (location.protocol === "file:") document.addEventListener("click", function (e) {
  var a = e.target.closest("a[href]"); if (!a) return;
  var h = a.getAttribute("href"); if (/^[a-z]+:/i.test(h) || h.charAt(0) === "#") return;
  var parts = h.split("#"); var path = parts[0].split("?")[0];
  if (path.slice(-1) !== "/") return;
  e.preventDefault(); location.href = path + "index.html" + (parts[1] ? "#" + parts[1] : "");
});

// "Copy link" on Break Room guides (and anywhere else with data-copy-link)
document.addEventListener("click", function (e) {
  var b = e.target.closest("[data-copy-link]");
  if (!b) return;
  var url = b.getAttribute("data-copy-link"), label = b.textContent;
  var done = function () { b.textContent = "Link copied"; setTimeout(function () { b.textContent = label; }, 2200); };
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(url).then(done, function () { window.prompt("Copy this link:", url); });
  else window.prompt("Copy this link:", url);
  if (window.sfTrack) window.sfTrack("guide_share", { method: "copy_link" });
});
