import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
page = doc[157] # 0-indexed 157 = Page 158

# Let's render the entire page 158 to an image so we can inspect the exact coordinates
pix = page.get_pixmap(dpi=150)
pix.save("d:/pps/numerical-methods-web/public/images/page_158_full.png")
print("Saved page_158_full.png with dimensions:", pix.width, pix.height)

# Page rect is (0, 0, 528, 664)
# Let's crop the region between y=90 and y=280:
# Left half: Figure P3-23
crop_p323 = fitz.Rect(70, 95, 270, 275)
pix_p323 = page.get_pixmap(clip=crop_p323, dpi=300)
pix_p323.save("d:/pps/numerical-methods-web/public/images/test_p3_23.png")
print("Saved test_p3_23.png:", pix_p323.width, pix_p323.height)

# Right half: Figure P3-24
crop_p324 = fitz.Rect(270, 95, 485, 275)
pix_p324 = page.get_pixmap(clip=crop_p324, dpi=300)
pix_p324.save("d:/pps/numerical-methods-web/public/images/test_p3_24.png")
print("Saved test_p3_24.png:", pix_p324.width, pix_p324.height)
