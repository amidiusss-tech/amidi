from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


SIZE = 1024
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "telegram-gym-chat-2x-week.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def vertical_gradient(width, height, top, bottom):
    image = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        mix = y / max(height - 1, 1)
        color = tuple(int(top[i] * (1 - mix) + bottom[i] * mix) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def radial_glow(size, center, radius, color):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    for step in range(radius, 0, -8):
        alpha = max(0, int(155 * (step / radius) ** 2))
        draw.ellipse((x - step, y - step, x + step, y + step), fill=color + (alpha,))
    return layer.filter(ImageFilter.GaussianBlur(30))


def add_streaks(image):
    draw = ImageDraw.Draw(image)
    streak_colors = [(255, 90, 0, 30), (255, 140, 40, 26), (255, 210, 120, 18)]
    for index, color in enumerate(streak_colors):
        offset = index * 110
        draw.polygon(
            [
                (0, 260 + offset),
                (0, 330 + offset),
                (SIZE, 60 + offset),
                (SIZE, 0 + offset),
            ],
            fill=color,
        )
        draw.polygon(
            [
                (0, 780 - offset),
                (0, 840 - offset),
                (SIZE, 520 - offset),
                (SIZE, 450 - offset),
            ],
            fill=color,
        )


def add_texture(image):
    texture = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)
    step = 24
    for x in range(-SIZE, SIZE * 2, step):
        draw.line((x, 0, x - 320, SIZE), fill=(255, 255, 255, 10), width=2)
    texture = texture.filter(ImageFilter.GaussianBlur(0.5))
    image.alpha_composite(texture)


def add_frame(image):
    draw = ImageDraw.Draw(image)
    outer = (44, 44, SIZE - 44, SIZE - 44)
    inner = (72, 72, SIZE - 72, SIZE - 72)
    draw.rounded_rectangle(outer, radius=52, outline=(255, 130, 30, 175), width=8)
    draw.rounded_rectangle(inner, radius=42, outline=(255, 210, 110, 85), width=2)

    corners = [
        [(96, 96), (220, 96), (160, 132)],
        [(SIZE - 96, 96), (SIZE - 220, 96), (SIZE - 160, 132)],
        [(96, SIZE - 96), (220, SIZE - 96), (160, SIZE - 132)],
        [(SIZE - 96, SIZE - 96), (SIZE - 220, SIZE - 96), (SIZE - 160, SIZE - 132)],
    ]
    for points in corners:
        draw.polygon(points, fill=(255, 150, 35, 220))


def add_floor(image):
    floor = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(floor)
    draw.polygon(
        [(0, 760), (SIZE, 690), (SIZE, SIZE), (0, SIZE)],
        fill=(12, 12, 16, 190),
    )
    draw.line((0, 788, SIZE, 728), fill=(255, 160, 50, 90), width=4)
    image.alpha_composite(floor)


def add_barbell(draw, y, accent):
    draw.line((188, y, SIZE - 188, y), fill=accent, width=12)
    for x in (238, 286, SIZE - 286, SIZE - 238):
        draw.rounded_rectangle((x - 14, y - 52, x + 14, y + 52), radius=8, fill=accent)
    for x in (206, SIZE - 206):
        draw.rounded_rectangle((x - 22, y - 72, x + 22, y + 72), radius=10, fill=(255, 210, 100, 255))


def draw_lifter(draw, cx, cy, scale, body, accent):
    head_r = int(34 * scale)
    draw.ellipse((cx - head_r, cy - 288 * scale - head_r, cx + head_r, cy - 288 * scale + head_r), fill=body)
    draw.polygon(
        [
            (cx - 66 * scale, cy - 210 * scale),
            (cx + 66 * scale, cy - 210 * scale),
            (cx + 102 * scale, cy - 48 * scale),
            (cx - 102 * scale, cy - 48 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx - 80 * scale, cy - 196 * scale),
            (cx - 164 * scale, cy - 320 * scale),
            (cx - 128 * scale, cy - 338 * scale),
            (cx - 32 * scale, cy - 214 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx + 80 * scale, cy - 196 * scale),
            (cx + 164 * scale, cy - 320 * scale),
            (cx + 128 * scale, cy - 338 * scale),
            (cx + 32 * scale, cy - 214 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx - 52 * scale, cy - 44 * scale),
            (cx - 4 * scale, cy - 44 * scale),
            (cx - 28 * scale, cy + 188 * scale),
            (cx - 86 * scale, cy + 188 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx + 52 * scale, cy - 44 * scale),
            (cx + 4 * scale, cy - 44 * scale),
            (cx + 28 * scale, cy + 188 * scale),
            (cx + 86 * scale, cy + 188 * scale),
        ],
        fill=body,
    )
    draw.rounded_rectangle(
        (cx - 114 * scale, cy + 176 * scale, cx - 28 * scale, cy + 202 * scale),
        radius=6,
        fill=accent,
    )
    draw.rounded_rectangle(
        (cx + 28 * scale, cy + 176 * scale, cx + 114 * scale, cy + 202 * scale),
        radius=6,
        fill=accent,
    )


def draw_boxer(draw, cx, cy, scale, body, accent):
    head_r = int(28 * scale)
    draw.ellipse((cx - head_r, cy - 230 * scale - head_r, cx + head_r, cy - 230 * scale + head_r), fill=body)
    draw.polygon(
        [
            (cx - 50 * scale, cy - 180 * scale),
            (cx + 42 * scale, cy - 170 * scale),
            (cx + 58 * scale, cy - 20 * scale),
            (cx - 66 * scale, cy - 18 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx + 24 * scale, cy - 162 * scale),
            (cx + 118 * scale, cy - 126 * scale),
            (cx + 140 * scale, cy - 82 * scale),
            (cx + 54 * scale, cy - 96 * scale),
        ],
        fill=body,
    )
    draw.ellipse(
        (cx + 126 * scale, cy - 112 * scale, cx + 176 * scale, cy - 60 * scale),
        fill=accent,
    )
    draw.polygon(
        [
            (cx - 30 * scale, cy - 140 * scale),
            (cx - 126 * scale, cy - 182 * scale),
            (cx - 144 * scale, cy - 148 * scale),
            (cx - 60 * scale, cy - 96 * scale),
        ],
        fill=body,
    )
    draw.ellipse(
        (cx - 166 * scale, cy - 184 * scale, cx - 118 * scale, cy - 132 * scale),
        fill=accent,
    )
    draw.polygon(
        [
            (cx - 20 * scale, cy - 8 * scale),
            (cx + 32 * scale, cy - 8 * scale),
            (cx + 56 * scale, cy + 152 * scale),
            (cx + 8 * scale, cy + 160 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx - 48 * scale, cy - 6 * scale),
            (cx - 6 * scale, cy - 6 * scale),
            (cx - 90 * scale, cy + 144 * scale),
            (cx - 132 * scale, cy + 142 * scale),
        ],
        fill=body,
    )


def draw_runner(draw, cx, cy, scale, body, accent):
    head_r = int(28 * scale)
    draw.ellipse((cx - head_r, cy - 234 * scale - head_r, cx + head_r, cy - 234 * scale + head_r), fill=body)
    draw.polygon(
        [
            (cx - 40 * scale, cy - 190 * scale),
            (cx + 54 * scale, cy - 176 * scale),
            (cx + 80 * scale, cy - 50 * scale),
            (cx - 32 * scale, cy - 44 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx + 40 * scale, cy - 156 * scale),
            (cx + 138 * scale, cy - 208 * scale),
            (cx + 152 * scale, cy - 176 * scale),
            (cx + 74 * scale, cy - 112 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx - 20 * scale, cy - 150 * scale),
            (cx - 126 * scale, cy - 74 * scale),
            (cx - 108 * scale, cy - 44 * scale),
            (cx - 2 * scale, cy - 100 * scale),
        ],
        fill=body,
    )
    draw.ellipse(
        (cx - 150 * scale, cy - 92 * scale, cx - 96 * scale, cy - 40 * scale),
        outline=accent,
        width=int(8 * scale),
    )
    draw.polygon(
        [
            (cx + 22 * scale, cy - 42 * scale),
            (cx + 74 * scale, cy - 48 * scale),
            (cx + 144 * scale, cy + 122 * scale),
            (cx + 94 * scale, cy + 136 * scale),
        ],
        fill=body,
    )
    draw.polygon(
        [
            (cx - 26 * scale, cy - 32 * scale),
            (cx + 8 * scale, cy - 36 * scale),
            (cx - 68 * scale, cy + 136 * scale),
            (cx - 104 * scale, cy + 138 * scale),
        ],
        fill=body,
    )
    draw.rounded_rectangle(
        (cx + 132 * scale, cy + 112 * scale, cx + 188 * scale, cy + 130 * scale),
        radius=5,
        fill=accent,
    )


def draw_title(image):
    draw = ImageDraw.Draw(image)
    font_small = ImageFont.truetype(FONT, 42)
    font_big = ImageFont.truetype(FONT, 276)
    font_mid = ImageFont.truetype(FONT, 88)
    font_bottom = ImageFont.truetype(FONT, 36)

    top_text = "КАЧАЛКА  •  СПОРТ"
    title_text = "2X"
    subtitle_text = "В НЕДЕЛЮ"
    footer_text = "ЖЕЛЕЗО   |   РЕЖИМ   |   ХАРАКТЕР"

    draw.text((SIZE / 2, 120), top_text, font=font_small, anchor="mm", fill=(255, 210, 120, 235))

    for dx, dy, alpha in [(0, 0, 230), (0, 0, 120)]:
        shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.text(
            (SIZE / 2 + dx, 382 + dy),
            title_text,
            font=font_big,
            anchor="mm",
            fill=(255, 90, 0, alpha),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        image.alpha_composite(shadow)

    title_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    title_draw = ImageDraw.Draw(title_layer)
    title_draw.text((SIZE / 2, 382), title_text, font=font_big, anchor="mm", fill=(255, 236, 194, 255))
    title_mask = title_layer.split()[-1]
    gradient = vertical_gradient(SIZE, SIZE, (255, 244, 220), (255, 96, 0))
    gradient.putalpha(title_mask)
    image.alpha_composite(gradient)
    stroke = ImageChops.multiply(title_layer, Image.new("RGBA", (SIZE, SIZE), (255, 180, 80, 255)))
    image.alpha_composite(stroke)

    draw.text((SIZE / 2, 520), subtitle_text, font=font_mid, anchor="mm", fill=(255, 235, 185, 255))
    draw.text((SIZE / 2, 930), footer_text, font=font_bottom, anchor="mm", fill=(255, 200, 120, 255))


def build_image():
    canvas = vertical_gradient(SIZE, SIZE, (12, 12, 18), (36, 6, 2))
    canvas.alpha_composite(radial_glow((SIZE, SIZE), (SIZE // 2, 332), 300, (255, 82, 0)))
    canvas.alpha_composite(radial_glow((SIZE, SIZE), (SIZE // 2, 650), 360, (255, 164, 60)))
    add_streaks(canvas)
    add_texture(canvas)
    add_floor(canvas)
    add_frame(canvas)

    figures = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(figures)
    body = (13, 15, 18, 255)
    accent = (255, 180, 72, 255)

    add_barbell(draw, 255, accent)
    draw_boxer(draw, 224, 790, 1.05, body, accent)
    draw_lifter(draw, 512, 770, 1.16, body, accent)
    draw_runner(draw, 806, 796, 1.0, body, accent)

    outline = figures.filter(ImageFilter.GaussianBlur(20))
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.bitmap((0, 0), outline, fill=(255, 105, 0, 96))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(figures)
    draw_title(canvas)

    vignette = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for inset in range(0, 180, 8):
        alpha = int(1.1 * inset)
        vdraw.rounded_rectangle(
            (inset, inset, SIZE - inset, SIZE - inset),
            radius=100,
            outline=(0, 0, 0, alpha),
            width=8,
        )
    canvas.alpha_composite(vignette)
    return canvas.convert("RGB")


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = build_image()
    image.save(OUTPUT, quality=95)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
