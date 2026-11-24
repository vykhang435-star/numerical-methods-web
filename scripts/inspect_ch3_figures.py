import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")

all_nums = [
    ("1D", [2, 3, 4, 5, 7, 8, 9, 10]),
    ("2D", [20, 22, 23, 27, 29, 30, 33, 49, 50, 51])
]

pages_to_check = [151, 152, 153, 156, 157, 158, 159, 160, 164, 165]

for p_idx in pages_to_check:
    page = doc[p_idx]
    blocks = page.get_text("blocks")
    print(f"\n================ Page {p_idx + 1} (PDF index {p_idx}) ================")
    for b in blocks:
        text = b[4].strip()
        for cat, nums in all_nums:
            for n in nums:
                if f"Figure P3–{n}" in text or f"Figure P3-{n}" in text or f"3.{n}" in text:
                    print(f"[{cat}] P3-{n} bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f})")
                    print("   ", repr(text[:90]))
