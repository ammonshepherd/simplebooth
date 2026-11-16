#!/usr/bin/env python3
"""Preview the photobooth strip without the Pi, camera or printer.

Uses the same layout code as the booth (strip.py), so what you see here is
what gets printed. Writes into the preview/ folder:

  strip.png        the single strip (what's uploaded to Google Drive)
  print_sheet.png  the double-wide image sent to the printer, with the
                   PRINT_OFFSET_X/Y from strip.py applied and a dashed cut line

Usage:
  python3 preview_strip.py                    # made-up sample photos
  python3 preview_strip.py a.jpg b.jpg c.jpg  # your own photos
  python3 preview_strip.py --logo other.png --text "Line 1\\nLine 2"

Only needs Pillow. If the Bangers font isn't installed (it's only on the Pi)
a similar fallback font is used, so letter widths may differ slightly.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

import strip

HERE = Path(__file__).resolve().parent
OUT = HERE / "preview"

SAMPLE_COLORS = [((70, 110, 160), (200, 220, 240)),
                 ((160, 90, 60), (245, 215, 180)),
                 ((60, 130, 90), (205, 235, 210))]


def sample_photo(n):
  """A stand-in camera photo: gradient with a simple figure and a label."""
  w, h = strip.PHOTO_SIZE
  (r1, g1, b1), (r2, g2, b2) = SAMPLE_COLORS[(n - 1) % len(SAMPLE_COLORS)]
  img = Image.new("RGB", (w, h))
  d = ImageDraw.Draw(img)
  for y in range(h):
    t = y / (h - 1)
    d.line([(0, y), (w, y)], fill=(int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t), int(b1 + (b2 - b1) * t)))
  for cx in (w * 0.38, w * 0.62):
    d.ellipse([cx - 70, 170, cx + 70, 310], fill=(255, 255, 255))
    d.rounded_rectangle([cx - 130, 330, cx + 130, h + 40], radius=90, fill=(255, 255, 255))
  font = strip.load_font(60)
  d.text((30, 25), f"Photo {n}", font=font, fill=(255, 255, 255))
  # thin outline so the photo edge is visible against the white strip
  d.rectangle([0, 0, w - 1, h - 1], outline=(0, 0, 0), width=2)
  return img


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument("photos", nargs="*", help="three photos to use (default: samples)")
  ap.add_argument("--logo", help="logo file (default: LOGO in strip.py)")
  ap.add_argument("--text", help="bottom text, use \\n for a line break (default: BOTTOM_TEXT in strip.py)")
  args = ap.parse_args()

  photos = []
  if args.photos:
    for p in args.photos:
      img = Image.open(p).convert("RGB")
      if img.size != strip.PHOTO_SIZE:   # camera output is already this size
        img = img.resize(strip.PHOTO_SIZE)
      photos.append(img)
  else:
    photos = [sample_photo(n) for n in range(1, 4)]

  text = args.text.replace("\\n", "\n") if args.text else None
  OUT.mkdir(exist_ok=True)

  booth = strip.build_strip(photos, logo=args.logo, bottom_text=text)
  booth.save(OUT / "strip.png")

  sheet = strip.build_print_sheet(booth)
  d = ImageDraw.Draw(sheet)
  x = strip.STRIP_WIDTH
  for y in range(0, sheet.height, 60):
    d.line([(x, y), (x, y + 30)], fill=(220, 0, 0), width=4)
  sheet.save(OUT / "print_sheet.png")

  print(f"Wrote {OUT / 'strip.png'}")
  print(f"Wrote {OUT / 'print_sheet.png'}  (red dashes = cut line, not printed)")


if __name__ == "__main__":
  main()
