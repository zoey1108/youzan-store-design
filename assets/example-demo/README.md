# 参考实现（虚构示例）

一套完整可跑的生成器，品牌「示例学堂 · AI 学习助手」和全部商品、次数、文案都是虚构的，只演示结构。新项目复制后改「数据 + 配色 + 文案」即可。

- `build.py`：会员卡（体验/月/季/半年/年）+ 额度加量包（迷你/标准/大）的主图（800×800@1.5）和商详长图（750@2）。不公开的额度数字用三段式进度条表示。
- `homepage.py`：首页横幅、会员权益条、购买须知（750 宽）。
- `usercenter.py`：个人中心头部背景（960×440）、到账说明广告位（710×200）、常见问题（750 宽）。

`homepage.py` 和 `usercenter.py` 会 `from build import ...`，三个文件要放在同一目录。需要 macOS + Google Chrome + Pillow（`pip install pillow`）。

```bash
python3 build.py        # 生成 主图/ 详情页/ html/
python3 homepage.py     # 生成 主页/
python3 usercenter.py   # 生成 个人中心/
```
