/* Evonne Flora Co. on-site gallery — browse 83 real installations by scene
   and colour palette, then shop the products behind each look. Vanilla JS. */
(function () {
  "use strict";
  var DATA = window.ONSITE_CASES || [];
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
    var keys = [], seen = {};
    list.forEach(function(x){
      (x.products||[]).forEach(function(k){ if(PRODUCTS[k] && !seen[k]){seen[k]=1;keys.push(k);} });
    });
    // prefer a balanced spread of flower types
    keys = keys.slice(0, 12);
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
      return;
    }
    if (elEmpty) elEmpty.style.display="none";
    current.forEach(function(x){
      var node = document.createElement("div");
      node.className = "onsite-item";
      node.innerHTML =
        '<img data-src="'+esc(x.img)+'" alt="'+esc(x.title)+'" loading="lazy" />' +
        '<div class="onsite-cap"><h3>'+esc(x.title)+'</h3><p>'+esc(sceneName(x.scene))+'</p>' +
        '<span class="look-btn">View look →</span></div>';
      elGrid.appendChild(node);
      node.addEventListener("click", function(){ openLightbox(current.indexOf(x)); });
    });
    elGrid.querySelectorAll("img[data-src]").forEach(function(img){ if(io) io.observe(img); else img.src=img.dataset.src; });
    renderLookPanel(current);
  }

  // --- lightbox with per-look product list ---
  var lb = document.getElementById("onsiteLb");
  var lbImg = document.getElementById("onsiteLbImg");
  var lbTitle = document.getElementById("onsiteLbTitle");
  var lbDesc = document.getElementById("onsiteLbDesc");
  var lbProds = document.getElementById("onsiteLbProducts");
  var lbIndex = 0;
  function openLightbox(i) {
    if (!lb || !current[i]) return;
    lbIndex = i;
    var x = current[i];
    lbImg.src = x.img; lbImg.alt = x.title;
    lbTitle.textContent = x.title;
    lbDesc.textContent = x.desc + "  ·  " + sceneName(x.scene);
    var html = "";
    (x.products||[]).forEach(function(k){
      var p = PRODUCTS[k]; if (!p) return;
      html += '<a class="lb-mini" href="products.html?q='+encodeURIComponent(p.n)+'">' +
        '<img src="'+esc(p.t)+'" alt="'+esc(p.n)+'" />' +
        '<span>'+esc(p.n)+'<br><small style="color:#A9A396">'+esc(p.cn||p.c)+'</small></span></a>';
    });
    lbProds.innerHTML = html;
    lb.classList.add("open"); document.body.style.overflow="hidden";
  }
  function closeLightbox() { if(lb) lb.classList.remove("open"); document.body.style.overflow=""; }
  function step(d) { if(current.length) openLightbox((lbIndex+d+current.length)%current.length); }
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
    var ps = params.get("scene"), pc = params.get("color");
    if (ps && (ps === "all" || bySlug(SCENES, ps))) activeScene = ps;
    if (pc && (pc === "all" || bySlug(COLORS, pc))) activeColor = pc;
    if (ps) {
      if (elSceneChips) elSceneChips.querySelectorAll(".chip").forEach(function(x){x.classList.toggle("active",x.dataset.scene===activeScene);});
      if (elSceneGrid) elSceneGrid.querySelectorAll(".scene-card").forEach(function(x){x.classList.toggle("active",x.dataset.scene===activeScene);});
    }
    if (pc && elColorChips) elColorChips.querySelectorAll(".chip").forEach(function(x){x.classList.toggle("active",x.dataset.color===activeColor);});
  } catch (e) {}
  render();
})();
