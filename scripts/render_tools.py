"""有赞商品视觉的通用渲染工具：HTML → PNG（本机 Chrome 无头模式）、裁掉长图底部空白、切片、拼总览。

用法（在你的生成器里）：
    import sys; sys.path.insert(0, "<skill>/scripts")
    from render_tools import shoot, trim_bottom, slice_long, overview

约定：生成的 HTML 给 <html> 设背景色 #010203（哨兵色），内容区自己设背景。
这样截一张足够高的图后，trim_bottom 能准确裁掉多余部分。
"""
import math
import subprocess
from pathlib import Path

from PIL import Image

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SENTINEL = (1, 2, 3)


def shoot(html_path, png_path, width, height, scale=2):
    """用 Chrome 无头模式截图。width/height 为 CSS 像素，输出尺寸 = 尺寸 × scale。"""
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={width},{height}", f"--force-device-scale-factor={scale}",
                    f"--screenshot={png_path}", Path(html_path).resolve().as_uri()],
                   check=True, capture_output=True)


def trim_bottom(png_path):
    """裁掉图片底部整行都是哨兵色的部分，返回裁后尺寸。"""
    im = Image.open(png_path).convert("RGB")
    w, h = im.size
    px = im.load()
    y = h - 1
    while y > 0 and all(px[x, y] == SENTINEL for x in range(0, w, 7)):
        y -= 1
    im.crop((0, 0, w, y + 1)).save(png_path, optimize=True)
    return w, y + 1


def slice_long(png_path, out_dir, max_h=3400):
    """把长图等分成高度不超过 max_h 的若干段，输出 <原名>-1.png、-2.png……"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(png_path)
    w, h = im.size
    n = math.ceil(h / max_h)
    step = math.ceil(h / n)
    stem = Path(png_path).stem
    paths = []
    for i in range(n):
        p = out_dir / f"{stem}-{i + 1}.png"
        im.crop((0, i * step, w, min(h, (i + 1) * step))).save(p, optimize=True)
        paths.append(p)
    return paths


def overview(png_paths, out_path, tile=360, cols=4, pad=24, bg=(245, 246, 248)):
    """把若干张方图拼成总览图，方便一次发给用户看。"""
    rows = math.ceil(len(png_paths) / cols)
    sheet = Image.new("RGB", (cols * tile + (cols + 1) * pad, rows * tile + (rows + 1) * pad), bg)
    for i, p in enumerate(png_paths):
        r, c = divmod(i, cols)
        sheet.paste(Image.open(p).convert("RGB").resize((tile, tile)), (pad + c * (tile + pad), pad + r * (tile + pad)))
    sheet.save(out_path)
    return out_path


def stitch_vertical(parts, out_path, bg=(255, 255, 255)):
    """竖向拼接 (图片路径, 顶部裁掉像素, 保留到的像素或 None) 列表，用于把编辑器分屏截图拼成长图。"""
    ims = []
    for path, top, bottom in parts:
        im = Image.open(path).convert("RGB")
        ims.append(im.crop((0, top, im.size[0], bottom or im.size[1])))
    w = max(i.size[0] for i in ims)
    out = Image.new("RGB", (w, sum(i.size[1] for i in ims)), bg)
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.size[1]
    out.save(out_path)
    return out_path
