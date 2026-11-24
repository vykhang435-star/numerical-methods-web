import fitz

doc = fitz.open()
img_doc = fitz.open("d:/pps/numerical-methods-web/public/images/hk241_fig_2_beam.png")
rect = img_doc[0].rect
page = doc.new_page(width=rect.width, height=rect.height)
page.insert_image(rect, filename="d:/pps/numerical-methods-web/public/images/hk241_fig_2_beam.png")

# Crop off top 35 points where the black bar is
clean_rect = fitz.Rect(0, 35, rect.width, rect.height)
pix = page.get_pixmap(clip=clean_rect, dpi=200)
pix.save("d:/pps/numerical-methods-web/public/images/hk241_fig_2_beam.png")
print("Cleaned hk241_fig_2_beam.png:", pix.width, pix.height)
