from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


SIZE = 1024
OUTPUT_PNG = Path("telegram_gym_chat_cover.png")
OUTPUT_JPG = Path("telegram_gym_chat_cover.jpg")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def vertical_gradient(size, top_color, bottom_color):
    width, height = size
    image = Image.new("RGB", size, top_color)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        mix = y / max(height - 1, 1)
        color = tuple(
            int(top_color[i] * (1 - mix) + bottom_color[i] * mix) for i in range(3)
        )
        draw.line((0, y, width, y), fill=color)
    return image


def add_diagonal_stripes(base):
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    spacing = 90
    for start in range(-SIZE, SIZE * 2, spacing):
        draw.polygon(
            [
                (start, 0),
                (start + 22, 0),
                (start + SIZE + 22, SIZE),
                (start + SIZE, SIZE),
            ],
            fill=(255, 255, 255, 18),
        )
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def add_vignette(image):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((-180, -180, SIZE + 180, SIZE + 180), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(120))
    mask = ImageChops.invert(mask)
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow.putalpha(mask.point(lambda value: int(value * 0.78)))
    return Image.alpha_composite(image, shadow)


def centered_text(draw, text, y, font, fill, stroke_fill=None, stroke_width=0):
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    width = bbox[2] - bbox[0]
    x = (SIZE - width) / 2
    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        stroke_fill=stroke_fill,
        stroke_width=stroke_width,
    )


def draw_glow_circle(base, center, radius, color, blur):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, glow)


def draw_dumbbell(draw, center_x, center_y, scale, color):
    bar_w = int(160 * scale)
    bar_h = int(18 * scale)
    plate_w = int(26 * scale)
    plate_h = int(90 * scale)
    gap = int(10 * scale)
    draw.rounded_rectangle(
        (
            center_x - bar_w // 2,
            center_y - bar_h // 2,
            center_x + bar_w // 2,
            center_y + bar_h // 2,
        ),
        radius=bar_h // 2,
        fill=color,
    )
    for side in (-1, 1):
        outer = center_x + side * (bar_w // 2 + gap + plate_w)
        inner = center_x + side * (bar_w // 2 + gap)
        left = min(inner, outer)
        right = max(inner, outer)
        draw.rounded_rectangle(
            (left, center_y - plate_h // 2, right, center_y + plate_h // 2),
            radius=int(8 * scale),
            fill=color,
        )
        outer2 = center_x + side * (bar_w // 2 + gap + plate_w + int(18 * scale))
        left2 = min(outer, outer2)
        right2 = max(outer, outer2)
        draw.rounded_rectangle(
            (left2, center_y - int(70 * scale), right2, center_y + int(70 * scale)),
            radius=int(8 * scale),
            fill=color,
        )


def draw_shield(draw, box):
    x1, y1, x2, y2 = box
    mid_x = (x1 + x2) / 2
    draw.polygon(
        [
            (mid_x, y1),
            (x2, y1 + 70),
            (x2 - 38, y2 - 110),
            (mid_x, y2),
            (x1 + 38, y2 - 110),
            (x1, y1 + 70),
        ],
        fill=(92, 13, 15, 255),
        outline=(232, 183, 60, 255),
        width=6,
    )


def draw_male_silhouette(draw, offset_x, scale, fill, outline):
    cx = SIZE // 2 + offset_x
    top = int(260 * scale)
    head_r = int(36 * scale)

    draw.ellipse(
        (cx - head_r, top, cx + head_r, top + 2 * head_r),
        fill=fill,
        outline=outline,
        width=max(2, int(4 * scale)),
    )

    shoulder_y = top + int(108 * scale)
    hip_y = shoulder_y + int(180 * scale)
    knee_y = hip_y + int(150 * scale)
    foot_y = knee_y + int(130 * scale)
    shoulder_half = int(110 * scale)
    waist_half = int(58 * scale)
    hip_half = int(82 * scale)

    torso = [
        (cx - shoulder_half, shoulder_y),
        (cx - waist_half, shoulder_y + int(80 * scale)),
        (cx - hip_half, hip_y),
        (cx + hip_half, hip_y),
        (cx + waist_half, shoulder_y + int(80 * scale)),
        (cx + shoulder_half, shoulder_y),
    ]
    draw.polygon(torso, fill=fill, outline=outline)

    arm_w = int(28 * scale)
    bicep_h = int(96 * scale)
    forearm_h = int(112 * scale)
    for side in (-1, 1):
        arm_x = cx + side * (shoulder_half + int(16 * scale))
        draw.rounded_rectangle(
            (
                arm_x - arm_w // 2,
                shoulder_y + int(4 * scale),
                arm_x + arm_w // 2,
                shoulder_y + bicep_h,
            ),
            radius=arm_w // 2,
            fill=fill,
            outline=outline,
            width=max(2, int(4 * scale)),
        )
        hand_x = arm_x + side * int(42 * scale)
        draw.rounded_rectangle(
            (
                min(arm_x, hand_x) - arm_w // 2,
                shoulder_y + bicep_h - int(10 * scale),
                max(arm_x, hand_x) + arm_w // 2,
                shoulder_y + bicep_h + forearm_h,
            ),
            radius=arm_w // 2,
            fill=fill,
            outline=outline,
            width=max(2, int(4 * scale)),
        )

    thigh_w = int(42 * scale)
    calf_w = int(34 * scale)
    for side in (-1, 1):
        thigh_x = cx + side * int(32 * scale)
        calf_x = cx + side * int(42 * scale)
        draw.rounded_rectangle(
            (
                thigh_x - thigh_w // 2,
                hip_y,
                thigh_x + thigh_w // 2,
                knee_y,
            ),
            radius=thigh_w // 2,
            fill=fill,
            outline=outline,
            width=max(2, int(4 * scale)),
        )
        draw.rounded_rectangle(
            (
                calf_x - calf_w // 2,
                knee_y - int(8 * scale),
                calf_x + calf_w // 2,
                foot_y,
            ),
            radius=calf_w // 2,
            fill=fill,
            outline=outline,
            width=max(2, int(4 * scale)),
        )


def build_image():
    base = vertical_gradient((SIZE, SIZE), (8, 8, 8), (52, 0, 0)).convert("RGBA")
    base = add_diagonal_stripes(base)
    base = draw_glow_circle(base, (SIZE // 2, 350), 260, (255, 188, 54, 48), 90)
    base = draw_glow_circle(base, (SIZE // 2, 680), 320, (215, 0, 0, 72), 120)
    base = add_vignette(base)

    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(
        (60, 48, SIZE - 60, SIZE - 48),
        radius=32,
        outline=(188, 31, 31, 255),
        width=4,
    )
    draw.rounded_rectangle(
        (86, 74, SIZE - 86, SIZE - 74),
        radius=28,
        outline=(233, 182, 59, 180),
        width=2,
    )

    draw_shield(draw, (300, 180, 724, 790))
    draw_male_silhouette(draw, -185, 0.73, (15, 15, 15, 240), (230, 182, 55, 160))
    draw_male_silhouette(draw, 0, 0.95, (10, 10, 10, 255), (245, 195, 75, 190))
    draw_male_silhouette(draw, 185, 0.73, (15, 15, 15, 240), (230, 182, 55, 160))

    draw_dumbbell(draw, 238, 268, 0.72, (232, 182, 60, 255))
    draw_dumbbell(draw, 786, 268, 0.72, (232, 182, 60, 255))
    draw_dumbbell(draw, 250, 842, 0.88, (172, 24, 24, 255))
    draw_dumbbell(draw, 774, 842, 0.88, (172, 24, 24, 255))

    font_small = ImageFont.truetype(FONT_BOLD, 42)
    font_mid = ImageFont.truetype(FONT_BOLD, 64)
    font_big = ImageFont.truetype(FONT_BOLD, 124)
    font_tag = ImageFont.truetype(FONT_REGULAR, 34)

    centered_text(
        draw,
        "МУЖСКОЙ СПОРТ-ЧАТ",
        78,
        font_small,
        fill=(242, 214, 125),
        stroke_fill=(30, 0, 0),
        stroke_width=2,
    )
    centered_text(
        draw,
        "2 РАЗА",
        604,
        font_big,
        fill=(255, 237, 180),
        stroke_fill=(92, 0, 0),
        stroke_width=5,
    )
    centered_text(
        draw,
        "В НЕДЕЛЮ",
        718,
        font_mid,
        fill=(255, 207, 71),
        stroke_fill=(54, 0, 0),
        stroke_width=4,
    )
    centered_text(
        draw,
        "КАЧАЛКА  •  СПОРТ  •  ДИСЦИПЛИНА",
        836,
        font_small,
        fill=(255, 226, 142),
        stroke_fill=(30, 0, 0),
        stroke_width=2,
    )
    centered_text(
        draw,
        "TESTOSTERONE MODE",
        920,
        font_tag,
        fill=(215, 215, 215),
    )

    return base


def main():
    image = build_image()
    image.save(OUTPUT_PNG, optimize=True)
    image.convert("RGB").save(OUTPUT_JPG, quality=95, optimize=True)
    print(f"saved {OUTPUT_PNG}")
    print(f"saved {OUTPUT_JPG}")


if __name__ == "__main__":
    main()
