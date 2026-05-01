#!/usr/bin/env python3
"""Generate a Wi-Fi join QR code as PNG with logo overlay and caption."""

import argparse
import os
import re
import sys
from pathlib import Path

import qrcode
import qrcode.constants
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "qrcodes"
LOGO_PATH = ROOT / "assets" / "wifi.png"
CAPTION_SUFFIX = "Wi-Fi by Acacia"

CODE_RE = re.compile(r"^[A-Z]{3}$")
SPECIAL_CHARS = set(r'\;,":')

FONT_CANDIDATES = [
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
     "/System/Library/Fonts/Supplemental/Arial.ttf"),
    ("/Library/Fonts/Arial Bold.ttf", "/Library/Fonts/Arial.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


def escape_value(value: str) -> str:
    return "".join(f"\\{c}" if c in SPECIAL_CHARS else c for c in value)


def build_payload(ssid: str, password: str, security: str) -> str:
    s = escape_value(ssid)
    if security == "nopass":
        return f"WIFI:T:nopass;S:{s};;"
    p = escape_value(password)
    return f"WIFI:T:{security};S:{s};P:{p};;"


def find_fonts():
    for bold, regular in FONT_CANDIDATES:
        if os.path.exists(bold) and os.path.exists(regular):
            return bold, regular
    return None, None


def make_qr(payload: str) -> Image.Image:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGBA")


def overlay_logo(qr_img: Image.Image, logo_path: Path, ratio: float = 0.18) -> Image.Image:
    logo = Image.open(logo_path).convert("RGBA")
    qw, qh = qr_img.size
    target_w = int(qw * ratio)
    aspect = logo.height / logo.width
    target_h = int(target_w * aspect)
    logo = logo.resize((target_w, target_h), Image.LANCZOS)
    pad = int(target_w * 0.18)
    bg = Image.new("RGBA", (target_w + pad * 2, target_h + pad * 2), (255, 255, 255, 255))
    bg.paste(logo, (pad, pad), logo)
    pos = ((qw - bg.width) // 2, (qh - bg.height) // 2)
    qr_img.paste(bg, pos, bg)
    return qr_img


def add_caption(qr_img: Image.Image, name: str, suffix: str = CAPTION_SUFFIX) -> Image.Image:
    bold_path, reg_path = find_fonts()
    qw, qh = qr_img.size
    name_size = max(48, qw // 14)
    sub_size = max(28, qw // 22)
    if bold_path:
        font_name = ImageFont.truetype(bold_path, name_size)
        font_sub = ImageFont.truetype(reg_path, sub_size)
    else:
        font_name = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    line_gap = sub_size // 2
    top_pad = sub_size
    bottom_pad = sub_size
    strip_h = top_pad + name_size + line_gap + sub_size + bottom_pad

    out = Image.new("RGBA", (qw, qh + strip_h), (255, 255, 255, 255))
    out.paste(qr_img, (0, 0))
    draw = ImageDraw.Draw(out)

    name_bbox = draw.textbbox((0, 0), name, font=font_name)
    name_w = name_bbox[2] - name_bbox[0]
    sub_bbox = draw.textbbox((0, 0), suffix, font=font_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]

    y0 = qh + top_pad
    draw.text(((qw - name_w) // 2, y0), name, fill="black", font=font_name)
    draw.text(
        ((qw - sub_w) // 2, y0 + name_size + line_gap),
        suffix,
        fill="black",
        font=font_sub,
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Wi-Fi join QR code as PNG with logo and caption."
    )
    parser.add_argument("code", help="3-letter uppercase identifier (e.g. AMA)")
    parser.add_argument("name", help="Extended name shown in the caption (e.g. Primula)")
    parser.add_argument("ssid", help="Wi-Fi network SSID")
    parser.add_argument("password", help="Wi-Fi password (ignored when --security nopass)")
    parser.add_argument(
        "--security",
        choices=["WPA", "WEP", "nopass"],
        default="WPA",
        help="Authentication type (default: WPA)",
    )
    args = parser.parse_args()

    if not CODE_RE.match(args.code):
        print(
            f"error: code must match [A-Z]{{3}}, got {args.code!r}",
            file=sys.stderr,
        )
        return 2

    payload = build_payload(args.ssid, args.password, args.security)
    qr_img = make_qr(payload)
    if LOGO_PATH.exists():
        qr_img = overlay_logo(qr_img, LOGO_PATH)
    qr_img = add_caption(qr_img, args.name)

    OUTPUT_DIR.mkdir(exist_ok=True)
    output = OUTPUT_DIR / f"{args.code}-wifi.png"
    qr_img.convert("RGB").save(output)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
