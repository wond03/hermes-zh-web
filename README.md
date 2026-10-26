# hermes-zh · Hermes 控制台中文增强插件

给 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 的网页控制台补中文——**作为插件运行，不改源码、不需要重新构建前端、升级 Hermes 也不会被冲掉**。

覆盖 2600+ 条界面文案：侧边栏、对话、会话、文件、模型、配置（含 908 条字段说明）、渠道、密钥、系统、成就，以及**插件市场 860+ 个插件的简介**。

## 安装

**方式一：控制台里装（推荐）**

控制台 → 插件 → 「从 GitHub / Git 地址安装」→ 填：

```
wond03/hermes-zh-plugin
```

勾上「安装后启用」→ 安装 → 刷新页面。

> 安装完可能会提示「Custom (unreviewed) source — not from the Hermes catalog」，这是**来源提示**，不是安全拦截：插件会经过 Hermes 的安全扫描，扫描结果是通过的。点确认即可。

**方式二：手动放目录**

```bash
git clone https://github.com/wond03/hermes-zh-plugin ~/.hermes/plugins/hermes-zh
hermes config set plugins.enabled '["hermes-zh"]'
systemctl restart hermes-dashboard
```

装好后刷新浏览器：侧边栏多出一个「中文增强」页（`/hermes-zh`，说明 + 停用按钮），其余界面文案变中文。

> 插件市场里已经有一个同名的 `hermes-zh`（别人的简体中文语言包，只覆盖 `approval.*` / `gateway.*` 一小块）。从 GitHub 安装到同名目录会覆盖，装之前先确认 `~/.hermes/plugins/hermes-zh` 是空的。

## 关闭 / 恢复 / 卸载

**临时关掉（保留插件，随时开回来）**

1. 侧边栏「中文增强」→ 点「停用中文（界面回到英文）」→ 页面自动刷新，立刻是英文
2. 「插件」页 → 已安装插件 → `hermes-zh` → 「停用」
3. 命令行：

```bash
hermes config set plugins.enabled '[]'
systemctl restart hermes-dashboard
```

停用后刷新浏览器即生效，不用重启服务。恢复：「插件」页 → `hermes-zh` → 「启用」→ 刷新。

**彻底卸载**

```bash
rm -rf ~/.hermes/plugins/hermes-zh
hermes config set plugins.enabled '[]'
systemctl restart hermes-dashboard
```

或在「插件」页点「卸载」。

## 更新词典

```bash
# 维护者：改词表 → 重新生成 → 提交
vim dict/ui_zh.json          # 界面文案
vim dict/catalog_zh.json     # 插件市场简介
python3 tools/build.py
git commit -am "i18n: +N 词条" && git push
```

用户侧：「插件」页点「更新」或「强制重装」，刷新即可——不用重启服务，也不用构建前端。

插件市场的简介是**机器翻译**，随上游 catalog 变化会逐渐过期。重新跑一遍抓取 + 翻译：

```bash
python3 tools/translate_catalog.py   # 需要 DEEPSEEK_API_KEY，断点续跑
```

## 工作原理

插件加载 `dashboard/dist/index.js`（142KB），它：

1. 内置核心词典 1722 条（界面文案 + 配置字段说明）
2. 页面渲染后遍历文本节点与 `placeholder/title/aria-label`，精确匹配即替换
3. 用 `MutationObserver` 跟进 React 后续渲染
4. 跳过 `pre/code/input/textarea/终端/可编辑区`，文件名、日志、代码、输入内容不会被误翻
5. 空闲时（`requestIdleCallback`）再 fetch `dashboard/dist/catalog.json`（857 条插件简介），**不拖慢首屏**

## 未收录文案自动翻译（可选，默认关）

词库覆盖不到的地方（第三方插件的按钮、上游新加的文案），可以在「中文增强」页打开**自动翻译**：

- 接口：[bilibili/Index-Translate](https://github.com/bilibili/Index-Translate) 的公开端点（35B 翻译模型，免费、无需 key、允许跨域）
- 带术语提示（board=看板、triage=待分诊、worker=执行器……），一次批量 12 条
- 只翻**短英文句**：跳过品牌名（Anthropic、DeepSeek 等）、聊天内容、日志、文件名、输入框
- 结果缓存在浏览器 `localStorage`，翻一次不再请求
- 失败静默降级回英文，不影响使用

打开方式：插件页 →「中文增强」→「开启自动翻译」。介意文本发送到第三方就别开。

**默认是关闭的，装完不会发起任何外部请求**——纯本地词库替换，断网也能用。

## 只装插件够不够

| 场景 | 只装插件 | 说明 |
|---|---|---|
| 桌面浏览器日常使用 | **够** | 侧边栏、对话、会话、文件、模型、配置、渠道、密钥、系统、成就、插件市场都是中文 |
| 手机浏览器 | 可以用，但打字体验差 | 官方手机端把输入藏在终端隐藏输入框里，没有可见输入条；配套补丁才加显式输入框和图片/文件上传 |
| 登录页 | 英文（5 个词） | 登录前浏览器还没加载插件，够不到 |
| 插件名 / 仓库名 / 作者名 | 保留英文 | 翻了会搜不到、装错东西 |

需要手机输入条或会话删除修复时再装配套补丁 [hermes-cn-patch](https://github.com/wond03/hermes-cn-patch)；其余情况只装本插件即可。

## 已知限制

- 只处理**已经渲染出来的文本**；登录页、组件结构与交互（手机输入条、上传按钮）不在能力范围内。
- 插件市场简介为机器翻译，术语以原仓库说明为准；上游改了简介需要重跑一次翻译脚本。
- 有 5 个插件的简介保留英文：它们的原文含 `~/.ssh`、`Credential Manager`、`sudo` 这类字样，Hermes 的安装安全扫描会把它们判为高危（哪怕只是说明文字），只好不收录。
- 精确匹配，不做语义翻译：拼接出来的句子可能只翻一半。
- `aria-label` 也会被翻译，屏幕阅读器读中文。

## 许可

MIT。词典里的英文原文来自 Hermes Agent（MIT, © Nous Research）与第三方插件作者的公开简介。
