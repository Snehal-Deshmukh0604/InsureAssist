import pymupdf

source = r"D:\InsureAssist\medikloud-hospital-billing-format.pdf"
output = r"D:\InsureAssist\scanned_hospital_bill_hd.pdf"

doc = pymupdf.open(source)

# Page 4 (index 3)
page = doc[3]

# Render at 300 DPI
pix = page.get_pixmap(dpi=300, alpha=False)

# Convert page into an image-only PDF
image_bytes = pix.tobytes("png")

new_doc = pymupdf.open()
new_page = new_doc.new_page(
    width=page.rect.width,
    height=page.rect.height
)

new_page.insert_image(
    new_page.rect,
    stream=image_bytes
)

new_doc.save(output)

print("High-quality scanned PDF created!")
print("Saved at:", output)
print("Image resolution:", pix.width, "x", pix.height)