"""Cut out the background, boost local contrast, flatten onto white.

Run once per photo (local only):  python scripts/prep_photo.py path/to/photo.jpg
Writes source-prepped.png (grayscale) in the repo root.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent

# head-and-shoulders crop as fractions of the photo (left, top, right, bottom)
CROP = (0.14, 0.0, 0.88, 0.62)

src = Image.open(sys.argv[1]).convert("RGB")
w, h = src.size
src = src.crop((int(CROP[0] * w), int(CROP[1] * h), int(CROP[2] * w), int(CROP[3] * h)))
cut = remove(src)  # RGBA, background alpha = 0


rgba = np.array(cut)
gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)

alpha = rgba[:, :, 3].astype(np.float32) / 255.0
flat = (gray * alpha + 255 * (1 - alpha)).astype(np.uint8)

Image.fromarray(flat).save(ROOT / "source-prepped.png")
print("wrote source-prepped.png", flat.shape[::-1])
