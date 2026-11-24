import pymupdf

pdf_path = r"D:\InsureAssist\scanned_hospital_bill.pdf"

doc = pymupdf.open(pdf_path)
page = doc[0]

pix = page.get_pixmap(matrix=pymupdf.Matrix(3, 3))

output_path = r"D:\InsureAssist\scanned_preview.png"
pix.save(output_path)

print("PDF converted into image successfully!")
print("Image saved at:", output_path)
print("Image dimensions:", pix.width, "x", pix.height)
