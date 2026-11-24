import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
page = doc[222] # Page 223
print("Page 223 rect:", page.rect)
blocks = page.get_text("blocks")
for b in blocks:
    text = b[4].strip()
    if any(k in text for k in ["4.", "Problems", "beam"]):
        print(f"BBox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f})")
        print("Text:", text[:140])
        print("-" * 40)
