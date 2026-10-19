"""有赞商品视觉生成器（参考实现）

示例数据：品牌「示例学堂」、商品、次数、文案均为虚构，仅演示结构。
图片里不放价格：价格以有赞商品价为准，调价不用改图。

用法：python3 build.py            生成全部主图 + 详情页
     python3 build.py nianka     只生成某个商品
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
HTML_DIR = ROOT / "html"
MAIN_DIR = ROOT / "主图"
DETAIL_DIR = ROOT / "详情页"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

AI_FEATURES = ["智能问答", "作文批改", "语音讲解", "练习生成"]
FREE_FEATURES = ["学习计划", "错题收藏", "每日一练", "单词本", "打印"]

MEMBERS = [
    dict(id="shouchong", name="体验会员", short="体验", months=1, dl=0, badge="新人专享", tone="orange",
         footer="仅限新用户 · 限购 1 次"),
    dict(id="yueka", name="月卡", short="月卡", months=1, dl=0, badge=None, tone="brown",
         footer="智能问答 · 作文批改 · 语音讲解 · 练习生成"),
    dict(id="jika", name="季卡", short="季卡", months=3, dl=30, badge=None, tone="brown",
         footer="含资料下载 · 开卡一次给满"),
    dict(id="bannianka", name="半年卡", short="半年卡", months=6, dl=60, badge=None, tone="brown",
         footer="含资料下载 · 开卡一次给满"),
    dict(id="nianka", name="年卡", short="年卡", months=12, dl=240, badge="推荐", tone="brown",
         footer="含资料下载 · 开卡一次给满"),
]
PACKS = [
    dict(id="mini", name="迷你包", dl=10, layers=1),
    dict(id="biaozhun", name="标准包", dl=20, layers=2),
    dict(id="dabao", name="大包", dl=40, layers=3),
]

# ---------- 图标（Feather 风格线性图标） ----------
ICONS = {
    "智能问答": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
    "作文批改": '<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "语音讲解": '<circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/>',
    "练习生成": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "资料下载": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "edit": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "phone": '<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
}
CROWN = '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M2.5 7.5l5 4 4.5-7 4.5 7 5-4-2 11h-15z"/><rect x="4.5" y="19.5" width="15" height="2" rx="1" fill="currentColor"/></svg>'
SPARK = '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 1.5l2.6 7.9 7.9 2.6-7.9 2.6L12 22.5l-2.6-7.9L1.5 12l7.9-2.6z"/></svg>'


def icon(name, size=40, stroke="currentColor"):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{stroke}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


# ---------- 公共样式（示例品牌色，按你的品牌替换） ----------
BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html{background:#010203}
body{font-family:'PingFang SC','Hiragino Sans GB',sans-serif;color:#5C3A1E;-webkit-font-smoothing:antialiased}
:root{--o1:#FFA040;--o2:#FF6B24;--o-line:#FF844C;--o-bg:#FFF0E8;--b1:#5C3A1E;--b2:#8C5A3C;--b3:#A8806A;--page:#F5F6F8;--gold1:#FFF1D0;--gold2:#E6BC74}
.brand{display:flex;align-items:center;gap:12px;font-weight:600;color:var(--b1)}
.logo{display:inline-grid;place-items:center;border-radius:12px;background:linear-gradient(135deg,var(--o1),var(--o2));color:#fff;font-weight:800}
.badge{color:#fff;font-weight:700;background:linear-gradient(135deg,var(--o1),var(--o2));border-radius:999px;box-shadow:0 6px 16px rgba(255,107,36,.28)}
.gold-text{background:linear-gradient(180deg,var(--gold1) 10%,var(--gold2) 90%);-webkit-background-clip:text;background-clip:text;color:transparent}
.meter{display:flex;gap:6px;justify-content:center;align-items:center}
.meter i{display:block;border-radius:999px;background:#F3E6DC}
.meter i.on:nth-child(1){background:linear-gradient(90deg,#FFCB94,#FFAE70)}
.meter i.on:nth-child(2){background:linear-gradient(90deg,#FFAE70,#FF8C48)}
.meter i.on:nth-child(3){background:linear-gradient(90deg,#FF8C48,#FF6B24)}
.tile .meter{height:57px}.tile .meter i{width:40px;height:16px}
.stat .meter{height:51px}.stat .meter i{width:34px;height:14px}
.tmeter{justify-content:center}.tmeter i{width:24px;height:10px}
"""

MAIN_CSS = BASE_CSS + """
.canvas{position:relative;width:800px;height:800px;overflow:hidden;padding:48px 56px}
.member{background:linear-gradient(180deg,#FFDCC2 0%,#FFF0E5 52%,#FFF9F4 100%)}
.pack{background:linear-gradient(180deg,#FFE3CF 0%,#FFF0E8 50%,#FFF9F5 100%)}
.deco{position:absolute;border-radius:50%;pointer-events:none}
.d1{width:520px;height:520px;right:-180px;top:-200px;background:radial-gradient(circle,rgba(255,255,255,.75),rgba(255,255,255,0) 70%)}
.d2{width:380px;height:380px;left:-160px;bottom:60px;background:radial-gradient(circle,rgba(255,160,64,.16),rgba(255,160,64,0) 70%)}
header{position:relative;display:flex;justify-content:space-between;align-items:center;height:56px}
header .brand{font-size:26px}
header .logo{width:48px;height:48px;font-size:26px}
header .badge{font-size:26px;padding:10px 26px}

/* 会员卡面 */
.card{position:relative;margin:34px auto 0;width:640px;height:340px;border-radius:36px;padding:34px 40px;overflow:hidden;
  box-shadow:0 24px 48px rgba(92,58,30,.28),inset 0 1px 0 rgba(255,255,255,.18)}
.card.brown{background:linear-gradient(135deg,#7A5030 0%,#4E3019 55%,#3A2312 100%);color:var(--gold2)}
.card.orange{background:linear-gradient(135deg,#FFB257 0%,#FF8A34 50%,#FF6B24 100%);color:#fff;box-shadow:0 24px 48px rgba(255,107,36,.32)}
.card .sheen{position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,0) 35%,rgba(255,255,255,.14) 48%,rgba(255,255,255,0) 60%)}
.card .ring{position:absolute;right:-90px;bottom:-120px;width:360px;height:360px;border-radius:50%;border:2px solid rgba(255,255,255,.12)}
.card .ring.r2{right:-30px;bottom:-60px;width:240px;height:240px}
.card-top{display:flex;align-items:center;gap:10px;font-size:24px;font-weight:600}
.card-top svg{width:34px;height:34px}
.card-top .mem{margin-left:auto;font-size:18px;letter-spacing:6px;opacity:.6;font-weight:500}
.card-name{margin-top:28px;display:flex;align-items:baseline;gap:14px}
.card-name b{font-size:120px;line-height:1;font-weight:800;letter-spacing:2px}
.card-name span{font-size:40px;font-weight:600}
.card.orange .card-name b{color:#fff;text-shadow:0 4px 12px rgba(180,60,0,.25)}
.card-bottom{position:absolute;left:40px;right:40px;bottom:30px;display:flex;justify-content:space-between;font-size:22px;opacity:.85}

/* 加量包插画 */
.stack{position:relative;margin:58px auto 0;width:380px;height:236px}
.layer{position:absolute;left:50%;width:300px;height:184px;border-radius:30px;transform:translateX(-50%);
  background:linear-gradient(135deg,var(--o1),var(--o2));box-shadow:0 18px 36px rgba(255,107,36,.30);
  display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;gap:8px}
.layer svg{width:64px;height:64px}
.layer b{font-size:30px;font-weight:700;letter-spacing:2px}
.layer.back{opacity:.55;box-shadow:none}
.pack-name{text-align:center;margin-top:14px;font-size:84px;color:var(--b1);font-weight:800;line-height:1.1}

/* 数据块 */
.tiles{position:relative;display:flex;gap:20px;margin-top:40px}
.pack .tiles{margin-top:26px}
.tile{flex:1;background:#fff;border-radius:24px;padding:22px 10px 20px;text-align:center;box-shadow:0 8px 24px rgba(140,90,60,.08)}
.tile .v{font-size:52px;font-weight:800;color:var(--o2);line-height:1.1}
.tile .v small{font-size:24px;font-weight:700;margin-left:4px}
.tile .k{margin-top:8px;font-size:22px;color:var(--b2)}
footer{position:absolute;left:0;right:0;bottom:44px;text-align:center;font-size:23px;color:var(--b3);letter-spacing:1px}
"""

DETAIL_CSS = BASE_CSS + """
.page{width:750px;background:var(--page);padding-bottom:48px}
.hero{position:relative;padding:44px 40px 40px;background:linear-gradient(180deg,#FFDCC2 0%,#FFF0E5 62%,var(--page) 100%);overflow:hidden}
.hero .brand{font-size:24px}
.hero .logo{width:44px;height:44px;font-size:24px}
.hero h1{margin-top:34px;font-size:64px;font-weight:800;line-height:1.15}
.hero .sub{margin-top:14px;max-width:400px;font-size:27px;color:var(--b2);line-height:1.6}
.hero .tag{display:inline-block;margin-top:22px;font-size:22px;padding:8px 22px}
.hero .art{position:absolute;right:-30px;top:96px;width:300px;height:190px;border-radius:30px;transform:rotate(-8deg);
  display:flex;flex-direction:column;justify-content:space-between;padding:24px 28px;box-shadow:0 20px 40px rgba(92,58,30,.25)}
.art.brown{background:linear-gradient(135deg,#7A5030,#3A2312);color:var(--gold2)}
.art.orange{background:linear-gradient(135deg,#FFB257,#FF6B24);color:#fff}
.art .t{display:flex;align-items:center;gap:8px;font-size:18px;font-weight:600}
.art .t svg{width:26px;height:26px}
.art b{font-size:60px;font-weight:800;line-height:1}
.sec{margin:24px 32px 0;background:#fff;border-radius:28px;padding:36px 32px}
.sec h2{display:flex;align-items:center;gap:12px;font-size:32px;font-weight:700}
.sec h2::before{content:"";width:8px;height:30px;border-radius:4px;background:linear-gradient(180deg,var(--o1),var(--o2))}
.sec .lead{margin-top:10px;font-size:23px;color:var(--b3);line-height:1.6}
.stats{display:flex;gap:16px;margin-top:26px}
.stat{flex:1;background:var(--o-bg);border-radius:20px;padding:22px 8px;text-align:center}
.stat .v{font-size:46px;font-weight:800;color:var(--o2);line-height:1.1}
.stat .v small{font-size:22px;margin-left:3px}
.stat .k{margin-top:8px;font-size:21px;color:var(--b2)}
.stat .n{margin-top:4px;font-size:18px;color:var(--b3)}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:28px}
.feat{text-align:center}
.feat .ic{width:84px;height:84px;margin:0 auto;border-radius:24px;background:var(--o-bg);display:grid;place-items:center;color:var(--o2)}
.feat .nm{margin-top:12px;font-size:22px;font-weight:600}
.feat .ds{margin-top:4px;font-size:18px;color:var(--b3);line-height:1.4}
.feat.off .ic{background:#F2F2F2;color:#C4C4C4}
.feat.off .nm{color:#B5B5B5}
.chips{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}
.chip{font-size:22px;padding:10px 20px;border-radius:999px;background:#F5F6F8;color:var(--b2)}
table{width:100%;margin-top:24px;border-collapse:separate;border-spacing:0;font-size:22px}
th,td{padding:18px 10px;text-align:center;border-bottom:1px solid #F1E6DE}
th{font-weight:600;color:var(--b2);font-size:21px}
td:first-child,th:first-child{text-align:left;padding-left:4px;color:var(--b1)}
tr.hl td{background:#FFF6F0;font-weight:700;color:var(--o2)}
tr.hl td:first-child{border-radius:14px 0 0 14px}
tr.hl td:last-child{border-radius:0 14px 14px 0}
.mini-badge{display:inline-block;margin-left:8px;font-size:16px;padding:2px 10px;border-radius:999px;color:#fff;background:linear-gradient(135deg,var(--o1),var(--o2));vertical-align:2px}
.cmp td.y{color:var(--o2);font-weight:600}
.cmp td.n{color:#C4C4C4}
.cmp .grp td{font-size:19px;color:var(--b3);padding:22px 4px 8px;border-bottom:none;text-align:left}
.steps{display:flex;gap:14px;margin-top:28px}
.step{flex:1;text-align:center;position:relative}
.step .ic{width:76px;height:76px;margin:0 auto;border-radius:50%;background:linear-gradient(135deg,var(--o1),var(--o2));color:#fff;display:grid;place-items:center}
.step .no{margin-top:12px;font-size:18px;color:var(--o2);font-weight:700;letter-spacing:2px}
.step .nm{margin-top:4px;font-size:22px;font-weight:600;line-height:1.4}
.step .ds{margin-top:6px;font-size:18px;color:var(--b3);line-height:1.5}
.hl-box{margin-top:26px;border:2px dashed var(--o-line);border-radius:20px;padding:20px 24px;background:#FFF8F4;font-size:23px;line-height:1.6}
.hl-box b{color:var(--o2)}
.notes{margin-top:22px;list-style:none}
.notes li{position:relative;padding-left:30px;font-size:22px;line-height:1.65;color:var(--b2);margin-top:12px}
.notes li::before{content:"";position:absolute;left:4px;top:13px;width:10px;height:10px;border-radius:50%;background:var(--o-line)}
.notes li b{color:var(--b1)}
.foot{margin:34px 32px 0;text-align:center;font-size:20px;color:var(--b3);line-height:1.7}
"""


def meter(on, cls=""):
    """三段式进度条：亮起的段数表示额度多少，不出现具体点数。"""
    return f'<div class="meter {cls}">' + "".join(f'<i class="{"on" if k < on else ""}"></i>' for k in range(3)) + "</div>"


def page(css, body):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


def brand_html():
    return '<div class="brand"><span class="logo">示</span><span>示例学堂 · AI 学习助手</span></div>'


# ---------- 主图 ----------
def main_member(m):
    badge = f'<span class="badge">{m["badge"]}</span>' if m["badge"] else ""
    name_cls = "" if m["tone"] == "orange" else "gold-text"
    second = (f'<div class="tile"><div class="v">{m["dl"]}<small>次</small></div><div class="k">资料下载</div></div>'
              if m["dl"] else
              '<div class="tile"><div class="v">4<small>项</small></div><div class="k">AI 功能全部可用</div></div>')
    body = f'''<div class="canvas member"><div class="deco d1"></div><div class="deco d2"></div>
<header>{brand_html()}{badge}</header>
<div class="card {m["tone"]}"><div class="ring"></div><div class="ring r2"></div><div class="sheen"></div>
  <div class="card-top">{CROWN}<span>示例学堂会员</span><span class="mem">MEMBER</span></div>
  <div class="card-name"><b class="{name_cls}">{m["short"]}</b><span>会员</span></div>
  <div class="card-bottom"><span>有效期 {m["months"]} 个月</span><span>AI 学习辅导</span></div>
</div>
<div class="tiles">
  <div class="tile">{meter(3)}<div class="k">每月 AI 权益</div></div>
  {second}
  <div class="tile"><div class="v">{m["months"]}<small>个月</small></div><div class="k">会员有效期</div></div>
</div>
<footer>{m["footer"]}</footer></div>'''
    return page(MAIN_CSS, body)


def main_pack(p):
    n = p["layers"]
    layers = []
    for i in range(n):  # 后层在前，层数代表包的大小
        depth = n - 1 - i
        top = 48 - depth * 24
        scale = 1 - depth * 0.08
        cls = "layer back" if depth else "layer"
        inner = "" if depth else f'{SPARK}<b>额度加量包</b>'
        layers.append(f'<div class="{cls}" style="top:{top}px;transform:translateX(-50%) scale({scale})">{inner}</div>')
    body = f'''<div class="canvas pack"><div class="deco d1"></div><div class="deco d2"></div>
<header>{brand_html()}<span class="badge">会员专享</span></header>
<div class="stack">{"".join(layers)}</div>
<div class="pack-name">{p["name"]}</div>
<div class="tiles">
  <div class="tile">{meter(p["layers"])}<div class="k">AI 权益补充</div></div>
  <div class="tile"><div class="v">{p["dl"]}<small>次</small></div><div class="k">资料下载</div></div>
  <div class="tile"><div class="v">1<small>年</small></div><div class="k">到账后有效</div></div>
</div>
<footer>仅限当前会员购买 · 可叠加购买</footer></div>'''
    return page(MAIN_CSS, body)


# ---------- 详情页 ----------
FEAT_DESC = {
    "智能问答": "拍照提问<br>即时解答",
    "作文批改": "上传作文<br>逐句点评",
    "语音讲解": "语音讲解<br>可随时追问",
    "练习生成": "按薄弱点<br>生成练习",
    "资料下载": "学习资料<br>PDF 下载",
}


def feature_grid(dl_on):
    cells = []
    for f in AI_FEATURES + ["资料下载"]:
        off = f == "资料下载" and not dl_on
        ds = "本套餐不含" if off else FEAT_DESC[f]
        cells.append(f'<div class="feat{" off" if off else ""}"><div class="ic">{icon(f, 40)}</div>'
                     f'<div class="nm">{f}</div><div class="ds">{ds}</div></div>')
    return f'<div class="grid">{"".join(cells)}</div>'


def free_section():
    chips = "".join(f'<span class="chip">{f}</span>' for f in FREE_FEATURES)
    return f'''<div class="sec"><h2>这些功能一直免费</h2>
<div class="lead">不开会员也能用，开了会员同样不占额度。</div><div class="chips">{chips}</div></div>'''


def steps_section():
    steps = [("edit", "下单时填写<br>App 账号手机号", "在商品留言里填写"),
             ("phone", "支付成功<br>即到账", "未注册的号码<br>注册后自动到账"),
             ("user", "打开示例学堂 App<br>会员中心查看", "用同一手机号登录")]
    cells = "".join(f'<div class="step"><div class="ic">{icon(i, 34)}</div><div class="no">STEP {n}</div>'
                    f'<div class="nm">{t}</div><div class="ds">{d}</div></div>'
                    for n, (i, t, d) in enumerate(steps, 1))
    return f'''<div class="sec"><h2>怎么开通</h2><div class="steps">{cells}</div>
<div class="hl-box">下单时请在留言<b>「App 账号手机号」</b>里填写使用 App 的手机号（家长或孩子的账号）。号码填错的，请联系客服退款后重新下单。</div></div>'''


def member_compare(current):
    rows = ['<tr><th>套餐</th><th>有效期</th><th>AI 权益</th><th>资料下载</th></tr>']
    for m in MEMBERS:
        if m["id"] == "shouchong" and current["id"] != "shouchong":
            continue
        badge = f'<span class="mini-badge">{m["badge"]}</span>' if m["badge"] else ""
        hl = ' class="hl"' if m["id"] == current["id"] else ""
        dl = f'{m["dl"]} 次' if m["dl"] else "不含"
        rows.append(f'<tr{hl}><td>{m["name"]}{badge}</td><td>{m["months"]} 个月</td><td>每月发放</td><td>{dl}</td></tr>')
    return f'''<div class="sec"><h2>套餐对比</h2>
<div class="lead">每月 AI 权益相同，有效期越长，资料下载次数越多。</div><table>{"".join(rows)}</table></div>'''


def free_vs_member(m):
    def row(name, free, paid):
        fc = "y" if free == "可用" else "n"
        pc = "n" if paid in ("—", "不含") else "y"
        return f'<tr><td>{name}</td><td class="{fc}">{free}</td><td class="{pc}">{paid}</td></tr>'
    dl = f'{m["dl"]} 次' if m["dl"] else "不含"
    rows = [f'<tr><th>功能</th><th>免费用户</th><th>{m["name"]}</th></tr>',
            '<tr class="grp"><td colspan="3">会员权益</td></tr>']
    rows += [row(f, "—", "可用") for f in AI_FEATURES]
    rows.append(row("资料下载", "—", dl))
    rows.append('<tr class="grp"><td colspan="3">免费功能</td></tr>')
    rows.append(row(f"学习计划、错题收藏等 {len(FREE_FEATURES)} 项", "可用", "可用"))
    return f'<div class="sec"><h2>免费用户 vs {m["name"]}</h2><table class="cmp">{"".join(rows)}</table></div>'


def detail_member(m):
    is_first = m["id"] == "shouchong"
    title = "体验会员" if is_first else f'{m["name"]}会员'
    tag = (f'<span class="badge tag">{m["badge"]}</span>' if m["badge"] else "")
    issues = m["months"]
    stats = [f'<div class="stat"><div class="v">{m["months"]}<small>个月</small></div><div class="k">会员有效期</div></div>',
             f'<div class="stat">{meter(3)}<div class="k">每月 AI 权益</div>'
             f'<div class="n">按月发放 · 共 {issues} 次</div></div>']
    if m["dl"]:
        stats.append(f'<div class="stat"><div class="v">{m["dl"]}<small>次</small></div><div class="k">资料下载</div>'
                     f'<div class="n">开卡一次给满</div></div>')
    else:
        stats.append('<div class="stat"><div class="v">4<small>项</small></div><div class="k">AI 功能全部可用</div>'
                     '<div class="n">资料下载需季卡及以上</div></div>')
    notes = [
        "<b>额度按月发放：</b>开卡当天发放首月AI 权益，之后每月同一天重新发放；当月未用完的到下次发放时清零，不结转。",
        "<b>不同功能消耗不同：</b>语音讲解、作文批改消耗较高，每一笔消耗都能在 App「会员中心 · 权益明细」里查到；快用完时会提醒。",
    ]
    if m["dl"]:
        notes.append("<b>资料下载次数：</b>开卡时一次给满，会员有效期内随时用，会员到期时剩余次数清零。")
    notes += [
        "<b>续费排队生效：</b>会员有效期内再次购买，新会员卡在当前会员到期后自动生效，不叠加、不顺延。",
        "<b>不够用怎么办：</b>会员可以在 App 内另购额度加量包。",
    ]
    if is_first:
        notes.insert(0, "<b>购买资格：</b>仅限新注册的示例学堂账号购买 1 次；老用户账号下单，系统会自动为你退款。")
    body = f'''<div class="page">
<div class="hero">{brand_html()}
  <div class="art {m["tone"]}"><div class="t">{CROWN}示例学堂会员</div><b class="{"" if m["tone"] == "orange" else "gold-text"}">{m["short"]}</b></div>
  <h1>{title}</h1>
  <div class="sub">开通会员，使用全部<br>AI 学习辅导功能<br>高算力 AI 能力每月配有服务额度</div>{tag}
</div>
<div class="sec"><h2>套餐内容</h2><div class="stats">{"".join(stats)}</div></div>
<div class="sec"><h2>会员权益</h2><div class="lead">AI 权益是统一额度，以下功能之间可以自由使用。</div>{feature_grid(bool(m["dl"]))}</div>
{free_section()}
{member_compare(m)}
{free_vs_member(m)}
{steps_section()}
<div class="sec"><h2>使用说明</h2><ul class="notes">{"".join(f"<li>{n}</li>" for n in notes)}</ul></div>
{purchase_notes()}
<div class="foot">AI 权益为 AI 服务额度，不可提现、转赠或折现<br>如有疑问请联系客服</div>
</div>'''
    return page(DETAIL_CSS, body)


def purchase_notes():
    items = [
        "本商品为示例学堂 App 会员服务，<b>无需物流</b>，支付成功后自动到账对应的 App 账号。",
        "到账后即可使用，<b>不支持七天无理由退货</b>。",
        "一笔订单只能到账一个账号；手机号填错的，请联系客服退款后重新下单。",
        "注销示例学堂账号后，剩余会员时长与权益全部作废，不可恢复。",
    ]
    return f'<div class="sec"><h2>购买须知</h2><ul class="notes">{"".join(f"<li>{i}</li>" for i in items)}</ul></div>'


def detail_pack(p):
    hl = ' class="hl"'
    others = "".join(
        f'<tr{hl if x["id"] == p["id"] else ""}><td>{x["name"]}</td><td>{meter(x["layers"], "tmeter")}</td><td>{x["dl"]} 次</td><td>1 年</td></tr>'
        for x in PACKS)
    notes = [
        "<b>仅限当前会员购买：</b>体验会员、月卡及以上会员都可以买；未开通会员或会员已到期的账号下单，系统会自动为你退款。",
        "<b>有效期 1 年：</b>到账后 1 年内有效，可叠加购买，每个包单独计算有效期。",
        "<b>扣减顺序：</b>先用每月发放的会员额度，用完再用加量包；多个加量包按购买先后使用。",
        "<b>资料下载次数：</b>先用会员卡的次数，用完再用加量包的次数；加量包到期时未用完的次数清零。",
        "<b>会员到期后：</b>加量包里没用完的AI 权益与次数照常可用，直到加量包到期。",
    ]
    body = f'''<div class="page">
<div class="hero">{brand_html()}
  <div class="art orange"><div class="t">{SPARK}额度加量包</div><b>{p["name"]}</b></div>
  <h1>额度加量包<br><span style="color:var(--o2)">{p["name"]}</span></h1>
  <div class="sub">会员额度不够用时的补充<br>同时含AI 权益与资料下载次数</div><span class="badge tag">会员专享</span>
</div>
<div class="sec"><h2>加量包内容</h2><div class="stats">
  <div class="stat">{meter(p["layers"])}<div class="k">AI 权益补充</div><div class="n">AI 功能通用</div></div>
  <div class="stat"><div class="v">{p["dl"]}<small>次</small></div><div class="k">资料下载</div><div class="n">月卡会员同样可用</div></div>
  <div class="stat"><div class="v">1<small>年</small></div><div class="k">有效期</div><div class="n">自到账起计算</div></div>
</div></div>
<div class="sec"><h2>可用于</h2><div class="lead">AI 权益是统一额度，以下功能之间可以自由使用。</div>{feature_grid(True)}</div>
<div class="sec"><h2>三档加量包</h2><table><tr><th>加量包</th><th>AI 权益</th><th>资料下载</th><th>有效期</th></tr>{others}</table></div>
{steps_section()}
<div class="sec"><h2>使用说明</h2><ul class="notes">{"".join(f"<li>{n}</li>" for n in notes)}</ul></div>
{purchase_notes()}
<div class="foot">AI 权益为 AI 服务额度，不可提现、转赠或折现<br>如有疑问请联系客服</div>
</div>'''
    return page(DETAIL_CSS, body)


# ---------- 渲染 ----------
def shoot(html_path, png_path, width, height, scale):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={width},{height}", f"--force-device-scale-factor={scale}",
                    f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True)


def trim_bottom(png_path):
    """详情页高度不固定：截一张足够高的图，再裁掉底部的哨兵色 #010203。"""
    im = Image.open(png_path).convert("RGB")
    w, h = im.size
    px = im.load()
    y = h - 1
    while y > 0 and all(px[x, y] == (1, 2, 3) for x in range(0, w, 7)):
        y -= 1
    im.crop((0, 0, w, y + 1)).save(png_path, optimize=True)
    return im.size[0], y + 1


def build(only=None):
    for d in (HTML_DIR, MAIN_DIR, DETAIL_DIR):
        d.mkdir(exist_ok=True)
    jobs = [(m, main_member, detail_member) for m in MEMBERS] + [(p, main_pack, detail_pack) for p in PACKS]
    for item, main_fn, detail_fn in jobs:
        if only and item["id"] != only:
            continue
        label = item["name"] if item in MEMBERS else f'加量包-{item["name"]}'
        main_html = HTML_DIR / f'{item["id"]}-main.html'
        main_html.write_text(main_fn(item), encoding="utf-8")
        main_png = MAIN_DIR / f"{label}-主图.png"
        shoot(main_html, main_png, 800, 800, 1.5)

        detail_html = HTML_DIR / f'{item["id"]}-detail.html'
        detail_html.write_text(detail_fn(item), encoding="utf-8")
        detail_png = DETAIL_DIR / f"{label}-详情页.png"
        shoot(detail_html, detail_png, 750, 6000, 2)
        size = trim_bottom(detail_png)
        print(f"✓ {label}  主图 1200×1200  详情页 {size[0]}×{size[1]}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
