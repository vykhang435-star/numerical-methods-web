import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")

target_nums = [9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 26, 27, 37, 38, 39]

for p_idx in range(223, 231):
    page = doc[p_idx]
    blocks = page.get_text("blocks")
    for b in blocks:
        text = b[4].strip()
        for num in target_nums:
            if f"Figure P4–{num}" in text or f"Figure P4-{num}" in text:
                print(f"Page {p_idx + 1} (idx {p_idx}): Fig P4-{num} caption at ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f})")
                print("   Caption text:", repr(text))
