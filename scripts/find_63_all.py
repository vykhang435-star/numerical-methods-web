import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")
for p in range(len(doc)):
    text = doc[p].get_text()
    if "Linear Algebra and Matrix Inversion" in text:
        print(f"p.{p+1}: {repr(text[:80])}")
