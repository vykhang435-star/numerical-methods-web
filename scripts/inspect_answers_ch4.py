import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
for p_idx in [797, 798, 799, 800]:
    print(f"\n================ Page {p_idx + 1} (PDF index {p_idx}) ================")
    text = doc[p_idx].get_text()
    for line in text.splitlines():
        if line.strip().startswith("4.") or any(f"4.{n}" in line for n in [9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 26, 27, 37, 38, 39]):
            print(">>>", line.strip())
        elif any(k in line for k in ["d2y", "d1y", "d3y", "phi", "f1y", "f2y", "Answers"]):
            print("   ", line.strip())
