#!/usr/bin/env python3
from __future__ import annotations

from math import cos, radians, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


SIZE = 1024
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "telegram-gym-chat.png"

TOP_BANNER = "\u0032 \u0420\u0410\u0417\u0410 \u0412 \u041d\u0415\u0414\u0415\u041b\u042e"
BOTTOM_BANNER = (
    "\u041a\u0410\u0427\u0410\u041b\u041a\u0410  \u2022  "
    "\u0421\u041f\u041e\u0420\u0422  \u2022  "
    "\u0421\u0418\u041b\u0410"
)
MID_LABEL = "\u0412 \u041d\u0415\u0414\u0415\u041b\u042e"


def blend(start: tuple[int, int, int], end: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(start, end, strict=True))


def font_candidates() -> list[Path]:
    return [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in font_candidates():
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def regular_polygon(
    cx: float, cy: float, radius: float, sides: int, rotation_deg: float = -90
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for step in range(sides):
        angle = radians(rotation_deg + (360 / sides) * step)
        points.append((cx + cos(angle) * radius, cy + sin(angle) * radius))
    return points


def rotated_rect(
    cx: float, cy: float, width: float, height: float, angle_deg: float
) -> list[tuple[float, float]]:
    angle = radians(angle_deg)
    dx = width / 2
    dy = height / 2
    corners = [(-dx, -dy), (dx, -dy), (dx, dy), (-dx, dy)]
    points: list[tuple[float, float]] = []
    for px, py in corners:
        rx = px * cos(angle) - py * sin(angle)
        ry = px * sin(angle) + py * cos(angle)
        points.append((cx + rx, cy + ry))
    return points


def draw_vertical_gradient(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    top = (6, 7, 10)
    middle = (55, 12, 18)
    bottom = (13, 13, 16)
    for y in range(SIZE):
        t = y / (SIZE - 1)
        if t < 0.55:
            color = blend(top, middle, t / 0.55)
        else:
            color = blend(middle, bottom, (t - 0.55) / 0.45)
        draw.line([(0, y), (SIZE, y)], fill=color)


def add_background_glow(base: Image.Image) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse((90, 110, 930, 920), fill=(240, 66, 30, 70))
    draw.ellipse((220, 120, 800, 760), fill=(255, 176, 60, 56))
    draw.ellipse((310, 210, 720, 640), fill=(255, 220, 110, 28))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    base.alpha_composite(glow)


def add_angled_panels(base: Image.Image) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.polygon([(0, 70), (320, 0), (495, 0), (0, 395)], fill=(110, 16, 24, 110))
    draw.polygon([(660, 0), (850, 0), (1024, 170), (1024, 315)], fill=(190, 74, 28, 85))
    draw.polygon([(0, 760), (245, 560), (420, 1024), (0, 1024)], fill=(70, 8, 16, 120))
    draw.polygon([(640, 850), (1024, 520), (1024, 1024), (770, 1024)], fill=(130, 20, 18, 105))
    overlay = overlay.filter(ImageFilter.GaussianBlur(8))
    base.alpha_composite(overlay)


def add_vignette(base: Image.Image) -> None:
    mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((-160, -120, 1180, 1140), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    darkness = Image.new("RGBA", base.size, (0, 0, 0, 185))
    dark_edges = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dark_edges.paste(darkness, mask=Image.eval(mask, lambda p: 255 - p))
    base.alpha_composite(dark_edges)


def draw_shield(base: Image.Image) -> None:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.polygon(regular_polygon(512, 560, 330, 6), fill=(0, 0, 0, 180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(38))
    base.alpha_composite(shadow)

    shield = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shield)
    outer = regular_polygon(512, 550, 320, 6)
    inner = regular_polygon(512, 550, 286, 6)
    core = regular_polygon(512, 550, 250, 6)
    draw.polygon(outer, fill=(25, 26, 33, 245), outline=(235, 170, 70, 230), width=10)
    draw.polygon(inner, fill=(14, 15, 18, 220), outline=(180, 36, 28, 210), width=4)
    draw.polygon(core, fill=(10, 11, 14, 220))
    for offset in range(-3, 4):
        draw.line(
            [(320 + offset * 20, 770), (512, 320), (704 - offset * 20, 770)],
            fill=(255, 145, 48, 36),
            width=10,
        )
    shield = shield.filter(ImageFilter.GaussianBlur(0.6))
    base.alpha_composite(shield)


def draw_badge_rings(base: Image.Image) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse((120, 120, 904, 904), outline=(255, 255, 255, 14), width=2)
    draw.ellipse((160, 160, 864, 864), outline=(255, 210, 120, 24), width=3)
    draw.ellipse((214, 214, 810, 810), outline=(255, 82, 36, 18), width=2)
    base.alpha_composite(layer)


def draw_jointed_limb(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], width: int, color: tuple[int, int, int, int]) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    radius = max(3, width // 2)
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_dumbbell(
    draw: ImageDraw.ImageDraw, x: float, y: float, scale: float, angle_deg: float, fill: tuple[int, int, int, int]
) -> None:
    handle = rotated_rect(x, y, 68 * scale, 16 * scale, angle_deg)
    plate_a = rotated_rect(x - 26 * scale, y, 18 * scale, 54 * scale, angle_deg)
    plate_b = rotated_rect(x + 26 * scale, y, 18 * scale, 54 * scale, angle_deg)
    outer_a = rotated_rect(x - 40 * scale, y, 14 * scale, 70 * scale, angle_deg)
    outer_b = rotated_rect(x + 40 * scale, y, 14 * scale, 70 * scale, angle_deg)
    for shape in (handle, plate_a, plate_b, outer_a, outer_b):
        draw.polygon(shape, fill=fill)


def draw_power_figure(base: Image.Image, cx: float, base_y: float, scale: float, variant: str) -> None:
    glow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    main_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    rim_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))

    glow = ImageDraw.Draw(glow_layer)
    main = ImageDraw.Draw(main_layer)
    rim = ImageDraw.Draw(rim_layer)

    shadow = (255, 84, 38, 105)
    body = (10, 11, 14, 255)
    trim = (248, 185, 82, 235)

    if variant == "center":
        shoulders = ((cx - 116 * scale, base_y - 312 * scale), (cx + 116 * scale, base_y - 312 * scale))
        hips = ((cx - 58 * scale, base_y - 116 * scale), (cx + 58 * scale, base_y - 116 * scale))
        left_elbow = (cx - 196 * scale, base_y - 212 * scale)
        right_elbow = (cx + 196 * scale, base_y - 212 * scale)
        left_wrist = (cx - 214 * scale, base_y - 336 * scale)
        right_wrist = (cx + 214 * scale, base_y - 336 * scale)
        left_knee = (cx - 76 * scale, base_y + 66 * scale)
        right_knee = (cx + 76 * scale, base_y + 66 * scale)
        left_ankle = (cx - 48 * scale, base_y + 278 * scale)
        right_ankle = (cx + 48 * scale, base_y + 278 * scale)
        head_box = (cx - 40 * scale, base_y - 430 * scale, cx + 40 * scale, base_y - 350 * scale)
        dumbbell_angle = 90
    elif variant == "left":
        shoulders = ((cx - 90 * scale, base_y - 270 * scale), (cx + 82 * scale, base_y - 268 * scale))
        hips = ((cx - 52 * scale, base_y - 102 * scale), (cx + 38 * scale, base_y - 104 * scale))
        left_elbow = (cx - 146 * scale, base_y - 190 * scale)
        right_elbow = (cx + 124 * scale, base_y - 152 * scale)
        left_wrist = (cx - 172 * scale, base_y - 82 * scale)
        right_wrist = (cx + 160 * scale, base_y - 24 * scale)
        left_knee = (cx - 70 * scale, base_y + 54 * scale)
        right_knee = (cx + 40 * scale, base_y + 72 * scale)
        left_ankle = (cx - 46 * scale, base_y + 236 * scale)
        right_ankle = (cx + 36 * scale, base_y + 252 * scale)
        head_box = (cx - 34 * scale, base_y - 370 * scale, cx + 34 * scale, base_y - 302 * scale)
        dumbbell_angle = 26
    else:
        shoulders = ((cx - 82 * scale, base_y - 268 * scale), (cx + 90 * scale, base_y - 270 * scale))
        hips = ((cx - 38 * scale, base_y - 104 * scale), (cx + 52 * scale, base_y - 102 * scale))
        left_elbow = (cx - 124 * scale, base_y - 152 * scale)
        right_elbow = (cx + 146 * scale, base_y - 190 * scale)
        left_wrist = (cx - 160 * scale, base_y - 24 * scale)
        right_wrist = (cx + 172 * scale, base_y - 82 * scale)
        left_knee = (cx - 40 * scale, base_y + 72 * scale)
        right_knee = (cx + 70 * scale, base_y + 54 * scale)
        left_ankle = (cx - 36 * scale, base_y + 252 * scale)
        right_ankle = (cx + 46 * scale, base_y + 236 * scale)
        head_box = (cx - 34 * scale, base_y - 370 * scale, cx + 34 * scale, base_y - 302 * scale)
        dumbbell_angle = -26

    torso = [
        (shoulders[0][0] - 26 * scale, shoulders[0][1] - 4 * scale),
        (shoulders[1][0] + 26 * scale, shoulders[1][1] - 4 * scale),
        (cx + 66 * scale, base_y - 182 * scale),
        hips[1],
        (cx + 26 * scale, base_y - 54 * scale),
        (cx - 26 * scale, base_y - 54 * scale),
        hips[0],
        (cx - 66 * scale, base_y - 182 * scale),
    ]

    pelvis = [
        (cx - 52 * scale, base_y - 106 * scale),
        (cx + 52 * scale, base_y - 106 * scale),
        (cx + 42 * scale, base_y - 46 * scale),
        (cx - 42 * scale, base_y - 46 * scale),
    ]

    for polygon in (torso, pelvis):
        glow.polygon(polygon, fill=shadow)
        main.polygon(polygon, fill=body)

    glow.ellipse(head_box, fill=shadow)
    main.ellipse(head_box, fill=body)
    neck = (cx - 18 * scale, base_y - 350 * scale, cx + 18 * scale, base_y - 312 * scale)
    glow.rounded_rectangle(neck, radius=8 * scale, fill=shadow)
    main.rounded_rectangle(neck, radius=8 * scale, fill=body)

    glow_width_arm = int(74 * scale)
    main_width_arm = int(58 * scale)
    glow_width_leg = int(82 * scale)
    main_width_leg = int(62 * scale)

    left_arm = [shoulders[0], left_elbow, left_wrist]
    right_arm = [shoulders[1], right_elbow, right_wrist]
    left_leg = [(cx - 26 * scale, base_y - 56 * scale), left_knee, left_ankle]
    right_leg = [(cx + 26 * scale, base_y - 56 * scale), right_knee, right_ankle]

    for limb in (left_arm, right_arm):
        draw_jointed_limb(glow, limb, glow_width_arm, shadow)
        draw_jointed_limb(main, limb, main_width_arm, body)

    for limb in (left_leg, right_leg):
        draw_jointed_limb(glow, limb, glow_width_leg, shadow)
        draw_jointed_limb(main, limb, main_width_leg, body)

    foot_w = 62 * scale
    foot_h = 22 * scale
    for ankle, tilt in ((left_ankle, -10), (right_ankle, 10)):
        glow.polygon(rotated_rect(ankle[0], ankle[1] + 20 * scale, foot_w, foot_h, tilt), fill=shadow)
        main.polygon(rotated_rect(ankle[0], ankle[1] + 20 * scale, foot_w, foot_h, tilt), fill=body)

    for wrist, angle in ((left_wrist, dumbbell_angle), (right_wrist, dumbbell_angle)):
        draw_dumbbell(glow, wrist[0], wrist[1], scale * 1.12, angle, shadow)
        draw_dumbbell(main, wrist[0], wrist[1], scale, angle, body)

    rim.line(
        [
            (shoulders[1][0] + 10 * scale, shoulders[1][1] - 6 * scale),
            (cx + 66 * scale, base_y - 182 * scale),
            hips[1],
            (cx + 42 * scale, base_y - 48 * scale),
            (cx + 22 * scale, base_y + 154 * scale),
            right_ankle,
        ],
        fill=trim,
        width=max(3, int(7 * scale)),
        joint="curve",
    )
    rim.line(
        [shoulders[1], right_elbow, right_wrist],
        fill=trim,
        width=max(3, int(7 * scale)),
        joint="curve",
    )
    rim.arc(head_box, start=300, end=70, fill=trim, width=max(3, int(5 * scale)))
    rim.rounded_rectangle(neck, radius=8 * scale, outline=trim, width=max(2, int(4 * scale)))

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(26))
    rim_layer = rim_layer.filter(ImageFilter.GaussianBlur(0.8))

    base.alpha_composite(glow_layer)
    base.alpha_composite(main_layer)
    base.alpha_composite(rim_layer)


def add_big_2x(base: Image.Image) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = load_font(360)
    draw.text(
        (512, 300),
        "2X",
        font=font,
        fill=(255, 125, 42, 62),
        anchor="mm",
        stroke_width=8,
        stroke_fill=(255, 194, 92, 26),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    base.alpha_composite(layer)


def draw_banner(base: Image.Image, y0: int, y1: int, text: str, font: ImageFont.ImageFont) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle((116, y0, 908, y1), radius=24, fill=(8, 8, 10, 168), outline=(235, 170, 70, 165), width=3)
    draw.text((512, (y0 + y1) / 2 + 2), text, font=font, fill=(255, 236, 210, 245), anchor="mm")
    layer = layer.filter(ImageFilter.GaussianBlur(0.2))
    base.alpha_composite(layer)


def add_text(base: Image.Image) -> None:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    title_font = load_font(86)
    mid_font = load_font(62)
    footer_font = load_font(44)

    draw_banner(base, 66, 146, TOP_BANNER, title_font)
    draw_banner(base, 902, 968, BOTTOM_BANNER, footer_font)

    shadow_draw.text(
        (512, 825),
        MID_LABEL,
        font=mid_font,
        fill=(0, 0, 0, 220),
        anchor="mm",
        stroke_width=6,
        stroke_fill=(0, 0, 0, 220),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    base.alpha_composite(shadow)

    text_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    draw.text(
        (512, 818),
        MID_LABEL,
        font=mid_font,
        fill=(255, 236, 210, 255),
        anchor="mm",
        stroke_width=3,
        stroke_fill=(195, 60, 34, 220),
    )
    base.alpha_composite(text_layer)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))
    draw_vertical_gradient(image)
    image = image.convert("RGBA")

    add_background_glow(image)
    add_angled_panels(image)
    draw_badge_rings(image)
    draw_shield(image)
    add_big_2x(image)
    draw_power_figure(image, 512, 708, 1.0, "center")
    draw_power_figure(image, 252, 748, 0.8, "left")
    draw_power_figure(image, 772, 748, 0.8, "right")
    add_text(image)
    add_vignette(image)

    image.save(OUTPUT, format="PNG", optimize=True)
    print(f"saved {OUTPUT}")


if __name__ == "__main__":
    main()
