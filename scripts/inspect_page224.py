import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
page = doc[223] # Page 224
print("Page 224 rect:", page.rect)
blocks = page.get_text("blocks")
for b in blocks:
    text = b[4].strip()
    if any(k in text for k in ["4.", "Figure", "Problems"]):
        print(f"BBox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f})")
        print("Text:", text[:120])
        print("-" * 40)
