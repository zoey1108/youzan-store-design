"""有赞店铺主页图片（参考实现）（横幅 / 会员权益 / 购买须知）

复用 build.py 的配色、图标与渲染函数。宽 750 设计，2 倍渲染。
用法：python3 homepage.py
"""
from build import (AI_FEATURES, BASE_CSS, CROWN, FEAT_DESC, HTML_DIR, ICONS, ROOT,
                   brand_html, icon, page, shoot, trim_bottom)

OUT = ROOT / "主页"

HOME_CSS = BASE_CSS + """
.wrap{width:750px}
/* 顶部横幅 */
.banner{position:relative;overflow:hidden;padding:44px 40px 48px;
  background:linear-gradient(160deg,#FFDCC2 0%,#FFEBDD 45%,#FFF6EF 100%)}
.banner .brand{font-size:24px}
.banner .logo{width:44px;height:44px;font-size:24px}
.banner h1{margin-top:38px;max-width:410px;font-size:60px;font-weight:800;line-height:1.18;letter-spacing:1px}
.banner h1 em{font-style:normal;color:var(--o2)}
.banner .sub{margin-top:14px;max-width:410px;font-size:24px;color:var(--b2);line-height:1.6}
.banner .cta{margin-top:30px;display:inline-flex;align-items:center;gap:10px;
  font-size:26px;padding:14px 34px}
.banner .glow{position:absolute;right:-120px;top:-120px;width:520px;height:520px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.8),rgba(255,255,255,0) 70%)}
.cards{position:absolute;right:26px;top:118px;width:270px;height:250px}
.mc{position:absolute;width:220px;height:140px;border-radius:24px;padding:20px 22px;
  display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 16px 32px rgba(92,58,30,.25)}
.mc .t{display:flex;align-items:center;gap:6px;font-size:16px;font-weight:600}
.mc .t svg{width:22px;height:22px}
.mc b{font-size:44px;font-weight:800;line-height:1}
.mc.brown{background:linear-gradient(135deg,#7A5030,#3A2312);color:var(--gold2)}
.mc.orange{background:linear-gradient(135deg,#FFB257,#FF6B24);color:#fff;box-shadow:0 16px 32px rgba(255,107,36,.3)}
.mc.c1{right:0;top:0;transform:rotate(8deg)}
.mc.c2{right:40px;top:104px;transform:rotate(-6deg)}

/* 会员权益条 */
.perks{background:#fff;padding:34px 24px 30px}
.perks h2{text-align:center;font-size:30px;font-weight:700}
.perks h2 small{display:block;margin-top:6px;font-size:20px;font-weight:400;color:var(--b3)}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-top:26px}
.feat{text-align:center}
.feat .ic{width:80px;height:80px;margin:0 auto;border-radius:24px;background:var(--o-bg);display:grid;place-items:center;color:var(--o2)}
.feat .nm{margin-top:12px;font-size:22px;font-weight:600}
.feat .ds{margin-top:4px;font-size:17px;color:var(--b3);line-height:1.4}
.note{margin:24px 16px 0;padding:14px 18px;border-radius:16px;background:#FFF8F4;font-size:19px;color:var(--b2);text-align:center}

/* 购买须知 */
.howto{background:var(--page);padding:30px 24px 36px}
.box{background:#fff;border-radius:28px;padding:32px 30px}
.box h2{display:flex;align-items:center;gap:12px;font-size:30px;font-weight:700}
.box h2::before{content:"";width:8px;height:28px;border-radius:4px;background:linear-gradient(180deg,var(--o1),var(--o2))}
.steps{display:flex;gap:12px;margin-top:26px}
.step{flex:1;text-align:center}
.step .ic{width:70px;height:70px;margin:0 auto;border-radius:50%;background:linear-gradient(135deg,var(--o1),var(--o2));color:#fff;display:grid;place-items:center}
.step .no{margin-top:10px;font-size:16px;color:var(--o2);font-weight:700;letter-spacing:2px}
.step .nm{margin-top:4px;font-size:21px;font-weight:600;line-height:1.4}
.hl{margin-top:24px;border:2px dashed var(--o-line);border-radius:18px;padding:18px 22px;background:#FFF8F4;font-size:21px;line-height:1.6}
.hl b{color:var(--o2)}
.mini{margin-top:18px;font-size:18px;color:var(--b3);line-height:1.7}
"""


def banner():
    body = f'''<div class="wrap"><div class="banner"><div class="glow"></div>{brand_html()}
<h1>示例学堂会员<br><em>AI 学习辅导</em></h1>
<div class="sub">智能问答 · 作文批改<br>语音讲解 · 练习生成</div>
<span class="badge cta">选择会员套餐 ↓</span>
<div class="cards">
  <div class="mc brown c1"><div class="t">{CROWN}示例学堂会员</div><b class="gold-text">年卡</b></div>
  <div class="mc orange c2"><div class="t">{CROWN}新人专享</div><b>体验</b></div>
</div></div></div>'''
    return page(HOME_CSS, body)


def perks():
    cells = "".join(f'<div class="feat"><div class="ic">{icon(f, 38)}</div><div class="nm">{f}</div>'
                    f'<div class="ds">{FEAT_DESC[f]}</div></div>' for f in AI_FEATURES + ["资料下载"])
    body = f'''<div class="wrap"><div class="perks">
<h2>会员权益<small>AI 权益是统一额度，以下功能之间可以自由使用</small></h2>
<div class="grid">{cells}</div>
<div class="note">资料下载为季卡及以上专享 · 学习计划、错题收藏等一直免费</div>
</div></div>'''
    return page(HOME_CSS, body)


def howto():
    steps = [("edit", "下单时填写<br>App 账号手机号"), ("phone", "支付成功<br>自动到账"), ("user", "打开示例学堂 App<br>会员中心查看")]
    cells = "".join(f'<div class="step"><div class="ic">{icon(i, 32)}</div><div class="no">STEP {n}</div>'
                    f'<div class="nm">{t}</div></div>' for n, (i, t) in enumerate(steps, 1))
    body = f'''<div class="wrap"><div class="howto"><div class="box"><h2>购买须知</h2>
<div class="steps">{cells}</div>
<div class="hl">下单时请在留言<b>「App 账号手机号」</b>里填写使用 App 的手机号（家长或孩子的账号）。号码未注册的，注册后自动到账；号码填错的，请联系客服退款后重新下单。</div>
<div class="mini">· 会员有效期内再次购买，新会员卡在当前会员到期后自动生效<br>· 本商品无需物流，到账后即可使用，不支持七天无理由退货<br>· 体验会员仅限新用户购买 1 次</div>
</div></div></div>'''
    return page(HOME_CSS, body)


def main():
    OUT.mkdir(exist_ok=True)
    HTML_DIR.mkdir(exist_ok=True)
    for name, fn in [("1-横幅", banner), ("2-会员权益", perks), ("3-购买须知", howto)]:
        html = HTML_DIR / f"home-{name}.html"
        html.write_text(fn(), encoding="utf-8")
        png = OUT / f"主页-{name}.png"
        shoot(html, png, 750, 1400, 2)
        print("✓", png.name, trim_bottom(png))


if __name__ == "__main__":
    main()
