// ONSITE GALLERY DATA — 现场效果图数据
// 每条记录：img 图片路径 / cat 分类 / title 英文标题 / desc 英文说明
// 分类：wedding 婚礼 | event 活动美陈 | holiday 节日装饰 | retail 橱窗陈列
// 后期加图：把压缩好的图放 assets/img/onsite/，按下面格式追加一条即可。
window.ONSITE_DATA = [
  { img: "assets/img/onsite/onsite-001.jpg", cat: "wedding", title: "Castle Entrance Floral Arch", desc: "An ivory and green floral arch framing a castle doorway." }, // 城堡婚礼拱门
  { img: "assets/img/onsite/onsite-002.jpg", cat: "wedding", title: "Garden Wedding Arch with Sheer Drapes", desc: "Lush greenery, ivory blooms and soft sheers for an outdoor ceremony." }, // 户外婚礼拱门
  { img: "assets/img/onsite/onsite-003.jpg", cat: "event", title: "Botanical Wall with Woven Hats", desc: "A colorful floral wall installation with hats and seasonal accents." }, // 室内装饰·花艺墙
  { img: "assets/img/onsite/onsite-004.jpg", cat: "event", title: "Indoor Floral Landscape", desc: "A full-height floral scene transforming an interior venue." }, // 室内造景
  { img: "assets/img/onsite/onsite-005.jpg", cat: "event", title: "Interior Floral Column", desc: "Ivory flowers and greenery cladding a venue column." }, // 店铺装饰·室内花艺柱
  { img: "assets/img/onsite/onsite-006.jpg", cat: "event", title: "Birthday Celebration Backdrop", desc: "A soft floral backdrop for a children’s birthday party." }, // 生日装饰
  { img: "assets/img/onsite/onsite-007.jpg", cat: "retail", title: "Storefront Entrance Florals", desc: "Floral arrangements framing a shop entrance." }, // 店面门口花艺
  { img: "assets/img/onsite/onsite-008.jpg", cat: "retail", title: "Cafe Facade in Bloom", desc: "A flower-filled storefront facade for a neighborhood cafe." }, // 咖啡店门头花艺
  { img: "assets/img/onsite/onsite-009.jpg", cat: "retail", title: "Lemon-Themed Window Display", desc: "A bright window display with florals, ribbons and fruit accents." }, // 橱窗装饰
];

window.ONSITE_CATS = [
  { slug: "wedding", en: "Weddings", cn: "婚礼现场" },
  { slug: "event",   en: "Events & Installations", cn: "活动美陈" },
  { slug: "holiday", en: "Holiday Decor", cn: "节日装饰" },
  { slug: "retail",  en: "Retail & Display", cn: "橱窗陈列" },
];
