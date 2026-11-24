import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")
for p in range(390, 420):
    text = doc[p].get_text()
    if "EXERCISE SET 6.3" in text.upper():
        print(f"Set 6.3 on PDF page {p+1} (idx {p})")
        for line in text.splitlines()[:20]:
            print("  ", line)
