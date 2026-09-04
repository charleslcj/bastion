/* i18n.js — 中英切换,与主站同机制(data-en / data-zh)
 *
 * 为什么这个文件存在(2026-08-08):
 * Bastion 的客户段是 SGV / Inland Empire 的华人货代 —— 那批公司的负责人
 * (FMC 官方备案:David Liu · Molly Ren · Danfeng Wang · Simon Huang · Jessica Huang…)
 * 中文沟通远比英文顺。**普通话是这门生意唯一的成本优势(CAC≈0)**,
 * 而新建的三个成交页面(quote / carriers / rates)最初全是英文 —— 等于把护城河扔了。
 *
 * 机制刻意做得极简:
 *  · 纯静态,无依赖,GitHub Pages 直出
 *  · 记住选择(localStorage),下次进站不用再点
 *  · 首访按浏览器语言自动判定 zh-*,但用户点过就以用户为准
 *  · placeholder / title / aria-label 一并切换 —— 表单里的提示语才是最需要翻译的部分
 */
(function () {
  var KEY = "bastion_lang";

  function apply(lang) {
    document.documentElement.setAttribute("lang", lang === "zh" ? "zh-CN" : "en");
    var attrs = ["", "placeholder", "title", "aria-label"];
    document.querySelectorAll("[data-en],[data-zh-placeholder],[data-zh-title]")
      .forEach(function (el) {
        attrs.forEach(function (a) {
          var zh = el.getAttribute(a ? "data-zh-" + a : "data-zh");
          var en = el.getAttribute(a ? "data-en-" + a : "data-en");
          var val = lang === "zh" ? (zh || en) : (en || zh);
          if (val == null) return;
          if (!a) { el.innerHTML = val; } else { el.setAttribute(a, val); }
        });
      });
    // <option> 文本
    document.querySelectorAll("option[data-zh]").forEach(function (o) {
      var v = lang === "zh" ? o.getAttribute("data-zh") : o.getAttribute("data-en");
      if (v) o.textContent = v;
    });
    var btn = document.getElementById("langToggle");
    if (btn) btn.textContent = lang === "zh" ? "EN" : "中文";
    try { localStorage.setItem(KEY, lang); } catch (e) {}
  }

  function initial() {
    try {
      var saved = localStorage.getItem(KEY);
      if (saved) return saved;
    } catch (e) {}
    return /^zh/i.test(navigator.language || "") ? "zh" : "en";
  }

  document.addEventListener("DOMContentLoaded", function () {
    var lang = initial();
    apply(lang);
    var btn = document.getElementById("langToggle");
    if (btn) {
      btn.addEventListener("click", function () {
        lang = lang === "zh" ? "en" : "zh";
        apply(lang);
      });
    }
  });
})();
