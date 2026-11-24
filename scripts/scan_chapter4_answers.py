import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
print("Searching answers for Chapter 4...")

for p_idx in range(790, 805):
    text = doc[p_idx].get_text()
    if "CHAPTER 4" in text.upper() or "CHAPTER 4" in text:
        print(f"=== Page {p_idx + 1} (0-indexed {p_idx}) ===")
        for line in text.splitlines():
            if any(k in line for k in ["4.", "CHAPTER", "d", "f", "phi"]):
                print("   ", line.strip())
