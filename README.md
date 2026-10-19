# youzan-store-design

一个**与具体 AI agent 无关**的 skill：把「有赞微商城的店铺装修 + 商品上架」整套流程交给 AI agent 做。Claude Code、Codex、Cursor、Gemini CLI，或你自己基于 LLM 搭的 agent 都能用。

- **本地出图**：从 PRD 或商品资料提炼商品表与文案禁区，用 HTML + 无头浏览器批量生成商品主图、商详长图、首页和个人中心配图，渲染后自查再交付。
- **后台操作**：用任意浏览器自动化能力（agent 自带浏览器工具、浏览器扩展、Playwright/Puppeteer/CDP）操作已登录的有赞商家后台：创建或编辑商品（主图、详情、卖点、类目、留言、限购、售后、仓库或上架），搭建并发布店铺主页、个人中心，调整购物车与底部导航。
- **安全闸门**：上架、发布、店铺级设置、删除都会先停下来请你确认；不会替你输入密码。

`references/youzan-backend.md` 是实测的有赞后台操作手册，记录了每个页面的入口、字段定位和踩过的坑。

## 安装

**支持 Agent Skills（`SKILL.md`）格式的 agent**：把仓库克隆到该 agent 的 skills 目录。具体路径以各工具的文档为准，例如：

```bash
# Claude Code
git clone https://github.com/zoey1108/youzan-store-design ~/.claude/skills/youzan-store-design
# Codex CLI
git clone https://github.com/zoey1108/youzan-store-design ~/.codex/skills/youzan-store-design
```

**其他 agent**：克隆到项目里，在系统提示词、规则文件或 `AGENTS.md` 里写一句「处理有赞店铺任务时，先阅读 youzan-store-design/SKILL.md 并按其执行」。仓库根目录自带的 `AGENTS.md` 可以直接复用。

之后对 agent 说「给我的有赞店做一套商品图」「把这几个套餐上架到有赞」「改一下店铺首页」即可。

## 依赖

- Python 3 + Pillow：`pip install pillow`
- 出图用的浏览器，任选其一：
  - Chrome / Chromium / Edge（macOS、Linux、Windows 会自动查找，也可用环境变量 `CHROME_PATH` 指定）
  - Playwright：`pip install playwright && playwright install chromium`
- 后台操作：一个已登录有赞商家后台的浏览器，并且你的 agent 能驱动它，比如浏览器扩展，或用 `--remote-debugging-port` 启动 Chrome 后通过 CDP/Playwright 连接。

## 目录

```
SKILL.md                      流程总纲（触发条件、六个阶段、确认闸门、能力对照）
AGENTS.md                     给不支持 skill 格式的 agent 的入口说明
references/youzan-backend.md  有赞后台操作手册（实测踩坑）
references/design-rules.md    视觉与文案规则、自查清单
scripts/render_tools.py       跨平台 HTML→PNG、裁底、切片、拼总览、拼长图
assets/example-demo/          完整参考实现（虚构品牌「示例学堂」）
```

参考实现里的品牌、商品、次数和文案都是虚构的，只用来演示结构。
