"""有赞个人中心图片（参考实现）（头部背景 / 到账说明广告位 / 常见问题）

复用 build.py 的配色与渲染。不出现任何AI 权益点数。
用法：python3 usercenter.py
"""
from build import BASE_CSS, CROWN, HTML_DIR, ROOT, icon, page, shoot, trim_bottom

OUT = ROOT / "个人中心"

UC_CSS = BASE_CSS + """
/* 头部背景 960x440：中间色调，深色昵称和白色图标都看得清 */
.head{position:relative;width:960px;height:440px;overflow:hidden;
  background:linear-gradient(135deg,#FFC08F 0%,#FF9F5E 55%,#FF8A45 100%)}
.head .glow{position:absolute;left:-160px;top:-200px;width:620px;height:620px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.45),rgba(255,255,255,0) 70%)}
.head .ring{position:absolute;border-radius:50%;border:2px solid rgba(255,255,255,.22)}
.head .r1{right:-120px;top:-160px;width:520px;height:520px}
.head .r2{right:-40px;top:-80px;width:360px;height:360px}
.head .mc{position:absolute;right:70px;bottom:-40px;width:300px;height:190px;border-radius:28px;transform:rotate(-10deg);
  background:linear-gradient(135deg,#7A5030,#3A2312);opacity:.9;box-shadow:0 20px 40px rgba(92,58,30,.25);
  padding:26px 30px;color:var(--gold2)}
.head .mc .t{display:flex;align-items:center;gap:8px;font-size:20px;font-weight:600}
.head .mc .t svg{width:26px;height:26px}

/* 广告位 710x200：到账说明 */
.ad{position:relative;width:710px;height:200px;border-radius:0;overflow:hidden;padding:28px 34px;
  background:linear-gradient(120deg,#FFF3EA 0%,#FFE4D0 100%);display:flex;align-items:center;gap:26px}
.ad .ic{flex:none;width:96px;height:96px;border-radius:28px;background:linear-gradient(135deg,var(--o1),var(--o2));
  display:grid;place-items:center;color:#fff;box-shadow:0 10px 22px rgba(255,107,36,.28)}
.ad h3{font-size:32px;font-weight:800;line-height:1.25}
.ad h3 em{font-style:normal;color:var(--o2)}
.ad p{margin-top:10px;font-size:22px;color:var(--b2);line-height:1.5}
.ad .arrow{position:absolute;right:30px;top:50%;transform:translateY(-50%);font-size:40px;color:var(--o-line)}

/* 常见问题 750 宽 */
.faq{width:750px;background:var(--page);padding:12px 24px 36px}
.box{background:#fff;border-radius:28px;padding:32px 30px 14px}
.box h2{display:flex;align-items:center;gap:12px;font-size:30px;font-weight:700}
.box h2::before{content:"";width:8px;height:28px;border-radius:4px;background:linear-gradient(180deg,var(--o1),var(--o2))}
.qa{padding:24px 0;border-bottom:1px solid #F1E6DE}
.qa:last-child{border-bottom:none}
.q{display:flex;gap:12px;font-size:25px;font-weight:700;line-height:1.45}
.q b{flex:none;width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,var(--o1),var(--o2));color:#fff;
  font-size:20px;display:grid;place-items:center;margin-top:1px}
.a{margin:10px 0 0 48px;font-size:22px;color:var(--b2);line-height:1.65}
.a strong{color:var(--b1)}
.tip{margin-top:20px;text-align:center;font-size:20px;color:var(--b3)}
"""

FAQ = [
    ("付了钱，会员没到账？",
     "请核对订单留言里的<strong>「App 账号手机号」</strong>。号码还没注册的，用这个号码注册示例学堂 App 后会自动到账；号码填错的，请联系客服退款后重新下单。"),
    ("在哪里查看会员和 AI 权益？",
     "打开示例学堂 App，用下单时填写的手机号登录，进入<strong>「会员中心」</strong>即可查看会员有效期、本月 AI 权益状态和资料下载次数，快用完时 App 会提醒。"),
    ("续费后为什么还显示原来的会员卡？",
     "同一时间只有一张会员卡生效。会员有效期内再次购买，新会员卡会在当前会员到期后自动生效，不叠加、不顺延。"),
    ("会员可以退款吗？",
     "会员服务到账后即可使用，<strong>不支持七天无理由退货</strong>。手机号填错、重复购买等情况，请联系客服处理。"),
]


def head():
    body = f'''<div class="head"><div class="glow"></div><div class="ring r1"></div><div class="ring r2"></div>
<div class="mc"><div class="t">{CROWN}示例学堂会员</div></div></div>'''
    return page(UC_CSS, body)


def ad():
    body = f'''<div class="ad"><div class="ic">{icon("phone", 48)}</div>
<div><h3>会员在<em>示例学堂 App</em> 里使用</h3>
<p>用下单时填写的手机号登录 App<br>进入「会员中心」查看会员与权益</p></div></div>'''
    return page(UC_CSS, body)


def faq():
    items = "".join(f'<div class="qa"><div class="q"><b>Q</b>{q}</div><div class="a">{a}</div></div>' for q, a in FAQ)
    body = f'''<div class="faq"><div class="box"><h2>常见问题</h2>{items}</div>
<div class="tip">还有其他问题？点上方「客服聊天」联系我们</div></div>'''
    return page(UC_CSS, body)


def main():
    OUT.mkdir(exist_ok=True)
    HTML_DIR.mkdir(exist_ok=True)
    for name, fn, w, h in [("1-头部背景", head, 960, 440), ("2-到账说明", ad, 710, 200), ("3-常见问题", faq, 750, 1600)]:
        html = HTML_DIR / f"uc-{name}.html"
        html.write_text(fn(), encoding="utf-8")
        png = OUT / f"个人中心-{name}.png"
        shoot(html, png, w, h + 200, 2)
        print("✓", png.name, trim_bottom(png))


if __name__ == "__main__":
    main()
