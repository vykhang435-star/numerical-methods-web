import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")

# Exercise Set 1.2: Book pages 28-32 -> PDF pages 46-50 (idx 45-49)
print("=== Exercise Set 1.2 text ===")
for p in range(45, 50):
    text = doc[p].get_text()
    if "EXERCISE SET 1.2" in text.upper():
        print(f"--- PDF Page {p+1} (Book page {p+1-18}) ---")
        print(text[:1200])

# Exercise Set 3.1: Book pages 114-117 -> PDF pages 132-135 (idx 131-134)
print("\n=== Exercise Set 3.1 text ===")
for p in range(131, 136):
    text = doc[p].get_text()
    if "EXERCISE SET 3.1" in text.upper():
        print(f"--- PDF Page {p+1} (Book page {p+1-18}) ---")
        print(text[:1200])
