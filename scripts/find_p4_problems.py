import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
# Find text of Problem 4.6, 4.7, 4.8, 4.9 around page 220-230
for p_idx in range(215, 235):
    text = doc[p_idx].get_text()
    if any(k in text for k in ["Figure P4–6", "Figure P4–8", "4.8", "4.6"]):
        print(f"=== Page {p_idx + 1} (0-indexed {p_idx}) ===")
        for line in text.splitlines():
            if any(k in line for k in ["4.6", "4.7", "4.8", "4.9", "Figure P4", "Problems"]):
                print("   ", line.strip())
