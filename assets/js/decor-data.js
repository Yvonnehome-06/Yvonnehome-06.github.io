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
//   accents = Decor Accents        装饰物
//
// 目前图片待用户提供，数组为空 —— 页面会显示友好的"即将更新"占位。
// 用户发来图片文件夹路径后，把压缩好的图按下面格式逐条填入即可，无需改页面。
// ---------------------------------------------------------------
window.DECOR_DATA = [
  // 示例（取消注释即可预览效果）：
  // { img: "assets/img/decor/decor-001.jpg", cat: "drapery", title: "Ivory Drapery Backdrop", desc: "Flowing fabric panel for ceremony backdrops." },
];

window.DECOR_CATS = [
  { slug: "drapery", en: "Drapery & Backdrops", cn: "布幔 / 背景幔" },
  { slug: "sheers",  en: "Sheer Curtains",      cn: "纱帘" },
  { slug: "accents", en: "Decor Accents",       cn: "装饰物" },
];
