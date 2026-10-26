# hermes-zh · Hermes 控制台中文增强插件

给 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 的网页控制台补中文——**作为插件运行，不需要改源码、不需要重新构建前端**。

> 覆盖范围：组件里写死的英文界面文案（系统页、模型页、文件页、成就页、配置分类、渠道说明……共 1770 条）。
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

> 插件市场里已经有一个同名的 `hermes-zh`（别人的简体中文语言包）。从 GitHub 安装到同名目录会覆盖，装之前先看一眼 `~/.hermes/plugins/hermes-zh` 是不是空的。

装好后刷新浏览器：侧边栏多出一个「中文增强」页（`/hermes-zh`，只有说明和一个停用按钮），其余英文界面文案变中文。

## 关闭 / 恢复 / 卸载

**临时关掉（保留插件，随时开回来）**

三个入口任选：

1. 侧边栏「中文增强」→ 点「停用中文（界面回到英文）」→ 页面自动刷新，界面立刻是英文
2. 「插件」页 → 拉到「已安装插件」→ 找到 `hermes-zh` → 点「停用」
3. 命令行：

```bash
hermes config set plugins.enabled '[]'     # 只留这一项的话；有其它插件就保留它们的名字
systemctl restart hermes-dashboard
```

停用后**刷新浏览器就生效**，不用重启服务。想恢复：「插件」页 → `hermes-zh` → 「启用」→ 刷新。

**彻底卸载**

```bash
rm -rf ~/.hermes/plugins/hermes-zh
hermes config set plugins.enabled '[]'
systemctl restart hermes-dashboard
```

或在「插件」页点该插件的「卸载」（会连目录一起删）。

> 插件包里有 `plugin.yaml`，所以宿主把它当作正常用户插件：插件页的「启用 / 停用 / 更新 / 卸载」四个按钮都可用。

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

1. 把 `dict/ui_zh.json` 编译进 bundle（1770 条精确匹配 + 10 条动态规则：`15h ago` → `15 小时前` 等）
2. 页面渲染后遍历文本节点与 `placeholder/title/aria-label`，命中即替换
3. 用 `MutationObserver` 跟进 React 后续渲染
4. 跳过 `pre/code/input/textarea/终端/可编辑区`，所以文件名、日志、代码、输入内容不会被误翻

## 只装插件够不够

| 场景 | 只装插件 | 说明 |
|---|---|---|
| 桌面浏览器日常使用 | **够** | 侧边栏、对话、会话、文件、模型、配置、渠道、系统、成就都是中文；配置页 908 条字段说明也在词典里 |
| 手机浏览器 | 可以用，但打字体验差 | 官方的手机端把输入藏在终端隐藏输入框里，没有可见输入条；配套补丁才加显式输入框和图片/文件上传 |
| 登录页 | 英文（5 个词） | 登录前浏览器还没加载插件，够不到；影响很小 |
| 插件市场 / 技能市场 / MCP 目录 | 英文 | 第三方作者写的简介，翻了会失真，建议保持原样 |

需要手机输入条或会话删除修复时再装配套补丁 [hermes-cn-patch](https://github.com/<you>/hermes-cn-patch)；其余情况只装本插件即可。

## 边界

- 只处理**已经渲染出来的文本**；登录页（登录前不加载插件）、组件结构与交互（手机输入条、上传按钮）不在能力范围内。
- 精确匹配，不做语义翻译：拼接出来的句子可能只翻一半。
- `aria-label` 也会被翻译，屏幕阅读器读中文。

## 许可

MIT。词典里的英文原文来自 Hermes Agent（MIT, © Nous Research）。
