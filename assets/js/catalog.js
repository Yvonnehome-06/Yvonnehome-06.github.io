/* Evonne Flora Co. catalog — vanilla JS, zero dependencies.
   Renders 960 products from flowers-data.js with category filter,
   live search, batched rendering and lightbox. */
(function () {
  "use strict";
  var DATA = window.FLOWER_DATA || [];
  var CATS = window.FLOWER_CATS || [];
  var PAGE = 60;                 // 每批渲染数量，避免一次 960 张卡顿
  var shown = PAGE;
  var filtered = DATA.slice();
  var io = null;

  var elCatalog = document.getElementById("catalog");
  var elChips = document.getElementById("catChips");
  var elCount = document.getElementById("catCount");
  var elSearch = document.getElementById("catSearch");
  var elLoadMore = document.getElementById("loadMore");
  var elNoResult = document.getElementById("noResult");
  if (!elCatalog) return;

  // 懒加载 observer
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
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function card(item, i) {
    var colorHint = "";
    var cm = item.name.match(/-\s*([^-]+)$/);
    if (cm) colorHint = cm[1].trim();
    return '' +
      '<div class="prod" data-lightbox="' + i + '">' +
        '<div class="thumb"><img data-src="' + esc(item.thumb) + '" alt="' + esc(item.name) + '" loading="lazy" /></div>' +
        '<div class="body">' +
          '<h3>' + esc(item.name) + '</h3>' +
          '<p class="meta">' + esc(item.catCn) + (colorHint ? ' · ' + esc(colorHint) : '') + '</p>' +
          '<div class="tags"><span class="tag">' + esc(item.sku || item.cn) + '</span></div>' +
        '</div>' +
      '</div>';
  }

  function render(reset) {
    if (reset) { elCatalog.innerHTML = ""; shown = PAGE; }
    var slice = filtered.slice(0, shown);
    // 按类别分组插标题
    var html = "", lastCat = null, startIdx = 0;
    for (var k = 0; k < slice.length; k++) {
      var item = slice[k];
      if (item.cat !== lastCat) {
        var c = CATS.find(function (x) { return x.slug === item.cat; });
        var anchor = item.cat;
        html += '<section class="cat-section" id="' + esc(anchor) + '"><h2>' +
                esc(c ? c.en : item.cat) + ' <small>' +
                filtered.filter(function (x) { return x.cat === item.cat; }).length + ' items</small></h2>' +
                '<div class="prod-grid">';
        if (lastCat !== null) html += '</div></section>';
        lastCat = item.cat;
      }
      html += card(item, filtered.indexOf(item));
    }
    if (lastCat !== null) html += '</div></section>';
    elCatalog.innerHTML = html;

    // 绑定懒加载
    elCatalog.querySelectorAll("img[data-src]").forEach(function (img) {
      if (io) io.observe(img);
      else img.src = img.dataset.src;
    });
    // 灯箱点击
    elCatalog.querySelectorAll("[data-lightbox]").forEach(function (node) {
      node.addEventListener("click", function () { openLightbox(parseInt(node.dataset.lightbox, 10)); });
    });
    // 加载更多
    if (elLoadMore) elLoadMore.style.display = shown < filtered.length ? "block" : "none";
    if (elNoResult) elNoResult.style.display = filtered.length ? "none" : "block";
    if (elCount) elCount.textContent = filtered.length + " product" + (filtered.length === 1 ? "" : "s");
  }

  // 分类 chips
  if (elChips) {
    var all = '<button class="chip active" data-cat="all">All (' + DATA.length + ')</button>';
    CATS.forEach(function (c) {
      all += '<button class="chip" data-cat="' + esc(c.slug) + '">' + esc(c.en) + ' (' + c.count + ')</button>';
    });
    elChips.innerHTML = all;
    elChips.addEventListener("click", function (e) {
      var b = e.target.closest(".chip");
      if (!b) return;
      elChips.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      var cat = b.dataset.cat;
      var q = (elSearch && elSearch.value || "").trim().toLowerCase();
      filtered = DATA.filter(function (x) {
        var okCat = cat === "all" || x.cat === cat;
        var okQ = !q || (x.name + " " + x.cn + " " + x.catCn + " " + (x.sku || "")).toLowerCase().indexOf(q) >= 0;
        return okCat && okQ;
      });
      render(true);
      if (cat !== "all") { var t = document.getElementById(cat); if (t) t.scrollIntoView({ behavior: "smooth", block: "start" }); }
    });
  }

  // 搜索
  if (elSearch) {
    var timer;
    elSearch.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        var q = elSearch.value.trim().toLowerCase();
        var activeCat = elChips ? (elChips.querySelector(".chip.active") || {}).dataset.cat : "all";
        activeCat = activeCat || "all";
        filtered = DATA.filter(function (x) {
          var okCat = activeCat === "all" || x.cat === activeCat;
          var okQ = !q || (x.name + " " + x.cn + " " + x.catCn + " " + (x.sku || "")).toLowerCase().indexOf(q) >= 0;
          return okCat && okQ;
        });
        render(true);
      }, 180);
    });
  }

  if (elLoadMore) {
    elLoadMore.addEventListener("click", function () { shown += PAGE; render(false); });
  }

  // 灯箱
  var lb = document.getElementById("lb"), lbImg = document.getElementById("lbImg"), lbCap = document.getElementById("lbCap");
  var lbIndex = 0;
  function openLightbox(i) {
    lbIndex = i;
    var it = filtered[i];
    if (!it || !lb) return;
    lbImg.src = it.file;
    lbImg.alt = it.name;
    lbCap.textContent = it.name + "  ·  " + (i + 1) + " / " + filtered.length;
    lb.classList.add("open");
    document.body.style.overflow = "hidden";
  }
  function closeLightbox() { if (lb) lb.classList.remove("open"); document.body.style.overflow = ""; }
  function step(d) { openLightbox((lbIndex + d + filtered.length) % filtered.length); }
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

  // 首屏渲染；支持 hash 直达分类 与 ?q= 关键词直达（供案例页“shop the look”链接使用）
  render(true);
  var qs = "";
  try { qs = new URLSearchParams(location.search).get("q") || ""; } catch (e) {}
  if (qs && elSearch) {
    elSearch.value = qs;
    var q = qs.trim().toLowerCase();
    filtered = DATA.filter(function (x) {
      return (x.name + " " + (x.cn || "") + " " + x.catCn + " " + (x.sku || "")).toLowerCase().indexOf(q) >= 0;
    });
    render(true);
  } else if (location.hash) {
    var id = location.hash.slice(1);
    var b = elChips ? elChips.querySelector('[data-cat="' + id + '"]') : null;
    if (b) b.click();
  }
})();
