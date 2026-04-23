from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


WIDTH = 1024
HEIGHT = 1024
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "telegram-gym-chat-cover.png"

TITLE_TEXT = "\u041c\u0423\u0416\u0421\u041a\u041e\u0419 \u0421\u041f\u041e\u0420\u0422 \u0427\u0410\u0422"
COUNT_TEXT = "2"
BANNER_TEXT = "\u0420\u0410\u0417\u0410 \u0412 \u041d\u0415\u0414\u0415\u041b\u042e"
TAGLINE_TEXT = (
    "\u0421\u0418\u041b\u0410 \u2022 "
    "\u0420\u0415\u0416\u0418\u041c \u2022 "
    "\u0414\u0418\u0421\u0426\u0418\u041f\u041b\u0418\u041d\u0410"
)

DISPLAY_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoSansDisplay-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

BODY_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def load_font(size: int, display: bool = False) -> ImageFont.FreeTypeFont:
    candidates = DISPLAY_FONT_CANDIDATES if display else BODY_FONT_CANDIDATES
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def make_vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    base = Image.new("RGB", size, top)
    pixels = base.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        row = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(width):
            pixels[x, y] = row
    return base


def add_soft_glow(base: Image.Image, bbox: tuple[int, int, int, int], color: tuple[int, int, int, int], blur_radius: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse(bbox, fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    base.alpha_composite(glow)


def draw_stripes(layer: Image.Image) -> None:
    stripes = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(stripes)
    stripe_color = (255, 255, 255, 14)
    for offset in range(-HEIGHT, WIDTH, 90):
        draw.line((offset, 0, offset + HEIGHT, HEIGHT), fill=stripe_color, width=16)
    stripes = stripes.filter(ImageFilter.GaussianBlur(2))
    layer.alpha_composite(stripes)


def draw_hex_badge(draw: ImageDraw.ImageDraw, cx: int, cy: int, width: int, height: int, fill: tuple[int, int, int, int], outline: tuple[int, int, int, int], outline_width: int) -> None:
    dx = width // 2
    dy = height // 2
    notch = width // 7
    points = [
        (cx - dx + notch, cy - dy),
        (cx + dx - notch, cy - dy),
        (cx + dx, cy),
        (cx + dx - notch, cy + dy),
        (cx - dx + notch, cy + dy),
        (cx - dx, cy),
    ]
    draw.polygon(points, fill=fill, outline=outline)
    if outline_width > 1:
        inner = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        inner_draw = ImageDraw.Draw(inner)
        inner_draw.line(points + [points[0]], fill=outline, width=outline_width, joint="curve")
        draw.bitmap((0, 0), inner)


def centered_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, xy: tuple[int, int], fill: tuple[int, int, int], stroke_fill: tuple[int, int, int], stroke_width: int, anchor: str = "mm") -> None:
    x, y = xy
    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        anchor=anchor,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def draw_dumbbell(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, color: tuple[int, int, int, int]) -> None:
    plate_w = int(22 * scale)
    plate_h = int(56 * scale)
    gap = int(12 * scale)
    bar_w = int(44 * scale)
    draw.rounded_rectangle((x - plate_w - gap - bar_w // 2, y - plate_h // 2, x - gap - bar_w // 2, y + plate_h // 2), radius=8, fill=color)
    draw.rounded_rectangle((x + gap + bar_w // 2, y - plate_h // 2, x + plate_w + gap + bar_w // 2, y + plate_h // 2), radius=8, fill=color)
    draw.rounded_rectangle((x - bar_w // 2, y - int(8 * scale), x + bar_w // 2, y + int(8 * scale)), radius=6, fill=color)


def draw_person(layer: Image.Image, x: int, base_y: int, scale: float, pose: str) -> None:
    glow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    glow = ImageDraw.Draw(glow_layer)
    draw = ImageDraw.Draw(layer)

    body_color = (17, 18, 22, 255)
    glow_color = (255, 120, 30, 160)

    head_r = int(34 * scale)
    shoulder_y = base_y - int(260 * scale)
    hip_y = base_y - int(120 * scale)
    knee_y = base_y - int(34 * scale)
    hand_y = shoulder_y + int(18 * scale)
    shoulder_w = int(150 * scale)
    waist_w = int(74 * scale)
    leg_spread = int(70 * scale)
    arm_offset = int(148 * scale)
    stroke = int(40 * scale)

    torso = [
        (x - shoulder_w, shoulder_y),
        (x + shoulder_w, shoulder_y),
        (x + waist_w, hip_y),
        (x - waist_w, hip_y),
    ]

    for d in (glow, draw):
        color = glow_color if d is glow else body_color
        width = stroke + 12 if d is glow else stroke
        d.ellipse((x - head_r, shoulder_y - head_r * 2 - int(12 * scale), x + head_r, shoulder_y - int(12 * scale)), fill=color)
        d.polygon(torso, fill=color)
        d.rounded_rectangle((x - int(45 * scale), hip_y - int(12 * scale), x + int(45 * scale), hip_y + int(72 * scale)), radius=int(22 * scale), fill=color)

        if pose == "barbell":
            left_hand = (x - arm_offset, shoulder_y - int(118 * scale))
            right_hand = (x + arm_offset, shoulder_y - int(118 * scale))
            d.line((x - shoulder_w + int(20 * scale), shoulder_y + int(10 * scale), left_hand[0], left_hand[1]), fill=color, width=width, joint="curve")
            d.line((x + shoulder_w - int(20 * scale), shoulder_y + int(10 * scale), right_hand[0], right_hand[1]), fill=color, width=width, joint="curve")
            d.line((left_hand[0], left_hand[1], right_hand[0], right_hand[1]), fill=color, width=max(12, int(16 * scale)))
            plate_h = int(112 * scale)
            for center in (left_hand[0] - int(66 * scale), left_hand[0] - int(30 * scale), right_hand[0] + int(30 * scale), right_hand[0] + int(66 * scale)):
                d.rounded_rectangle((center - int(10 * scale), left_hand[1] - plate_h // 2, center + int(10 * scale), left_hand[1] + plate_h // 2), radius=int(5 * scale), fill=color)
        else:
            left_hand = (x - arm_offset + int(18 * scale), hand_y + int(72 * scale))
            right_hand = (x + arm_offset - int(18 * scale), hand_y + int(72 * scale))
            d.line((x - shoulder_w + int(12 * scale), shoulder_y + int(10 * scale), left_hand[0], left_hand[1]), fill=color, width=width, joint="curve")
            d.line((x + shoulder_w - int(12 * scale), shoulder_y + int(10 * scale), right_hand[0], right_hand[1]), fill=color, width=width, joint="curve")
            draw_dumbbell(d, left_hand[0], left_hand[1] + int(34 * scale), scale * 0.95, color)
            draw_dumbbell(d, right_hand[0], right_hand[1] + int(34 * scale), scale * 0.95, color)

        d.line((x - int(28 * scale), hip_y + int(44 * scale), x - leg_spread, knee_y), fill=color, width=width, joint="curve")
        d.line((x - leg_spread, knee_y, x - leg_spread - int(10 * scale), base_y), fill=color, width=width, joint="curve")
        d.line((x + int(28 * scale), hip_y + int(44 * scale), x + leg_spread, knee_y), fill=color, width=width, joint="curve")
        d.line((x + leg_spread, knee_y, x + leg_spread + int(10 * scale), base_y), fill=color, width=width, joint="curve")

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(int(20 * scale)))
    layer.alpha_composite(glow_layer)
    draw = ImageDraw.Draw(layer)
    draw.ellipse((x - head_r, shoulder_y - head_r * 2 - int(12 * scale), x + head_r, shoulder_y - int(12 * scale)), fill=body_color)
    draw.polygon(torso, fill=body_color)
    draw.rounded_rectangle((x - int(45 * scale), hip_y - int(12 * scale), x + int(45 * scale), hip_y + int(72 * scale)), radius=int(22 * scale), fill=body_color)

    if pose == "barbell":
        left_hand = (x - arm_offset, shoulder_y - int(118 * scale))
        right_hand = (x + arm_offset, shoulder_y - int(118 * scale))
        draw.line((x - shoulder_w + int(20 * scale), shoulder_y + int(10 * scale), left_hand[0], left_hand[1]), fill=body_color, width=stroke, joint="curve")
        draw.line((x + shoulder_w - int(20 * scale), shoulder_y + int(10 * scale), right_hand[0], right_hand[1]), fill=body_color, width=stroke, joint="curve")
        draw.line((left_hand[0], left_hand[1], right_hand[0], right_hand[1]), fill=(214, 214, 224, 255), width=max(12, int(16 * scale)))
        plate_h = int(112 * scale)
        for center in (left_hand[0] - int(66 * scale), left_hand[0] - int(30 * scale), right_hand[0] + int(30 * scale), right_hand[0] + int(66 * scale)):
            draw.rounded_rectangle((center - int(10 * scale), left_hand[1] - plate_h // 2, center + int(10 * scale), left_hand[1] + plate_h // 2), radius=int(5 * scale), fill=(214, 214, 224, 255))
    else:
        left_hand = (x - arm_offset + int(18 * scale), hand_y + int(72 * scale))
        right_hand = (x + arm_offset - int(18 * scale), hand_y + int(72 * scale))
        draw.line((x - shoulder_w + int(12 * scale), shoulder_y + int(10 * scale), left_hand[0], left_hand[1]), fill=body_color, width=stroke, joint="curve")
        draw.line((x + shoulder_w - int(12 * scale), shoulder_y + int(10 * scale), right_hand[0], right_hand[1]), fill=body_color, width=stroke, joint="curve")
        draw_dumbbell(draw, left_hand[0], left_hand[1] + int(34 * scale), scale * 0.95, (214, 214, 224, 255))
        draw_dumbbell(draw, right_hand[0], right_hand[1] + int(34 * scale), scale * 0.95, (214, 214, 224, 255))

    draw.line((x - int(28 * scale), hip_y + int(44 * scale), x - leg_spread, knee_y), fill=body_color, width=stroke, joint="curve")
    draw.line((x - leg_spread, knee_y, x - leg_spread - int(10 * scale), base_y), fill=body_color, width=stroke, joint="curve")
    draw.line((x + int(28 * scale), hip_y + int(44 * scale), x + leg_spread, knee_y), fill=body_color, width=stroke, joint="curve")
    draw.line((x + leg_spread, knee_y, x + leg_spread + int(10 * scale), base_y), fill=body_color, width=stroke, joint="curve")


def main() -> None:
    background = make_vertical_gradient((WIDTH, HEIGHT), (9, 10, 14), (20, 20, 28)).convert("RGBA")

    add_soft_glow(background, (150, 80, 874, 700), (180, 28, 20, 110), 110)
    add_soft_glow(background, (180, 250, 844, 980), (245, 145, 20, 92), 130)
    add_soft_glow(background, (340, 180, 684, 540), (255, 220, 120, 58), 80)
    draw_stripes(background)

    frame = ImageDraw.Draw(background)
    frame.rounded_rectangle((24, 24, WIDTH - 24, HEIGHT - 24), radius=42, outline=(220, 166, 78, 255), width=8)
    frame.rounded_rectangle((48, 48, WIDTH - 48, HEIGHT - 48), radius=34, outline=(255, 255, 255, 44), width=2)

    accent = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    accent_draw = ImageDraw.Draw(accent)
    accent_draw.polygon([(512, 150), (612, 210), (412, 210)], fill=(255, 175, 43, 170))
    accent_draw.polygon([(512, 874), (612, 814), (412, 814)], fill=(255, 175, 43, 120))
    accent = accent.filter(ImageFilter.GaussianBlur(8))
    background.alpha_composite(accent)

    figure_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_person(figure_layer, 284, 812, 0.83, "dumbbell")
    draw_person(figure_layer, 512, 826, 1.02, "barbell")
    draw_person(figure_layer, 740, 812, 0.83, "dumbbell")
    background.alpha_composite(figure_layer)

    text_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    text = ImageDraw.Draw(text_layer)

    title_font = load_font(78, display=True)
    count_font = load_font(328, display=True)
    banner_font = load_font(64, display=False)
    tagline_font = load_font(40, display=False)

    centered_text(text, TITLE_TEXT, title_font, (512, 122), (240, 240, 242), (18, 18, 22), 4)
    centered_text(text, COUNT_TEXT, count_font, (512, 312), (255, 201, 58), (20, 20, 22), 10)

    banner = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    banner_draw = ImageDraw.Draw(banner)
    draw_hex_badge(
        banner_draw,
        512,
        458,
        740,
        112,
        (23, 24, 30, 226),
        (255, 180, 62, 255),
        6,
    )
    banner = banner.filter(ImageFilter.GaussianBlur(0))
    background.alpha_composite(banner)
    background.alpha_composite(text_layer)

    text = ImageDraw.Draw(background)
    centered_text(text, BANNER_TEXT, banner_font, (512, 458), (246, 246, 248), (18, 18, 22), 3)
    centered_text(text, TAGLINE_TEXT, tagline_font, (512, 942), (233, 233, 235), (18, 18, 22), 2)

    vignette = Image.new("L", (WIDTH, HEIGHT), 255)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse((-180, -120, WIDTH + 180, HEIGHT + 180), fill=215)
    vignette = ImageChops.invert(vignette.filter(ImageFilter.GaussianBlur(90)))
    vignette_rgba = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vignette_rgba.putalpha(vignette)
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 70))
    background = Image.alpha_composite(background, Image.composite(shadow, Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)), vignette))

    background.save(OUTPUT, format="PNG")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
