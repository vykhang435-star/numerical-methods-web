import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
print("Total pages:", len(doc))

for page_idx in range(120, 170):
    text = doc[page_idx].get_text()
    if "3.23" in text or "P3–23" in text or "P3-23" in text:
        print(f"--- Page {page_idx + 1} (0-indexed {page_idx}) ---")
        for line in text.splitlines():
            if any(k in line for k in ["3.23", "P3–23", "P3-23", "Figure", "Problems"]):
                print("   ", line.strip())
