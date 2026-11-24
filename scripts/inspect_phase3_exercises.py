import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")

def print_snippet(p_idx, label):
    text = doc[p_idx].get_text()
    print(f"\n=== {label} (PDF page {p_idx+1}) ===")
    print(text[:1400])

# 4.1: Book p. 182 -> PDF p. 200
print_snippet(199, "Set 4.1 p. 200")
print_snippet(200, "Set 4.1 p. 201")
# 4.3: Book p. 200 -> PDF p. 218
print_snippet(217, "Set 4.3 p. 218")
# 4.4: Book p. 210 -> PDF p. 228
print_snippet(227, "Set 4.4 p. 228")
# 5.2: Book p. 273 -> PDF p. 291
print_snippet(290, "Set 5.2 p. 291")
# 5.4: Book p. 289 -> PDF p. 307
print_snippet(306, "Set 5.4 p. 307")
