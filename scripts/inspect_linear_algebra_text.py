import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")

def print_page_range(start, end, label):
    print(f"\n==================== {label} ====================")
    for p in range(start - 1, end):
        text = doc[p].get_text()
        print(f"--- PDF Page {p+1} (Book page {p+1-18}) ---")
        print(text[:1500])

# Set 6.1 (PDF p. 386-388)
print_page_range(386, 388, "Set 6.1")
# Set 6.3 (PDF p. 409-411)
print_page_range(409, 411, "Set 6.3")
# Set 6.4 (PDF p. 417-418)
print_page_range(417, 418, "Set 6.4")
# Set 6.6 (PDF p. 443-445)
print_page_range(443, 445, "Set 6.6")
# Set 7.2 (PDF p. 467-468)
print_page_range(467, 468, "Set 7.2")
# Set 9.3 (PDF p. 608-609)
print_page_range(608, 609, "Set 9.3")
