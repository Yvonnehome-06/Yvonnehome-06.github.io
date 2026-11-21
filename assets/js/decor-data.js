// CEREMONY & EVENT DECOR DATA — 典礼配饰数据
// ---------------------------------------------------------------
// 每条记录一个对象，字段说明：
//   img  : 图片路径（相对站点根目录），例 "assets/img/decor/decor-001.jpg"
//   cat  : 子分类 slug，三选一：drapery | sheers | accents
//   title: 英文标题（海外客户看），例 "Ivory Sheer Curtain Panel"
//   desc : 英文一句话说明（可选），例 "Soft drape for wedding arches and backdrops."
//
// 子分类对应：
//   drapery = Drapery & Backdrops  布幔 / 背景幔
//   sheers  = Sheer Curtains       纱帘
//   accents = Ribbons & Accents     丝带与装饰物
//
// 目前含 3 款婚礼丝带（accents 子类），布幔/纱帘图样待用户提供后可继续按格式追加。
// ---------------------------------------------------------------
window.DECOR_DATA = [
  // 婚礼丝带（原独立分类，2026-11 并入典礼配饰 · 装饰物）
  { img: "assets/img/newitems/ribbons-1005.jpg", cat: "accents", title: "Wedding Sash Ribbon - 2 Pack", desc: "Wedding sash ribbon for chair backs, aisle decor and ceremony styling." },
  { img: "assets/img/newitems/ribbons-1006.jpg", cat: "accents", title: "Wedding Sash Ribbon - A Toast To Forever", desc: "Wedding sash ribbon for chair backs, aisle decor and ceremony styling." },
  { img: "assets/img/newitems/ribbons-1007.jpg", cat: "accents", title: "Wedding Sash Ribbon - Just Married", desc: "Wedding sash ribbon for chair backs, aisle decor and ceremony styling." },
];

window.DECOR_CATS = [
  { slug: "drapery", en: "Drapery & Backdrops", cn: "布幔 / 背景幔" },
  { slug: "sheers",  en: "Sheer Curtains",      cn: "纱帘" },
  { slug: "accents", en: "Ribbons & Accents",   cn: "丝带与装饰物" },
];
