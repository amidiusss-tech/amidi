#!/usr/bin/env python3
"""Generate a bold Telegram chat cover: gym / twice-a-week / alpha aesthetic."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
OUT = Path(__file__).resolve().parent / "telegram_gym_chat_cover.png"


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def draw_radial_glow(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, color: tuple[int, int, int, int]) -> None:
    for i in range(r, 0, -3):
        a = int(color[3] * (1 - i / r) ** 2)
        if a < 3:
            continue
        bbox = (cx - i, cy - i, cx + i, cy + i)
        draw.ellipse(bbox, outline=None, fill=(color[0], color[1], color[2], a))


def main() -> None:
    # Base: near-black with warm undertone
    img = Image.new("RGB", (W, H), (8, 6, 6))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        # subtle vertical warm vignette
        r = int(12 + 35 * t)
        g = int(4 + 12 * t)
        b = int(4 + 8 * t)
        for x in range(W):
            px[x, y] = (r, g, b)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # Diagonal "energy" stripes
    for i in range(-H, W + H, 28):
        od.polygon(
            [
                (i, 0),
                (i + 60, 0),
                (i + 20, H),
                (i - 40, H),
            ],
            fill=(180, 30, 20, 18),
        )

    # Central glow (testosterone red / ember)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    draw_radial_glow(gd, W // 2, H // 2 - 20, 420, (220, 50, 30, 120))
    draw_radial_glow(gd, W // 2 + 120, H // 2 + 80, 280, (255, 140, 40, 80))
    overlay = Image.alpha_composite(overlay, glow)

    # Simple barbell silhouette (alpha / gym symbol)
    bx, by, bw, bh = W // 2, H // 2 + 40, 520, 14
    od2 = ImageDraw.Draw(overlay)
    od2.rounded_rectangle(
        (bx - bw // 2 - 8, by - bh // 2 - 8, bx + bw // 2 + 8, by + bh // 2 + 8),
        radius=8,
        fill=(20, 18, 18, 200),
    )
    od2.rounded_rectangle(
        (bx - bw // 2, by - bh // 2, bx + bw // 2, by + bh // 2),
        radius=4,
        fill=(60, 58, 58, 255),
    )
    plate_w, plate_h = 22, 110
    for side in (-1, 1):
        od2.rounded_rectangle(
            (
                bx + side * (bw // 2 + plate_w // 2 + 4) - plate_w // 2,
                by - plate_h // 2,
                bx + side * (bw // 2 + plate_w // 2 + 4) + plate_w // 2,
                by + plate_h // 2,
            ),
            radius=4,
            fill=(200, 45, 35, 230),
        )
        od2.rounded_rectangle(
            (
                bx + side * (bw // 2 + plate_w + 26) - plate_w // 2 - 6,
                by - plate_h // 2 - 10,
                bx + side * (bw // 2 + plate_w + 26) + plate_w // 2 + 6,
                by + plate_h // 2 + 10,
            ),
            radius=4,
            fill=(140, 35, 30, 200),
        )

    # Stylized lifter silhouettes (wide shoulders, alpha vibe)
    def draw_lifter(side: int) -> None:
        sx = W // 2 + side * 340
        base_y = H // 2 + 260  # keep heads below headline block
        body = [
            (sx, base_y - 200),
            (sx + side * 78, base_y - 165),
            (sx + side * 92, base_y - 40),
            (sx + side * 58, base_y + 10),
            (sx + side * 52, base_y + 180),
            (sx - side * 52, base_y + 180),
            (sx - side * 58, base_y + 10),
            (sx - side * 92, base_y - 40),
            (sx - side * 78, base_y - 165),
        ]
        od2.polygon(body, fill=(25, 22, 22, 235))
        od2.ellipse((sx - 38, base_y - 248, sx + 38, base_y - 172), fill=(35, 32, 32, 240))

    draw_lifter(-1)
    draw_lifter(1)

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    d = ImageDraw.Draw(img)
    font_title = load_font(72)
    font_hero = load_font(118)
    font_sub = load_font(36)

    title = "МУЖСКОЙ ЗАЛ"
    hero = "2 РАЗА В НЕДЕЛЮ"
    sub = "СИЛА • ДИСЦИПЛИНА • БРАТСТВО"

    def text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
        bbox = d.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    tw, th = text_size(title, font_title)
    hw, hh = text_size(hero, font_hero)
    sw, sh = text_size(sub, font_sub)

    cx = W // 2
    y0 = 88

    def draw_shadowed(center_x: int, y: int, text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int]) -> None:
        tw_, th_ = text_size(text, font)
        x = center_x - tw_ // 2
        for ox, oy in ((4, 4), (2, 2), (0, 0)):
            color = (0, 0, 0) if (ox, oy) != (0, 0) else fill
            d.text((x + ox, y + oy), text, font=font, fill=color)

    # Gold / steel headline
    draw_shadowed(cx, y0, title, font_title, (235, 200, 120))
    draw_shadowed(cx, y0 + th + 18, hero, font_hero, (255, 245, 235))
    draw_shadowed(cx, y0 + th + 18 + hh + 22, sub, font_sub, (180, 175, 170))

    # Top chrome line
    d.rectangle((80, 36, W - 80, 40), fill=(200, 60, 45))
    d.rectangle((80, H - 40, W - 80, H - 36), fill=(200, 60, 45))

    # Slight film grain
    import random

    rnd = random.Random(42)
    noise = Image.new("L", (W, H))
    nd = ImageDraw.Draw(noise)
    for _ in range(9000):
        x, y = rnd.randint(0, W - 1), rnd.randint(0, H - 1)
        nd.point((x, y), fill=rnd.randint(180, 255))
    noise = noise.filter(ImageFilter.GaussianBlur(radius=1.2))
    img = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.035)

    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
