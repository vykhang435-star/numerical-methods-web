import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")

for idx in range(800, len(doc)):
    text = doc[idx].get_text()
    if "Exercise Set 1.2" in text or "Answers" in text or "EXERCISE SET 1.2" in text:
        print(f"PDF page {idx + 1} (idx {idx}) has: {repr(text[:100])}")
