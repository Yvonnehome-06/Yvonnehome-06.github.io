/* Evonne Flora Co. catalog — vanilla JS, zero dependencies.
   One card per STYLE (products-aggregated.js); click to open an editorial
   lightbox: large photo left, all colour/size variants right (like the
   on-site case panel). Filters, search and batched rendering preserved. */
(function () {
  "use strict";
  var DATA = window.PRODUCT_AGG || [];
  var CATS = window.PRODUCT_CATS || [];
  var PAGE = 60, shown = PAGE;
  var filtered = DATA.slice();
  var io = null;

  var elCatalog = document.getElementById("catalog");
  var elChips = document.getElementById("catChips");
  var elCount = document.getElementById("catCount");
  var elSearch = document.getElementById("catSearch");
  var elLoadMore = document.getElementById("loadMore");
  var elNoResult = document.getElementById("noResult");
  if (!elCatalog) return;

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

  function card(item, i) {
    var count = item.count || 1;
    return '' +
      '<div class="prod" data-card="' + i + '">' +
        '<div class="thumb">' +
          '<img data-src="' + esc(item.thumb) + '" alt="' + esc(item.name) + '" loading="lazy" />' +
          (count > 1 ? '<span class="style-count">' + count + ' colours</span>' : '') +
        '</div>' +
        '<div class="body">' +
          '<h3>' + esc(item.name) + '</h3>' +
          '<p class="meta">' + esc(item.catCn) + (count > 1 ? ' · ' + count + ' options' : '') + '</p>' +
          '<div class="tags"><span class="tag">' + esc(item.base) + '</span></div>' +
        '</div>' +
      '</div>';
  }

  function render(reset) {
    if (reset) { elCatalog.innerHTML = ""; shown = PAGE; }
    var slice = filtered.slice(0, shown);
    var html = "", lastCat = null;
    for (var k = 0; k < slice.length; k++) {
      var item = slice[k];
      if (item.cat !== lastCat) {
        var c = CATS.find(function (x) { return x.slug === item.cat; });
        html += '<section class="cat-section" id="' + esc(item.cat) + '"><h2>' +
                esc(c ? c.en : item.cat) + ' <small>' +
                filtered.filter(function (x) { return x.cat === item.cat; }).length + ' styles</small></h2>' +
                '<div class="prod-grid">';
        if (lastCat !== null) html += '</div></section>';
        lastCat = item.cat;
      }
      html += card(item, filtered.indexOf(item));
    }
    if (lastCat !== null) html += '</div></section>';
    elCatalog.innerHTML = html;

    elCatalog.querySelectorAll("img[data-src]").forEach(function (img) {
      if (io) io.observe(img); else img.src = img.dataset.src;
    });
    elCatalog.querySelectorAll("[data-card]").forEach(function (node) {
      node.addEventListener("click", function () { openLightbox(parseInt(node.dataset.card, 10)); });
    });
    if (elLoadMore) elLoadMore.style.display = shown < filtered.length ? "block" : "none";
    if (elNoResult) elNoResult.style.display = filtered.length ? "none" : "block";
    if (elCount) elCount.textContent = filtered.length + " style" + (filtered.length === 1 ? "" : "s");
  }

  if (elChips) {
    var all = '<button class="chip active" data-cat="all">All (' + DATA.length + ')</button>';
    CATS.forEach(function (c) {
      all += '<button class="chip" data-cat="' + esc(c.slug) + '">' + esc(c.en) + ' (' + c.count + ')</button>';
    });
    elChips.innerHTML = all;
    elChips.addEventListener("click", function (e) {
      var b = e.target.closest(".chip"); if (!b) return;
      elChips.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      var cat = b.dataset.cat;
      var q = (elSearch && elSearch.value || "").trim().toLowerCase();
      filtered = applyFilter(cat, q);
      render(true);
      if (cat !== "all") { var t = document.getElementById(cat); if (t) t.scrollIntoView({ behavior: "smooth", block: "start" }); }
    });
  }

  function applyFilter(cat, q) {
    return DATA.filter(function (x) {
      var okCat = cat === "all" || x.cat === cat;
      if (!okCat) return false;
      if (!q) return true;
      var hay = x.name + " " + x.base + " " + x.catCn + " " + x.catEn +
        x.variants.map(function (v) { return v.name + " " + v.cn + " " + v.color + " " + v.sku; }).join(" ");
      return hay.toLowerCase().indexOf(q) >= 0;
    });
  }

  if (elSearch) {
    var timer;
    elSearch.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        var activeCat = elChips ? (elChips.querySelector(".chip.active") || {}).dataset.cat : "all";
        filtered = applyFilter(activeCat || "all", elSearch.value.trim().toLowerCase());
        render(true);
      }, 180);
    });
  }
  if (elLoadMore) elLoadMore.addEventListener("click", function () { shown += PAGE; render(false); });

  // --- lightbox: photo stage + variant list ---
  var lb = document.getElementById("lb"), lbImg = document.getElementById("lbImg");
  var lbTitle = document.getElementById("lbTitle"), lbDesc = document.getElementById("lbDesc");
  var lbProducts = document.getElementById("lbProducts");
  var lbCount = document.getElementById("lbCount"), lbDots = document.getElementById("lbDots");
  var lbIndex = 0, shotIndex = 0, currentItem = null;

  function shots(item) { return item.variants && item.variants.length ? item.variants : [{ name:item.name, cn:item.base, color:"", thumb:item.thumb, file:item.file, sku:"" }]; }

  function showShot() {
    if (!currentItem) return;
    var ss = shots(currentItem);
    if (shotIndex >= ss.length) shotIndex = 0;
    if (shotIndex < 0) shotIndex = ss.length - 1;
    var v = ss[shotIndex];
    lbImg.src = v.file || v.thumb;
    lbImg.alt = v.name;
    if (lbCount) lbCount.textContent = ss.length > 1 ? (shotIndex + 1) + " / " + ss.length : "";
    if (lbDots) {
      lbDots.innerHTML = "";
      if (ss.length > 1) {
        ss.forEach(function (_, i) {
          var dot = document.createElement("button");
          dot.className = "lb-dot" + (i === shotIndex ? " active" : "");
          dot.type = "button"; dot.setAttribute("aria-label", "Option " + (i + 1));
          dot.addEventListener("click", function () { shotIndex = i; showShot(); highlightVariant(); });
          lbDots.appendChild(dot);
        });
      }
    }
    highlightVariant();
  }

  function highlightVariant() {
    if (!lbProducts) return;
    lbProducts.querySelectorAll("[data-v]").forEach(function (n) {
      n.style.borderColor = (parseInt(n.dataset.v, 10) === shotIndex) ? "var(--c-accent)" : "";
    });
  }

  function openLightbox(i) {
    if (!lb || !filtered[i]) return;
    lbIndex = i; shotIndex = 0; currentItem = filtered[i];
    lbTitle.textContent = currentItem.name;
    lbDesc.textContent = currentItem.catCn + " · " + (currentItem.count || 1) + " option" + (currentItem.count === 1 ? "" : "s") +
      ". Tell us the colour, size and quantity you need.";
    var ss = shots(currentItem);
    var html = '<div class="lb-mats-head"><span>Available options</span><span>' + ss.length + ' colours / sizes</span></div><div class="lb-mats">';
    ss.forEach(function (v, vi) {
      html += '<button type="button" class="lb-mini" data-v="' + vi + '">' +
        '<img src="' + esc(v.thumb || v.file) + '" alt="' + esc(v.name) + '" />' +
        '<span class="lb-mini-txt"><strong>' + esc(v.color ? (v.name.replace(/\s*-\s*[^-]+$/, "")) + " · " + v.color : v.name) + '</strong>' +
        '<small>' + esc(v.cn || v.sku || "") + '</small></span></button>';
    });
    html += '</div>';
    lbProducts.innerHTML = html;
    lbProducts.querySelectorAll("[data-v]").forEach(function (n) {
      n.addEventListener("click", function () { shotIndex = parseInt(n.dataset.v, 10); showShot(); });
    });
    showShot();
    lb.classList.add("open"); document.body.style.overflow = "hidden";
  }
  function closeLightbox() { if (lb) lb.classList.remove("open"); document.body.style.overflow = ""; }
  function step(d) {
    if (!currentItem) return;
    var ss = shots(currentItem), next = shotIndex + d;
    if (next >= 0 && next < ss.length) { shotIndex = next; showShot(); return; }
    var ni = (lbIndex + d + filtered.length) % filtered.length;
    openLightbox(ni);
    if (d > 0) shotIndex = 0; else shotIndex = shots(filtered[ni]).length - 1;
    showShot();
  }
  if (document.getElementById("lbClose")) document.getElementById("lbClose").addEventListener("click", closeLightbox);
  if (document.getElementById("lbPrev")) document.getElementById("lbPrev").addEventListener("click", function () { step(-1); });
  if (document.getElementById("lbNext")) document.getElementById("lbNext").addEventListener("click", function () { step(1); });
  if (lb) lb.addEventListener("click", function (e) { if (e.target === lb) closeLightbox(); });
  document.addEventListener("keydown", function (e) {
    if (!lb || !lb.classList.contains("open")) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
  });

  render(true);
  // deep link ?q= keyword (used by on-site "shop the look")
  try {
    var qs = new URLSearchParams(location.search).get("q") || "";
    if (qs) {
      if (elSearch) elSearch.value = qs;
      filtered = applyFilter("all", qs.trim().toLowerCase());
      render(true);
    } else if (location.hash) {
      var b = elChips ? elChips.querySelector('[data-cat="' + location.hash.slice(1) + '"]') : null;
      if (b) b.click();
    }
  } catch (e) {}
})();
