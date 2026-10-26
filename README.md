# hermes-zh · Hermes 控制台中文增强插件

给 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 的网页控制台补中文——**作为插件运行，不需要改源码、不需要重新构建前端**。

> 覆盖范围：组件里写死的英文界面文案（系统页、模型页、文件页、成就页、配置分类、渠道说明……共 830 条）。
> 词条文件、配置页字段说明、登录页、手机端输入栏仍需配套补丁：[hermes-cn-patch](https://github.com/<you>/hermes-cn-patch)。

## 安装

**方式一：从 GitHub 安装（推荐）**

控制台 → 插件 → 「从 GitHub / Git 地址安装」→ 填：

```
<your-account>/hermes-zh-plugin
```

勾上「安装后启用」→ 安装 → 刷新页面。

**方式二：手动放目录**

```bash
git clone https://github.com/<you>/hermes-zh-plugin ~/.hermes/plugins/hermes-zh
hermes config set plugins.enabled '["hermes-zh"]'   # 用户插件必须显式启用
systemctl restart hermes-dashboard
```

装好后刷新浏览器，侧边栏不会多出页面（它是纯运行时增强），但英文界面文案会变中文。

## 更新词典

```bash
# 维护者：改词典 → 重新生成 bundle → 提交
vim dict/ui_zh.json
python3 tools/build.py
git commit -am "i18n: +N 词条" && git push
```

用户侧：插件页点「更新」或「强制重装」，刷新即可——**不用重启服务，也不用重新构建前端**。

## 工作原理

插件 bundle 在控制台启动时被加载（`/dashboard-plugins/hermes-zh/dist/index.js`），它：

1. 把 `dict/ui_zh.json` 编译进 bundle（830 条精确匹配 + 10 条动态规则：`15h ago` → `15 小时前` 等）
2. 页面渲染后遍历文本节点与 `placeholder/title/aria-label`，命中即替换
3. 用 `MutationObserver` 跟进 React 后续渲染
4. 跳过 `pre/code/input/textarea/终端/可编辑区`，所以文件名、日志、代码、输入内容不会被误翻

## 边界

- 只处理**已经渲染出来的文本**；`zh.ts` 词条（编译期打包）、配置页字段说明（Python schema）、登录页（服务端 HTML）、手机端输入栏布局都不在能力范围内。
- 精确匹配，不做语义翻译：拼接出来的句子可能只翻一半。
- `aria-label` 也会被翻译，屏幕阅读器读中文。

## 许可

MIT。词典里的英文原文来自 Hermes Agent（MIT, © Nous Research）。
