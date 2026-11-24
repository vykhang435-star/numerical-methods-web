import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
for p_idx in range(222, 235):
    text = doc[p_idx].get_text()
    if "spring" in text.lower():
        print(f"=== Page {p_idx + 1} ===")
        for line in text.splitlines():
            if "spring" in line.lower() or "Figure" in line:
                print("   ", line.strip())
