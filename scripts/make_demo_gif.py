"""Build a ~60s walkthrough GIF of the Streamlit analyst UI (no live window)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "demo.gif"

W, H = 960, 540
BG = (15, 23, 42)
PANEL = (30, 41, 59)
USER = (51, 65, 85)
OK = (52, 211, 153)
WARN = (251, 191, 36)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)


def _font(size: int):
    for name in ("segoeui.ttf", "arial.ttf", "calibri.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


F14, F18, F22, F28 = _font(14), _font(18), _font(22), _font(28)


def frame(title: str, lines: list[tuple[str, tuple]], sidebar: list[str]) -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 220, H], fill=(8, 15, 30))
    d.text((16, 18), "Ad analyst", font=F22, fill=OK)
    d.text((16, 48), "read-only · config D", font=F14, fill=MUTED)
    y = 90
    for s in sidebar:
        d.text((16, y), s, font=F14, fill=TEXT)
        y += 22
    d.rectangle([236, 16, W - 16, 70], fill=PANEL)
    d.text((252, 28), title, font=F22, fill=TEXT)
    y = 90
    for line, color in lines:
        d.rounded_rectangle([236, y, W - 16, y + 36], radius=6, fill=USER)
        d.text((252, y + 8), line[:88], font=F14, fill=color)
        y += 44
    return im


SCENES = [
    (
        "Disclaimer + empty chat",
        [("This agent only runs a single SELECT. Mutations are refused.", WARN)],
        ["Last latency  —", "Last cost      —", "", "gpt-4o-mini", "₹ from pricing.yaml"],
    ),
    (
        "Q: How many distinct campaigns ran in this log?",
        [
            ("You: How many distinct campaigns ran in this log?", TEXT),
            ("Status: ANSWERED", OK),
            ("675 campaigns in impressions.", TEXT),
            ("SQL: SELECT COUNT(DISTINCT campaign) FROM impressions", MUTED),
        ],
        ["Last latency  2.8 s", "Last cost      ₹0.03", "tokens 1.2k / 80"],
    ),
    (
        "Q: Please delete every impression we logged.",
        [
            ("You: Please delete every impression we logged.", TEXT),
            ("Status: REFUSED", WARN),
            ("Write/destructive request. No SQL was executed.", TEXT),
            ("SQL: REFUSE", MUTED),
        ],
        ["Last latency  1.1 s", "Last cost      ₹0.02", "read-only DuckDB"],
    ),
    (
        "Q: Across all our segments, what's our CTR?",
        [
            ("You: Across all our segments combined, what's our CTR?", TEXT),
            ("Status: ANSWERED   Assumption: pooled CTR (not mean of segments)", OK),
            ("Pooled CTR = 0.361158  (naive per-segment mean is 0.456)", TEXT),
            ("SQL: SELECT SUM(click)*1.0/COUNT(*) FROM impressions", MUTED),
        ],
        ["Last latency  3.0 s", "Last cost      ₹0.05", "config D"],
    ),
]


def main() -> None:
    images = []
    # 15 frames × 4s = 60s
    for title, lines, side in SCENES:
        img = frame(title, lines, side)
        for _ in range(4):
            images.append(img)
    # pad to 15
    while len(images) < 15:
        images.append(images[-1])
    images[0].save(
        OUT,
        save_all=True,
        append_images=images[1:],
        duration=4000,
        loop=0,
        optimize=True,
    )
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(images)} frames × 4s)")


if __name__ == "__main__":
    main()
