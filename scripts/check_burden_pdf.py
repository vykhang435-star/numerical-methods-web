import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")
print("Total pages in numerical_analysis_9th.pdf:", len(doc))

# Check PDF page 19 (idx 18)
page19_text = doc[18].get_text()
print("PDF page 19 snippet:", repr(page19_text[:150]))

# Search for "Answers to Selected Exercises"
for idx in range(len(doc)-100, len(doc)):
    text = doc[idx].get_text()
    if "Answers to Selected Exercises" in text:
        print(f"Answers start around PDF page {idx + 1} (idx {idx})")
        break
