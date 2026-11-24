import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")

for p in range(40, 52):
    text = doc[p].get_text()
    for line in text.splitlines():
        if any(k in line.lower() for k in ["exercise", "set 1.2", "round-off", "arithmetic"]):
            print(f"PDF page {p+1}: {line}")
