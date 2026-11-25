/* Evonne Flora Co. ceremony & event decor — vanilla JS, zero dependencies.
   Renders decor items from decor-data.js with subcategory filter and an
   editorial lightbox: one card per product, variants revealed on open. */
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

    if (elCount) elCount.textContent = list.length + (list.length === 1 ? " product" : " products");

    if (!list.length) {
      if (elEmpty) elEmpty.style.display = "block";
      return;
    }
    if (elEmpty) elEmpty.style.display = "none";

    list.forEach(function (x) {
      var variants = Array.isArray(x.variants) && x.variants.length ? x.variants : null;
      var node = document.createElement("div");
      node.className = "decor-item";
      node.innerHTML =
        '<img data-src="' + esc(x.img) + '" alt="' + esc(x.title || "Ceremony decor") + '" loading="lazy" />' +
        (variants ? '<span class="style-count">' + variants.length + ' styles</span>' : '') +
        '<div class="decor-cap"><h3>' + esc(x.title || "") + '</h3>' +
        (x.desc ? '<p>' + esc(x.desc) + '</p>' : '') + '</div>';
      elGrid.appendChild(node);
      node.addEventListener("click", function () { openLightbox(x, variants); });
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

  // editorial lightbox — left large image + right variant list
  var lb = document.getElementById("decorLb");
  var lbImg = document.getElementById("decorLbImg");
  var lbTitle = document.getElementById("decorLbTitle");
  var lbDesc = document.getElementById("decorLbDesc");
  var lbProducts = document.getElementById("decorLbProducts");
  var lbCount = document.getElementById("decorLbCount");
  var lbDots = document.getElementById("decorLbDots");
  var cur = 0, slides = [];

  function paint() {
    var s = slides[cur];
    if (!s) return;
    if (lbImg) { lbImg.src = s.img; lbImg.alt = s.title || ""; }
    if (lbCount) lbCount.textContent = (cur + 1) + ' / ' + slides.length;
    if (lbDots) {
      lbDots.innerHTML = "";
      slides.forEach(function (_, i) {
        var b = document.createElement("button");
        b.className = "lb-dot" + (i === cur ? " active" : "");
        b.setAttribute("aria-label", "Image " + (i + 1));
        b.addEventListener("click", function () { cur = i; paint(); });
        lbDots.appendChild(b);
      });
    }
    if (lbProducts) {
      lbProducts.querySelectorAll(".lb-mini").forEach(function (el, i) {
        el.classList.toggle("active", i + 1 === cur);
      });
    }
  }

  function openLightbox(item, variants) {
    if (!lb) return;
    // First slide is always the cover (scene photo); variants follow.
    slides = [{ img: item.img, title: item.title, desc: item.desc, cover: true }]
      .concat(variants || []);
    cur = 0;
    if (lbTitle) lbTitle.textContent = item.title || "";
    if (lbDesc) lbDesc.textContent = item.desc || "";
    var stylesLabel = document.getElementById("decorLbStylesLabel");
    if (stylesLabel) stylesLabel.textContent = variants && variants.length > 1 ? (variants.length + " options") : "Made to order";
    if (lbProducts) {
      lbProducts.innerHTML = "";
      if (variants && variants.length > 1) {
        variants.forEach(function (v, i) {
          var a = document.createElement("button");
          a.className = "lb-mini";
          a.type = "button";
          a.innerHTML =
            '<img src="' + esc(v.img || item.img) + '" alt="" loading="lazy" />' +
            '<span class="lb-mini-txt"><strong>' + esc(v.title || item.title || "") + '</strong>' +
            (v.desc ? '<small>' + esc(v.desc) + '</small>' : '') + '</span>';
          a.addEventListener("click", function () { cur = i + 1; paint(); });
          lbProducts.appendChild(a);
        });
      }
    }
    paint();
    lb.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    if (lb) lb.classList.remove("open");
    document.body.style.overflow = "";
  }

  if (document.getElementById("decorLbClose")) document.getElementById("decorLbClose").addEventListener("click", closeLightbox);
  var prev = document.getElementById("decorLbPrev");
  var next = document.getElementById("decorLbNext");
  if (prev) prev.addEventListener("click", function () { cur = (cur - 1 + slides.length) % slides.length; paint(); });
  if (next) next.addEventListener("click", function () { cur = (cur + 1) % slides.length; paint(); });
  if (lb) lb.addEventListener("click", function (e) { if (e.target === lb) closeLightbox(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeLightbox();
    if (!lb || !lb.classList.contains("open")) return;
    if (e.key === "ArrowLeft") { cur = (cur - 1 + slides.length) % slides.length; paint(); }
    if (e.key === "ArrowRight") { cur = (cur + 1) % slides.length; paint(); }
  });

  render();
})();
