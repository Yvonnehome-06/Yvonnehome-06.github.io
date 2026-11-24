/* Evonne Flora Co. on-site gallery — browse 83 real installations by scene
   and colour palette, then shop the products behind each look. Vanilla JS. */
(function () {
  "use strict";
  // Cases merged into a same-scene group are hidden from browsing; the kept
  // case carries images[] with every photo in that group.
  var DATA = (window.ONSITE_CASES || []).filter(function(x){ return !x.mergedInto; });
  var SCENES = window.ONSITE_SCENES || [];
  var COLORS = window.ONSITE_COLORS || [];
  var PRODUCTS = window.LOOK_PRODUCTS || {};

  var elGrid = document.getElementById("onsiteGrid");
  var elSceneGrid = document.getElementById("sceneGrid");
  var elSceneChips = document.getElementById("sceneChips");
  var elColorChips = document.getElementById("colorChips");
  var elEmpty = document.getElementById("onsiteEmpty");
  var elCount = document.getElementById("onsiteCount");
  var elTitle = document.getElementById("resultTitle");
  var elLook = document.getElementById("lookPanel");
  if (!elGrid) return;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function bySlug(list, slug) { for (var i=0;i<list.length;i++) if (list[i].slug===slug) return list[i]; return null; }
  function sceneName(slug) { var s=bySlug(SCENES,slug); return s ? s.en : slug; }
  function colorObj(slug) { return bySlug(COLORS,slug); }
  function countForScene(slug) { return DATA.filter(function(x){return x.scene===slug;}).length; }

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

  var activeScene = "all", activeColor = "all", current = [];

  // --- scene cover cards ---
  function renderSceneCards() {
    if (!elSceneGrid) return;
    var html = "";
    SCENES.forEach(function (s) {
      var n = countForScene(s.slug);
      if (!n) return;
      var cover = DATA.find(function(x){return x.scene===s.slug;});
      html += '<a class="scene-card" data-scene="'+esc(s.slug)+'" href="#gallery">' +
        '<img data-src="'+esc(cover.thumb)+'" alt="'+esc(s.en)+'" loading="lazy" />' +
        '<div class="sc-body"><h3>'+esc(s.en)+'</h3><span>'+n+' installations</span></div></a>';
    });
    elSceneGrid.innerHTML = html;
    elSceneGrid.querySelectorAll("img[data-src]").forEach(function(img){ if(io) io.observe(img); else img.src=img.dataset.src; });
    elSceneGrid.addEventListener("click", function (e) {
      var card = e.target.closest(".scene-card");
      if (!card) return;
      e.preventDefault();
      setScene(card.dataset.scene, true);
    });
  }

  // --- filter chips ---
  function renderChips() {
    if (elSceneChips) {
      var sh = '<button class="chip active" data-scene="all">All scenes ('+DATA.length+')</button>';
      SCENES.forEach(function(s){ var n=countForScene(s.slug); if(n) sh += '<button class="chip" data-scene="'+esc(s.slug)+'">'+esc(s.en)+' ('+n+')</button>'; });
      elSceneChips.innerHTML = sh;
      elSceneChips.addEventListener("click", function(e){
        var b=e.target.closest(".chip"); if(!b) return;
        setScene(b.dataset.scene, false);
      });
    }
    if (elColorChips) {
      var ch = '<button class="chip active" data-color="all">All colours</button>';
      COLORS.forEach(function(c){
        var n = DATA.filter(function(x){return x.colors.indexOf(c.slug)>=0;}).length;
        if(n) ch += '<button class="chip color-chip" data-color="'+esc(c.slug)+'"><span class="dot" style="background:'+esc(c.hex)+'"></span>'+esc(c.en)+' ('+n+')</button>';
      });
      elColorChips.innerHTML = ch;
      elColorChips.addEventListener("click", function(e){
        var b=e.target.closest(".chip"); if(!b) return;
        elColorChips.querySelectorAll(".chip").forEach(function(x){x.classList.remove("active");});
        b.classList.add("active");
        activeColor = b.dataset.color;
        render();
      });
    }
  }

  function setScene(slug, fromCard) {
    activeScene = slug;
    if (elSceneChips) elSceneChips.querySelectorAll(".chip").forEach(function(x){
      x.classList.toggle("active", x.dataset.scene === slug);
    });
    if (elSceneGrid) elSceneGrid.querySelectorAll(".scene-card").forEach(function(x){
      x.classList.toggle("active", x.dataset.scene === slug);
    });
    render();
    if (fromCard) {
      var t = document.getElementById("gallery");
      if (t) t.scrollIntoView({behavior:"smooth",block:"start"});
    }
  }

  // --- shop-the-look rail: aggregate products for the active scene/colour ---
  function renderLookPanel(list) {
    if (!elLook) return;
    if (activeScene === "all") { elLook.innerHTML = ""; return; }
    // round-robin across cases so one case with a long breakdown can't
    // crowd out every other look in the same scene
    var buckets = list.map(function(x){
      var b = [], seen = {};
      (x.products||[]).forEach(function(k){ if(PRODUCTS[k] && !seen[k]){seen[k]=1;b.push(k);} });
      return b;
    });
    var keys = [], seen = {}, i = 0, added = true;
    while (added && keys.length < 12) {
      added = false;
      for (var b = 0; b < buckets.length; b++) {
        var k = buckets[b][i];
        if (k && !seen[k]) { seen[k] = 1; keys.push(k); added = true; if (keys.length >= 12) break; }
      }
      i++;
    }
    if (!keys.length) { elLook.innerHTML = ""; return; }
    var cards = keys.map(function(k){
      var p = PRODUCTS[k];
      return '<a class="look-prod" href="products.html?q='+encodeURIComponent(p.n)+'">' +
        '<div class="lp-img"><img src="'+esc(p.t)+'" alt="'+esc(p.n)+'" loading="lazy" /></div>' +
        '<div class="lp-body"><h4>'+esc(p.n)+'</h4><span>'+esc(p.cn || p.c)+'</span></div></a>';
    }).join("");
    var s = bySlug(SCENES, activeScene);
    elLook.innerHTML = '<div class="look-panel">' +
      '<p class="section-label">Products that create this look</p>' +
      '<h2>'+esc(s ? s.en : activeScene)+'</h2>' +
      '<p class="look-intro">These are the flowers and greenery used across the '+esc((s?s.en:activeScene).toLowerCase())+' scenes below. Click any piece to find it in the catalog — colours and stem lengths can be selected to match your palette.</p>' +
      '<div class="look-grid">'+cards+'</div></div>';
  }

  // --- "inside the look" breakdown: full material list for cases that have one ---
  var elBdSection = document.getElementById("breakdownSection");
  var elBdTitle = document.getElementById("bdTitle");
  var elBdIntro = document.getElementById("bdIntro");
  var elBdPanel = document.getElementById("breakdownPanel");

  // material groups are dynamic — a case can have any number (blooms / accents / foliage)
  function matGroups(x) {
    var m = x.materials; if (!m) return [];
    return Object.keys(m).map(function(g){
      var grp = m[g];
      if (!grp || !grp.items || !grp.items.length) return null;
      return { key:g, label:grp.label || g, blurb:grp.blurb || "", items:grp.items };
    }).filter(Boolean);
  }

  function renderBreakdown(list) {
    if (!elBdSection || !elBdPanel) return;
    var withMat = list.filter(function(c){ return c.materials; });
    if (!withMat.length) { elBdSection.style.display = "none"; elBdPanel.innerHTML = ""; return; }
    elBdSection.style.display = "";

    var total = 0;
    withMat.forEach(function(c){ matGroups(c).forEach(function(g){ total += g.items.length; }); });

    if (withMat.length === 1) {
      elBdTitle.textContent = withMat[0].title;
      elBdIntro.textContent = "Every piece in this installation, broken down by what it does. " +
        total + " materials in all — click any of them to find the matching SKU in the catalog.";
    } else {
      elBdTitle.textContent = "Installations, broken down";
      elBdIntro.textContent = "Every piece in these installations, broken down by what it does. " +
        total + " materials in all — click any of them to find the matching SKU in the catalog.";
    }

    var panels = "";
    withMat.forEach(function(x){
      var groups = "";
      matGroups(x).forEach(function(g){
        groups += '<div class="bd-group"><h3>'+esc(g.label)+'</h3>' +
          (g.blurb ? '<p>'+esc(g.blurb)+'</p>' : '') + '<div class="bd-list">';
        g.items.forEach(function(it){
          var p = PRODUCTS[it.k]; if (!p) return;
          groups += '<a class="bd-item" href="products.html?q='+encodeURIComponent(p.n)+'">' +
            '<img src="'+esc(p.t)+'" alt="'+esc(p.n)+'" loading="lazy" />' +
            '<div class="bd-txt"><h4>'+esc(p.n)+'</h4>' +
            '<span class="bd-cn">'+esc(p.cn||p.c)+'</span>' +
            '<span class="bd-role">'+esc(it.role||'')+'</span></div></a>';
        });
        groups += '</div></div>';
      });
      panels += '<div class="bd-block">' +
        (withMat.length > 1
          ? '<h3 class="bd-case-title">'+esc(x.title)+
            '<span>'+esc(sceneName(x.scene))+'</span></h3>'
          : '') +
        '<div class="bd-case">' +
          '<div class="bd-shot"><img src="'+esc(x.img)+'" alt="'+esc(x.title)+'" /></div>' +
          '<div>'+groups+'</div></div></div>';
    });

    elBdPanel.innerHTML = panels;
  }

  function render() {
    current = DATA.filter(function(x){
      var okScene = activeScene === "all" || x.scene === activeScene;
      var okColor = activeColor === "all" || x.colors.indexOf(activeColor) >= 0;
      return okScene && okColor;
    });
    elGrid.innerHTML = "";
    if (elCount) elCount.textContent = current.length + (current.length===1?" installation":" installations");
    if (elTitle) {
      var s = bySlug(SCENES, activeScene), c = colorObj(activeColor);
      elTitle.textContent = (activeScene!=="all" ? (s?s.en:activeScene) : "All installations") +
        (activeColor!=="all" ? " · " + (c?c.en:activeColor) : "");
    }
    if (!current.length) {
      if (elEmpty) elEmpty.style.display="block";
      renderLookPanel(current);
      renderBreakdown(current);
      return;
    }
    if (elEmpty) elEmpty.style.display="none";
    current.forEach(function(x){
      var node = document.createElement("div");
      node.className = "onsite-item";
      var nMat = 0;
      if (x.materials) {
        matGroups(x).forEach(function(g){ nMat += g.items.length; });
      } else { nMat = (x.products||[]).length; }
      var nPhotos = x.imageCount || (x.images ? x.images.length : 0);
      node.innerHTML =
        '<img data-src="'+esc(x.img)+'" alt="'+esc(x.title)+'" loading="lazy" />' +
        (nPhotos > 1 ? '<span class="photo-count">1 / '+nPhotos+'</span>' : '') +
        '<div class="onsite-cap"><h3>'+esc(x.title)+'</h3><p>'+esc(sceneName(x.scene))+'</p>' +
        '<span class="look-btn">View look →</span>' +
        (nPhotos > 1 ? '<span class="look-count">'+nPhotos+' photos</span>' : '') +
        (nMat && nPhotos <= 1 ? '<span class="look-count">'+nMat+' materials</span>' : '') +
        '</div>';
      elGrid.appendChild(node);
      node.addEventListener("click", function(){ openLightbox(current.indexOf(x)); });
    });
    elGrid.querySelectorAll("img[data-src]").forEach(function(img){ if(io) io.observe(img); else img.src=img.dataset.src; });
    renderLookPanel(current);
    renderBreakdown(current);
  }

  // --- lightbox with per-look product list ---
  var lb = document.getElementById("onsiteLb");
  var lbImg = document.getElementById("onsiteLbImg");
  var lbTitle = document.getElementById("onsiteLbTitle");
  var lbDesc = document.getElementById("onsiteLbDesc");
  var lbProds = document.getElementById("onsiteLbProducts");
  var lbCount = document.getElementById("onsiteLbCount");
  var lbDots = document.getElementById("onsiteLbDots");
  var lbIndex = 0, shotIndex = 0;

  function miniCard(k, role) {
    var p = PRODUCTS[k]; if (!p) return "";
    return '<a class="lb-mini" href="products.html?q='+encodeURIComponent(p.n)+'">' +
      '<img src="'+esc(p.t)+'" alt="'+esc(p.n)+'" />' +
      '<span>'+esc(p.n)+'<br><small>'+esc(p.cn||p.c)+'</small>' +
      (role ? '<em>'+esc(role)+'</em>' : '') + '</span></a>';
  }

  function materialGroups(x) {
    var html = "";
    matGroups(x).forEach(function(g){
      html += '<p class="lb-label">'+esc(g.label)+'</p><div class="lb-mats">';
      g.items.forEach(function(it){ html += miniCard(it.k, it.role); });
      html += '</div>';
    });
    return html;
  }

  function shotsOf(x) { return (x.images && x.images.length) ? x.images : [x.img]; }

  function showShot() {
    var x = current[lbIndex]; if (!x) return;
    var imgs = shotsOf(x);
    if (shotIndex >= imgs.length) shotIndex = 0;
    if (shotIndex < 0) shotIndex = imgs.length - 1;
    lbImg.src = imgs[shotIndex]; lbImg.alt = x.title + " — photo " + (shotIndex+1);
    if (lbCount) lbCount.textContent = imgs.length > 1 ? (shotIndex+1) + " / " + imgs.length : "";
    if (lbDots) {
      lbDots.innerHTML = "";
      if (imgs.length > 1) {
        imgs.forEach(function(src, i){
          var dot = document.createElement("button");
          dot.className = "lb-dot" + (i===shotIndex ? " active" : "");
          dot.type = "button";
          dot.setAttribute("aria-label", "Photo " + (i+1));
          dot.addEventListener("click", function(){ shotIndex=i; showShot(); });
          lbDots.appendChild(dot);
        });
      }
    }
  }

  function openLightbox(i) {
    if (!lb || !current[i]) return;
    lbIndex = i; shotIndex = 0;
    var x = current[i];
    lbTitle.textContent = x.title;
    lbDesc.textContent = x.desc + "  ·  " + sceneName(x.scene);
    var html = materialGroups(x);
    if (!html) {
      html = '<p class="lb-label">Products in this look</p>';
      (x.products||[]).forEach(function(k){ html += miniCard(k, ""); });
    }
    lbProds.innerHTML = html;
    showShot();
    lb.classList.add("open"); document.body.style.overflow="hidden";
  }
  function closeLightbox() { if(lb) lb.classList.remove("open"); document.body.style.overflow=""; }
  // Arrow keys / nav buttons page through photos of the current look first,
  // then move to the next look once the last photo is reached.
  function step(d) {
    if (!current.length) return;
    var imgs = shotsOf(current[lbIndex]);
    var next = shotIndex + d;
    if (next >= 0 && next < imgs.length) { shotIndex = next; showShot(); return; }
    var ni = (lbIndex + d + current.length) % current.length;
    openLightbox(ni);
    if (d > 0) shotIndex = 0; else shotIndex = shotsOf(current[ni]).length - 1;
    showShot();
  }
  if (document.getElementById("onsiteLbClose")) document.getElementById("onsiteLbClose").addEventListener("click", closeLightbox);
  if (document.getElementById("onsiteLbPrev")) document.getElementById("onsiteLbPrev").addEventListener("click", function(){step(-1);});
  if (document.getElementById("onsiteLbNext")) document.getElementById("onsiteLbNext").addEventListener("click", function(){step(1);});
  if (lb) lb.addEventListener("click", function(e){ if(e.target===lb) closeLightbox(); });
  document.addEventListener("keydown", function(e){
    if(!lb || !lb.classList.contains("open")) return;
    if(e.key==="Escape") closeLightbox();
    if(e.key==="ArrowLeft") step(-1);
    if(e.key==="ArrowRight") step(1);
  });

  var reset = document.getElementById("resetFilters");
  if (reset) reset.addEventListener("click", function(){
    activeScene="all"; activeColor="all";
    if(elSceneChips) elSceneChips.querySelectorAll(".chip").forEach(function(x){x.classList.toggle("active",x.dataset.scene==="all");});
    if(elColorChips) elColorChips.querySelectorAll(".chip").forEach(function(x){x.classList.toggle("active",x.dataset.color==="all");});
    if(elSceneGrid) elSceneGrid.querySelectorAll(".scene-card").forEach(function(x){x.classList.remove("active");});
    render();
  });

  renderSceneCards();
  renderChips();
  // gallery anchor target for scene-card scroll
  var meta = document.querySelector(".filter-meta");
  if (meta) meta.id = "gallery";

  // deep link: ?scene=wedding&color=pink — shareable filtered view
  try {
    var params = new URLSearchParams(location.search);
    var ps = params.get("scene"), pc = params.get("color"), pi = params.get("case");
    if (ps && (ps === "all" || bySlug(SCENES, ps))) activeScene = ps;
    if (pc && (pc === "all" || bySlug(COLORS, pc))) activeColor = pc;
    if (ps) {
      if (elSceneChips) elSceneChips.querySelectorAll(".chip").forEach(function(x){x.classList.toggle("active",x.dataset.scene===activeScene);});
      if (elSceneGrid) elSceneGrid.querySelectorAll(".scene-card").forEach(function(x){x.classList.toggle("active",x.dataset.scene===activeScene);});
    }
    if (pc && elColorChips) elColorChips.querySelectorAll(".chip").forEach(function(x){x.classList.toggle("active",x.dataset.color===activeColor);});
    render();
    // ?case=<id> opens that installation directly — shareable single-look link
    if (pi) {
      var idx = current.findIndex(function(x){ return String(x.id) === String(pi); });
      if (idx >= 0) openLightbox(idx);
    }
  } catch (e) {}
  render();
})();
