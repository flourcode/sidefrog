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
