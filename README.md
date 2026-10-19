# youzan-store-design

一个给 Claude Code 用的 skill：把「有赞微商城的店铺装修 + 商品上架」整套流程交给 Claude 做。

- **本地出图**：从 PRD 或商品资料提炼商品表与文案禁区，用 HTML + Chrome 无头渲染批量生成商品主图、商详长图、首页和个人中心配图，渲染后自查再交付。
- **后台操作**：通过 Claude in Chrome 在有赞商家后台创建或编辑商品（主图、详情、卖点、类目、留言、限购、售后、仓库或上架），搭建并发布店铺主页、个人中心，调整购物车与底部导航。
- **安全闸门**：上架、发布、店铺级设置、删除都会先停下来请你确认。

`references/youzan-backend.md` 是实测的有赞后台操作手册，记录了每个页面的入口、字段定位和踩过的坑。

## 安装

```bash
git clone https://github.com/zoey1108/youzan-store-design ~/.claude/skills/youzan-store-design
```

之后在 Claude Code 里说「给我的有赞店做一套商品图」「把这几个套餐上架到有赞」「改一下店铺首页」即可触发。

## 依赖

- macOS + Google Chrome（无头渲染）
- Python 3 + Pillow（`pip install pillow`）
- Claude in Chrome 扩展，且 Chrome 已登录你的有赞商家后台（后台操作部分需要）

## 目录

```
SKILL.md                      流程总纲（触发条件、六个阶段、确认闸门）
references/youzan-backend.md  有赞后台操作手册（实测踩坑）
references/design-rules.md    视觉与文案规则、自查清单
scripts/render_tools.py       HTML→PNG、裁底、切片、拼总览、拼长图
assets/example-demo/          完整参考实现（虚构品牌「示例学堂」）
```

参考实现里的品牌、商品、次数和文案都是虚构的，只用来演示结构。
