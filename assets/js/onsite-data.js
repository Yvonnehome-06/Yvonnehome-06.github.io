// ONSITE GALLERY DATA — 现场效果图数据
// ---------------------------------------------------------------
// 每条记录一个对象，字段说明：
//   img  : 图片路径（相对站点根目录），例 "assets/img/onsite/onsite-001.jpg"
//   cat  : 分类 slug，四选一：wedding | event | holiday | retail
//   title: 英文标题（海外客户看），例 "Ivory Rose Wedding Arch"
//   desc : 英文一句话说明（可选），例 "A full arch built from our ivory roses."
//
// 分类对应：
//   wedding = Weddings 婚礼
//   event   = Events & Installations 活动美陈
//   holiday = Holiday Decor 节日装饰
//   retail  = Retail & Display 橱窗陈列
//
// 目前图片待用户提供，数组为空 —— 页面会显示友好的"即将更新"占位。
// 用户发来图片文件夹路径后，把压缩好的图按下面格式逐条填入即可。
// ---------------------------------------------------------------
window.ONSITE_DATA = [
  // 示例（取消注释即可预览效果）：
  // { img: "assets/img/onsite/onsite-001.jpg", cat: "wedding", title: "Ivory Rose Wedding Arch", desc: "A statement arch built from our ivory roses and greenery." },
];

window.ONSITE_CATS = [
  { slug: "wedding", en: "Weddings", cn: "婚礼现场" },
  { slug: "event",   en: "Events & Installations", cn: "活动美陈" },
  { slug: "holiday", en: "Holiday Decor", cn: "节日装饰" },
  { slug: "retail",  en: "Retail & Display", cn: "橱窗陈列" },
];
