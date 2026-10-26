import json

zh = json.load(open("dict/ui_zh.json", encoding="utf-8"))
# 去掉会误伤的字串（太短或纯符号）
zh = {k: v for k, v in zh.items() if len(k) >= 3 and k.strip() == k and k != v}
pairs = ",\n".join(
    '    %s: %s' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False))
    for k, v in sorted(zh.items())
)

js = r"""/* Hermes 控制台中文覆盖层（zh overlay）
 * 作用：在中文界面下，把渲染出来的英文界面文案替换成中文。
 * 说明：字典按"英文原文 -> 中文"精确匹配，只翻译已知的界面文案，
 *      不碰终端输出、代码块、输入框内容和文件列表等数据。
 * 维护：词典在文件末尾 DICT 里，加词条即可；改完不需要重新构建前端，
 *      重新执行 /root/hermes-zh-patch/apply.sh 或直接刷新页面即可。
 */
(function () {
  "use strict";

  var DICT = {
__PAIRS__
  };

  var LOWER = {};
  for (var k in DICT) LOWER[k.toLowerCase()] = DICT[k];

  // 这些区域不翻译：终端、代码、输入框、编辑器
  var SKIP = "pre,code,textarea,input,select,option,script,style,.xterm,.xterm-rows,.xterm-screen,[contenteditable='true'],[data-no-zh]";

  function isZh() {
    var l = (document.documentElement.getAttribute("lang") || "").toLowerCase();
    if (l) return l.indexOf("zh") === 0;
    try {
      var s = localStorage.getItem("hermes-locale");
      if (s) return String(s).toLowerCase().indexOf("zh") === 0;
    } catch (e) {}
    return false;
  }

  // 带变量的动态文案用规则匹配
  var RULES = [
    [/^Running — messaging channels are online$/i, "运行中 — 消息渠道在线"],
    [/^Stopped — messaging channels are offline$/i, "已停止 — 消息渠道离线"],
    [/^every (\d+)h · last run (.+)$/i, "每 $1 小时 · 上次运行 $2"],
    [/^(\d+) hooks?$/i, "$1 个钩子"],
    [/^(\d+) of (\d+) channels configured\.?$/i, "$1/$2 个渠道已配置"],
    [/^(\d+) tasks? · all auto$/i, "$1 个任务 · 全部自动"],
    [/^(\d+) references? · (.+)$/i, "$1 个参考模型 · $2"],
    [/^(\d+)m ago$/i, "$1 分钟前"],
    [/^(\d+)h ago$/i, "$1 小时前"],
    [/^(\d+)d ago$/i, "$1 天前"],
    [/^just now$/i, "刚刚"],
  ];

  function lookup(t) {
    var hit = DICT[t] || LOWER[t.toLowerCase()];
    if (hit) return hit;
    for (var i = 0; i < RULES.length; i++) {
      if (RULES[i][0].test(t)) return t.replace(RULES[i][0], RULES[i][1]);
    }
    return null;
  }

  function skipped(node) {
    var el = node.nodeType === 1 ? node : node.parentElement;
    try {
      return !!(el && el.closest && el.closest(SKIP));
    } catch (e) {
      return false;
    }
  }

  function trNode(node) {
    var raw = node.nodeValue;
    if (!raw) return;
    var t = raw.trim();
    if (!t || t.length > 320) return;
    var hit = lookup(t);
    if (!hit) return;
    if (skipped(node)) return;
    node.nodeValue = raw.replace(t, hit);
  }

  var ATTRS = ["placeholder", "title", "aria-label"];
  function trAttrs(el) {
    if (!el.getAttribute) return;
    for (var i = 0; i < ATTRS.length; i++) {
      var v = el.getAttribute(ATTRS[i]);
      if (!v) continue;
      var hit = lookup(v.trim());
      if (hit) el.setAttribute(ATTRS[i], hit);
    }
  }

  function walk(root) {
    if (!root) return;
    if (root.nodeType === 3) { trNode(root); return; }
    if (root.nodeType !== 1) return;
    if (skipped(root)) return;
    trAttrs(root);
    var els = root.querySelectorAll("*");
    for (var i = 0; i < els.length; i++) trAttrs(els[i]);
    var tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var n, list = [];
    while ((n = tw.nextNode())) list.push(n);
    for (var j = 0; j < list.length; j++) trNode(list[j]);
  }

  var pending = [];
  var queued = false;
  function flush() {
    queued = false;
    var items = pending;
    pending = [];
    if (!isZh()) return;
    for (var i = 0; i < items.length; i++) {
      var nd = items[i];
      if (!nd || !nd.isConnected) continue;
      if (nd.nodeType === 3) trNode(nd);
      else walk(nd);
    }
  }
  function enqueue(node) {
    pending.push(node);
    if (queued) return;
    queued = true;
    (window.requestAnimationFrame || window.setTimeout)(flush, 16);
  }

  function start() {
    if (isZh()) walk(document.body);
    new MutationObserver(function (muts) {
      if (!isZh()) return;
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        if (m.type === "characterData") {
          if (m.target && m.target.parentElement && !skipped(m.target)) enqueue(m.target);
          continue;
        }
        for (var j = 0; j < m.addedNodes.length; j++) enqueue(m.addedNodes[j]);
      }
    }).observe(document.body, { childList: true, subtree: true, characterData: true });

    // 语言切换后重新扫一遍
    new MutationObserver(function () {
      if (isZh()) walk(document.body);
    }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  }

  // 停用开关（插件页里可切换），存在 localStorage，刷新后生效
  var DISABLE_KEY = "hermes:zh-disabled";
  function enabled() {
    try { return window.localStorage.getItem(DISABLE_KEY) !== "1"; } catch (e) { return true; }
  }

  var _start = start;
  start = function () {
    if (!enabled()) return;
    _start();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  // ---- 注册插件页（host 要求 bundle 调用 register()，否则显示"未注册"错误页）----
  function ZhPanel() {
    var SDK = window.__HERMES_PLUGIN_SDK__ || {};
    var R = SDK.React;
    if (!R) return null;
    var h = R.createElement;
    var muted = { color: "var(--text-tertiary, #888)", fontSize: 12, margin: "4px 0" };
    return h("div", { style: { padding: "20px 16px", maxWidth: 720, lineHeight: 1.8, fontSize: 14 } },
      h("h2", { style: { margin: "0 0 10px", fontSize: 18 } }, "中文增强"),
      h("p", { style: { margin: "0 0 6px" } },
        "运行时词典已加载 " + __COUNT__ + " 条，把控制台里写死的英文界面文案替换成中文。"),
      h("p", { style: { margin: "0 0 6px" } }, "状态：已启用"),
      h("p", { style: muted }, "不想用了就在「插件」页停用或卸载它，界面立刻回到英文。"),
      h("p", { style: muted },
        "只覆盖组件里写死的英文；词条文件、配置页字段说明、登录页、手机端输入栏由配套补丁负责。"),
      h("p", { style: muted }, "改词条：更新插件即可，不需要重新构建前端。")
    );
  }

  var PLUGINS = window.__HERMES_PLUGINS__;
  if (PLUGINS && PLUGINS.register) {
    PLUGINS.register("hermes-zh", ZhPanel);
  }
})();
"""

js = js.replace("__PAIRS__", pairs)
js = js.replace("__COUNT__", str(len(zh)))
open("dashboard/dist/index.js", "w", encoding="utf-8").write(js)
print("dashboard/dist/index.js", len(js), "bytes,", len(zh), "entries")
