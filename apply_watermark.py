import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from collections import Counter

import platform

# === 設定ファイル空白時のフォント設定 ===
def get_default_font_path():
    system = platform.system()
    if system == "Windows":
        return "arial.ttf"
    elif system == "Darwin":  # macOS
        return "/System/Library/Fonts/SFNS.ttf"
    else:  # Linux系
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# === 設定ファイルの読み込み ===
def load_config(config_path="watermark_config.txt"):
    config = {
        "font_path": get_default_font_path(),
        "font_size": 32,
        "text": "This is a sample image.\nPlease do not repost.",
    }

    if not os.path.exists(config_path):
        return config

    with open(config_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_text = False
    text_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if in_text:
            if line.lower() == "endtext":
                in_text = False
                config["text"] = "\n".join(text_lines)
            else:
                text_lines.append(line)
            continue

        if line.lower() == "text:":
            in_text = True
            text_lines = []
        elif "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()

            # font_size だけは型変換
            if key == "font_size":
                try:
                    config[key] = int(val)
                except ValueError:
                    print(f"[!] font_size の値が整数じゃない: {val}、無視します")
            else:
                config[key] = val

    return config

# === 画像の主色取得 ===
def get_dominant_color(img):
    small = img.resize((50, 50))
    pixels = list(small.getdata())
    most_common = Counter(pixels).most_common(1)[0][0]
    return most_common

# === クロスハッチパターン作成（αを40にして目立たなく） ===
def make_diagonal_stripes(size, base_width=2):
    w, h = size
    scale = min(w, h) / 512
    stripe_width = max(1, int(base_width * scale))
    spacing = stripe_width * 32

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 左下→右上方向の斜め線
    for i in range(-h, w, spacing):
        draw.line([(i, 0), (i + h, h)], fill=(180, 180, 180, 60), width=stripe_width)

    # 左上→右下方向の斜め線
    for i in range(0, w + h, spacing):
        draw.line([(i, 0), (i - h, h)], fill=(180, 180, 180, 60), width=stripe_width)

    return img

# === 中心からフェードアウトするマスク（ぼかし弱め） ===
def make_radial_mask(size):
    w, h = size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    max_r = int((w**2 + h**2)**0.5 / 2)
    for r in range(max_r, 0, -1):
        alpha = int(128 * (1 - (r / max_r)) ** 2) + 16
        draw.ellipse([(w/2 - r, h/2 - r), (w/2 + r, h/2 + r)], fill=alpha)
    return mask.filter(ImageFilter.GaussianBlur(1))



# === 透かし合成処理 ===
def add_watermark(img_path, out_path, config):
    base = Image.open(img_path).convert("RGBA")
    w, h = base.size

    # クロスハッチパターン生成
    stripes = make_diagonal_stripes((w, h))
    # デザイン性を損なったのでマスク外しました
    # mask = make_radial_mask((w, h))
    # stripes.putalpha(mask)
    base = Image.alpha_composite(base, stripes)

    # テキスト描画
    txt_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)
    try:
        font = ImageFont.truetype(config["font_path"], int(config["font_size"]))
    except:
        font = ImageFont.load_default()

    lines = config["text"].split("\n")
    # lines = [line.replace(" ", "\u00A0") for line in lines]

    font_size = int(config["font_size"])
    line_height = font_size + 2  # 適当な余白（行間）

    total_height = line_height * len(lines)
    y = h - total_height - 40

    # 文字色
    shadow_offset = 2
    shadow_color = (0, 0, 0, 150)  # 半透明の黒
    text_color = (255, 255, 255, 200)  # 固定：白

    for line in lines:
        text_w = font.getbbox(line)[2] if hasattr(font, 'getbbox') else font.getsize(line)[0]
        x = (w - text_w) / 2

        # シャドウ（下に少しずらす）
        draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=shadow_color)
        # 本文
        draw.text((x, y), line, font=font, fill=text_color)

        y += line_height

    base = Image.alpha_composite(base, txt_layer)
    base.convert("RGB").save(out_path)

# === メイン処理 ===
def main():
    if len(sys.argv) < 2:
        print("使い方: python apply_watermark.py 画像ファイルまたはフォルダ")
        return

    input_path = sys.argv[1]
    output_dir = "watermarked_output"
    os.makedirs(output_dir, exist_ok=True)
    config = load_config()

    if os.path.isdir(input_path):
        for filename in os.listdir(input_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                in_file = os.path.join(input_path, filename)
                out_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_wm.jpg")
                add_watermark(in_file, out_file, config)
    elif os.path.isfile(input_path):
        filename = os.path.basename(input_path)
        out_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_wm.jpg")
        add_watermark(input_path, out_file, config)
    else:
        print("指定されたパスが無効です")

if __name__ == "__main__":
    main()
