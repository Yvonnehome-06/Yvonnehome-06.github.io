/* Evonne Flora Co. ceremony & event decor — vanilla JS, zero dependencies.
   Renders decor items from decor-data.js with subcategory filter,
   lightbox and a graceful empty state while photos are pending. */
(function () {
  "use strict";
  var DATA = window.DECOR_DATA || [];
  var CATS = window.DECOR_CATS || [];

  var elGrid = document.getElementById("decorGrid");
  var elChips = document.getElementById("decorChips");
  var elEmpty = document.getElementById("decorEmpty");
  var elCount = document.getElementById("decorCount");
  if (!elGrid) return;

  var io = null;
  if ("IntersectionObserver" in window) {
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          var img = e.target;
          if (img.dataset.src) { img.src = img.dataset.src; delete img.dataset.src; }
          io.unobserve(img);
        }
      });
    }, { rootMargin: "200px" });
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  var active = "all";

  function render() {
    var list = active === "all" ? DATA : DATA.filter(function (x) { return x.cat === active; });
    elGrid.innerHTML = "";

    if (elCount) elCount.textContent = list.length + (list.length === 1 ? " item" : " items");

    if (!list.length) {
      if (elEmpty) elEmpty.style.display = "block";
      return;
    }
    if (elEmpty) elEmpty.style.display = "none";

    list.forEach(function (x) {
      var node = document.createElement("div");
      node.className = "onsite-item";
      node.innerHTML =
        '<img data-src="' + esc(x.img) + '" alt="' + esc(x.title || "Ceremony decor") + '" loading="lazy" />' +
        '<div class="onsite-cap"><h3>' + esc(x.title || "") + '</h3>' +
        (x.desc ? '<p>' + esc(x.desc) + '</p>' : '') + '</div>';
      elGrid.appendChild(node);
      node.addEventListener("click", function () { openLightbox(x.img, x.title || ""); });
    });

    elGrid.querySelectorAll("img[data-src]").forEach(function (img) {
      if (io) io.observe(img); else img.src = img.dataset.src;
    });
  }

  // chips
  if (elChips && DATA.length) {
    var html = '<button class="chip active" data-cat="all">All (' + DATA.length + ')</button>';
    CATS.forEach(function (c) {
      var n = DATA.filter(function (x) { return x.cat === c.slug; }).length;
      if (n) html += '<button class="chip" data-cat="' + esc(c.slug) + '">' + esc(c.en) + ' (' + n + ')</button>';
    });
    elChips.innerHTML = html;
    elChips.addEventListener("click", function (e) {
      var b = e.target.closest(".chip");
      if (!b) return;
      elChips.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      active = b.dataset.cat;
      render();
    });
  } else if (elChips) {
    elChips.style.display = "none";
  }

  // lightbox
  var lb = document.getElementById("decorLb");
  var lbImg = document.getElementById("decorLbImg");
  var lbCap = document.getElementById("decorLbCap");
  function openLightbox(src, cap) {
    if (!lb) return;
    lbImg.src = src; lbImg.alt = cap; lbCap.textContent = cap;
    lb.classList.add("open"); document.body.style.overflow = "hidden";
  }
  function closeLightbox() {
    if (lb) lb.classList.remove("open");
    document.body.style.overflow = "";
  }
  if (document.getElementById("decorLbClose")) document.getElementById("decorLbClose").addEventListener("click", closeLightbox);
  if (lb) lb.addEventListener("click", function (e) { if (e.target === lb) closeLightbox(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLightbox(); });

  render();
})();
