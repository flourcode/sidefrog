// Side Kit: copy buttons for the prompts. Copies the prompt text next to the button.
document.addEventListener("click", function (e) {
  var btn = e.target.closest("button[data-copy]");
  if (!btn) return;
  var box = document.querySelector("#" + btn.getAttribute("data-copy") + " blockquote");
  if (!box) return;
  var text = box.textContent.trim();
  var done = function () {
    btn.textContent = "Copied";
    var live = document.getElementById("kit-announce");
    if (live) live.textContent = "Prompt copied. Paste it into Claude, ChatGPT or Gemini.";
    setTimeout(function () { btn.textContent = "Copy prompt"; }, 2200);
  };
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(done, function () { btn.textContent = "Select the text above to copy"; });
  } else {
    var r = document.createRange(); r.selectNodeContents(box);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
    btn.textContent = "Selected. Press Ctrl+C or \u2318C";
  }
});

// Leap Worksheet: the Print button (no inline handlers; the site's CSP forbids them)
document.addEventListener("click", function (e) {
  if (e.target.closest("button[data-print]")) window.print();
});
