
import pymupdf
import pytesseract
import cv2
import numpy as np

from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pdf_path = r"D:\InsureAssist\scanned_hospital_bill_hd.pdf"

doc = pymupdf.open(pdf_path)
page = doc[0]

# Render at 400 DPI
pix = page.get_pixmap(
    dpi=400,
    alpha=False
)

image = Image.frombytes(
    "RGB",
    [pix.width, pix.height],
    pix.samples
)

# Crop the financial summary section.
width, height = image.size

left = int(width * 0.03)
top = int(height * 0.64)
right = int(width * 0.97)
bottom = int(height * 0.87)

cropped = image.crop(
    (left, top, right, bottom)
)

# Upscale for better OCR.
image_array = np.array(cropped)

upscaled = cv2.resize(
    image_array,
    None,
    fx=2,
    fy=2,
    interpolation=cv2.INTER_CUBIC
)

gray = cv2.cvtColor(
    upscaled,
    cv2.COLOR_RGB2GRAY
)

threshold = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)[1]

# Save crop for visual inspection.
cv2.imwrite(
    r"D:\InsureAssist\amount_crop.png",
    threshold
)

print("\n========== OCR USING PSM 6 ==========\n")

text1 = pytesseract.image_to_string(
    threshold,
    lang="eng",
    config="--oem 3 --psm 6"
)

print(text1)

print("\n========== OCR USING PSM 4 ==========\n")

text2 = pytesseract.image_to_string(
    threshold,
    lang="eng",
    config="--oem 3 --psm 4"
)

print(text2)

