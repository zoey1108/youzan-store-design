"""有赞商品视觉的通用渲染工具：HTML → PNG（无头浏览器）、裁掉长图底部空白、切片、拼总览、拼长图。

支持 macOS / Linux / Windows。浏览器查找顺序：
  1. 环境变量 CHROME_PATH
  2. 常见安装位置和 PATH 里的 Chrome / Chromium / Edge
  3. 以上都没有时，退回 Playwright（pip install playwright && playwright install chromium）

用法（在你的生成器里）：
    import sys; sys.path.insert(0, "<skill>/scripts")
    from render_tools import shoot, trim_bottom, slice_long, overview

约定：生成的 HTML 给 <html> 设背景色 #010203（哨兵色），内容区自己设背景。
这样截一张足够高的图后，trim_bottom 能准确裁掉多余部分。
"""
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

SENTINEL = (1, 2, 3)

_CANDIDATES = {
    "darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ],
    "win32": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
}
_PATH_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge",
               "microsoft-edge"]


def find_chrome():
    """返回可用的 Chrome/Chromium/Edge 路径；找不到返回 None。"""
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    for p in _CANDIDATES.get(sys.platform, []):
        if Path(p).exists():
            return p
    for name in _PATH_NAMES:
        hit = shutil.which(name)
        if hit:
            return hit
    return None


def _shoot_playwright(html_path, png_path, width, height, scale):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError("没找到 Chrome/Chromium/Edge，也没装 Playwright。请安装浏览器，或设置 CHROME_PATH，"
                           "或执行 pip install playwright && playwright install chromium") from e
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
        page.goto(Path(html_path).resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(png_path))
        browser.close()


def shoot(html_path, png_path, width, height, scale=2):
    """无头浏览器截图。width/height 为 CSS 像素，输出尺寸 = 尺寸 × scale。"""
    chrome = find_chrome()
    if not chrome:
        return _shoot_playwright(html_path, png_path, width, height, scale)
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
                    f"--window-size={width},{height}", f"--force-device-scale-factor={scale}",
                    f"--screenshot={Path(png_path).resolve()}", Path(html_path).resolve().as_uri()],
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
