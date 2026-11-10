(function () {
  "use strict";

  // Tahun hak cipta
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // Menu mobile
  var btn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Halaman pencarian (data dari data.js)
  var out = document.getElementById("cari-hasil");
  if (!out) return;
  var ket = document.getElementById("cari-ket");
  var q = (new URLSearchParams(location.search).get("q") || "").trim();
  var input = document.querySelector(".search input");
  if (input) input.value = q;
  var data = window.ARTICLES || [];
  var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  var found = !terms.length ? [] : data.filter(function (a) {
    var hay = (a.t + " " + a.e + " " + a.c).toLowerCase();
    return terms.every(function (t) { return hay.indexOf(t) !== -1; });
  });
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  if (!terms.length) {
    ket.textContent = "Ketik kata kunci pada kolom pencarian di atas.";
  } else if (!found.length) {
    ket.textContent = "Tidak ada berita yang cocok dengan \u201C" + q + "\u201D.";
  } else {
    ket.textContent = found.length + " berita untuk \u201C" + q + "\u201D.";
    out.innerHTML = found.map(function (a) {
      return '<article class="card"><div class="card-body"><span class="category">' + esc(a.c) +
        '</span><h3><a href="' + esc(a.u) + '">' + esc(a.t) + '</a></h3><p>' + esc(a.e) + "</p></div></article>";
    }).join("");
  }
})();

// Berbagi artikel dan menyalin tautan.
document.querySelectorAll('[data-share]').forEach(function (button) {
  button.addEventListener('click', async function () {
    var payload = { title: document.title, text: document.querySelector('.article .lead')?.textContent || document.title, url: location.href };
    try {
      if (navigator.share) await navigator.share(payload);
      else if (navigator.clipboard) { await navigator.clipboard.writeText(location.href); button.textContent = 'Tautan tersalin'; }
    } catch (_) { /* Pengguna membatalkan dialog berbagi. */ }
  });
});
document.querySelectorAll('[data-copy-url]').forEach(function (button) {
  button.addEventListener('click', async function () {
    try { await navigator.clipboard.writeText(location.href); button.textContent = 'Tautan tersalin'; }
    catch (_) { button.textContent = 'Salin manual dari alamat browser'; }
  });
});
