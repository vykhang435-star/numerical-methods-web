import fitz

doc231_ans = fitz.open("D:/pps/de_ktra/Dap an HK231-Phuong phap so-23101.pdf")
print("=== Đáp án Câu 3 HK231 (All pages) ===")
for p in range(len(doc231_ans)):
    text = doc231_ans[p].get_text()
    if any(k in text for k in ["Câu hỏi 3", "Câu 3", "3.a", "3.b", "3.c"]):
        print(f"--- Page {p+1} ---")
        print(text)
