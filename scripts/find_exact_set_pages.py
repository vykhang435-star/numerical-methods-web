import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")

for p in range(len(doc)):
    text = doc[p].get_text()
    if "Exercise Set 1.2" in text:
        print(f"Exercise Set 1.2 on PDF page {p+1} (idx {p})")
    if "Exercise Set 3.1" in text:
        print(f"Exercise Set 3.1 on PDF page {p+1} (idx {p})")
    if "Exercise Set 6.1" in text:
        print(f"Exercise Set 6.1 on PDF page {p+1} (idx {p})")
    if "Exercise Set 4.1" in text:
        print(f"Exercise Set 4.1 on PDF page {p+1} (idx {p})")
    if "Exercise Set 5.2" in text:
        print(f"Exercise Set 5.2 on PDF page {p+1} (idx {p})")
