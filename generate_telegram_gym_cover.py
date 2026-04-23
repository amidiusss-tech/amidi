from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 1080, 1080
OUTPUT_PATH = "telegram_gym_chat_cover.png"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def blend_channel(top: int, bottom: int, t: float) -> int:
    return int(top * (1.0 - t) + bottom * t)


def draw_vertical_gradient(image: Image.Image, top_rgb: tuple[int, int, int], bottom_rgb: tuple[int, int, int]) -> None:
    pixels = image.load()
    for y in range(HEIGHT):
        t = y / float(HEIGHT - 1)
        color = (
            blend_channel(top_rgb[0], bottom_rgb[0], t),
            blend_channel(top_rgb[1], bottom_rgb[1], t),
            blend_channel(top_rgb[2], bottom_rgb[2], t),
        )
        for x in range(WIDTH):
            pixels[x, y] = color


def centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, font: ImageFont.ImageFont, color: tuple[int, int, int]) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), text, font=font, fill=color)
    return y + text_height


def draw_lifter(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, color: tuple[int, int, int]) -> None:
    head_r = int(20 * scale)
    torso_w = int(46 * scale)
    torso_h = int(80 * scale)
    shoulder_y = cy - int(60 * scale)
    hip_y = cy + int(35 * scale)
    arm_span = int(145 * scale)
    bar_y = shoulder_y - int(35 * scale)
    arm_w = int(11 * scale)
    leg_w = int(14 * scale)

    # Head
    draw.ellipse((cx - head_r, shoulder_y - head_r * 2 - 10, cx + head_r, shoulder_y - 10), fill=color)

    # Torso
    draw.rounded_rectangle(
        (cx - torso_w // 2, shoulder_y, cx + torso_w // 2, shoulder_y + torso_h),
        radius=int(10 * scale),
        fill=color,
    )

    # Arms
    draw.rectangle((cx - arm_span, bar_y - arm_w // 2, cx + arm_span, bar_y + arm_w // 2), fill=color)
    draw.rectangle((cx - torso_w // 2 - arm_w, shoulder_y + 8, cx - torso_w // 2, bar_y), fill=color)
    draw.rectangle((cx + torso_w // 2, shoulder_y + 8, cx + torso_w // 2 + arm_w, bar_y), fill=color)

    # Barbell plates
    plate_h = int(50 * scale)
    plate_w = int(16 * scale)
    for side in (-1, 1):
        plate_x = cx + side * arm_span
        for i in range(3):
            offset = side * i * (plate_w + int(4 * scale))
            draw.rectangle(
                (
                    plate_x + offset - plate_w // 2,
                    bar_y - plate_h // 2,
                    plate_x + offset + plate_w // 2,
                    bar_y + plate_h // 2,
                ),
                fill=color,
            )

    # Legs
    draw.polygon(
        [
            (cx - torso_w // 3, shoulder_y + torso_h),
            (cx - torso_w // 2 - int(20 * scale), hip_y + int(70 * scale)),
            (cx - torso_w // 2 - int(5 * scale), hip_y + int(80 * scale)),
            (cx - leg_w, shoulder_y + torso_h),
        ],
        fill=color,
    )
    draw.polygon(
        [
            (cx + torso_w // 3, shoulder_y + torso_h),
            (cx + torso_w // 2 + int(20 * scale), hip_y + int(70 * scale)),
            (cx + torso_w // 2 + int(5 * scale), hip_y + int(80 * scale)),
            (cx + leg_w, shoulder_y + torso_h),
        ],
        fill=color,
    )


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 20))
    draw_vertical_gradient(image, (14, 16, 19), (71, 20, 20))
    draw = ImageDraw.Draw(image)

    # Subtle grid for gym-industrial texture
    grid_color = (58, 58, 58)
    for x in range(0, WIDTH, 80):
        draw.line((x, 0, x, HEIGHT), fill=grid_color, width=1)
    for y in range(0, HEIGHT, 80):
        draw.line((0, y, WIDTH, y), fill=grid_color, width=1)

    # Neon red glow behind athletes
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((190, 260, 890, 960), fill=(225, 40, 40, 115))
    glow = glow.filter(ImageFilter.GaussianBlur(45))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Athlete silhouettes
    draw_lifter(draw, cx=340, cy=680, scale=1.05, color=(18, 18, 20))
    draw_lifter(draw, cx=740, cy=700, scale=1.20, color=(11, 11, 13))

    # Strong top bar and border
    draw.rectangle((70, 70, WIDTH - 70, 85), fill=(214, 56, 56))
    draw.rectangle((70, 995, WIDTH - 70, 1010), fill=(214, 56, 56))
    draw.rounded_rectangle((35, 35, WIDTH - 35, HEIGHT - 35), radius=22, outline=(190, 58, 58), width=6)

    title_font = load_font(110)
    subtitle_font = load_font(62)
    accent_font = load_font(84)
    small_font = load_font(42)

    y = 125
    y = centered_text(draw, y, "ЖЕЛЕЗНЫЙ ЧАТ", title_font, (245, 245, 245))
    y += 8
    y = centered_text(draw, y, "КАЧАЛКА & СПОРТ", subtitle_font, (229, 229, 229))
    y += 22
    y = centered_text(draw, y, "2 РАЗА В НЕДЕЛЮ", accent_font, (235, 70, 70))
    y += 18
    centered_text(draw, y, "СИЛА • ДИСЦИПЛИНА • РЕЗУЛЬТАТ", small_font, (206, 206, 206))

    image.save(OUTPUT_PATH, format="PNG")
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
