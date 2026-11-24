import fitz

doc241 = fitz.open("D:/pps/de_ktra/De thi HK241.pdf")
print("=== Đáp án Câu 2 HK241 ===")
for p in range(2, len(doc241)):
    text = doc241[p].get_text()
    if "Câu 2" in text or "2.a" in text or "2.b" in text:
        print(f"--- Page {p+1} ---")
        print(text)

doc231_ans = fitz.open("D:/pps/de_ktra/Dap an HK231-Phuong phap so-23101.pdf")
print("=== Đáp án Câu 3 HK231 ===")
for p in range(len(doc231_ans)):
    text = doc231_ans[p].get_text()
    if "Câu 3" in text or "Câu hỏi 3" in text:
        print(f"--- Page {p+1} ---")
        print(text)
