from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "samples" / "input"
FONT_PATHS = [
    Path("C:/Windows/Fonts/malgun.ttf"),
    Path("C:/Windows/Fonts/malgunbd.ttf"),
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_PATHS:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def create_canvas(bg: tuple[int, int, int], accent: tuple[int, int, int], title: str, subtitle: str) -> Image.Image:
    image = Image.new("RGB", (1080, 1440), bg)
    draw = ImageDraw.Draw(image)
    title_font = load_font(76)
    body_font = load_font(42)

    draw.rounded_rectangle((90, 100, 990, 1320), radius=42, outline=accent, width=10)
    draw.ellipse((740, 180, 980, 420), fill=accent)
    draw.rounded_rectangle((150, 320, 730, 960), radius=54, fill=(255, 255, 255))
    draw.rounded_rectangle((240, 1010, 910, 1200), radius=32, fill=accent)
    draw.text((130, 120), title, fill=(255, 255, 255), font=title_font)
    draw.text((188, 420), subtitle, fill=(50, 42, 36), font=body_font)
    draw.text((290, 1060), "PHASE 1 DEMO", fill=(255, 255, 255), font=body_font)
    return image.filter(ImageFilter.GaussianBlur(radius=0.3))


def write_sample(folder: str, name: str, bg: tuple[int, int, int], accent: tuple[int, int, int], title: str, subtitle: str) -> None:
    target_dir = SAMPLES_DIR / folder
    ensure_dir(target_dir)
    canvas = create_canvas(bg, accent, title, subtitle)
    canvas.save(target_dir / name, format="PNG")


def main() -> None:
    write_sample(
        "cafe",
        "cafe-latte-01.png",
        (95, 58, 41),
        (235, 166, 92),
        "성수 신메뉴",
        "딸기 크림 라떼를\n밝게 소개하는 샘플 이미지",
    )
    write_sample(
        "cafe",
        "cafe-dessert-02.png",
        (56, 44, 70),
        (244, 201, 140),
        "오늘의 디저트",
        "포스터형 피드와\n숏폼 배경 테스트용 샘플",
    )
    write_sample(
        "restaurant",
        "restaurant-lunch-01.png",
        (44, 55, 38),
        (228, 124, 54),
        "점심 특선",
        "역삼 점심 할인형\n프로모션 샘플 이미지",
    )
    write_sample(
        "restaurant",
        "restaurant-menu-02.png",
        (33, 43, 63),
        (241, 191, 90),
        "오늘의 한 상",
        "메뉴/혜택/CTA 조합을\n검증하기 위한 샘플",
    )


if __name__ == "__main__":
    main()
