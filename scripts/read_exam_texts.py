import fitz

doc241 = fitz.open("D:/pps/de_ktra/De thi HK241.pdf")
print("=== De thi HK241 ===")
for p in range(len(doc241)):
    print(f"--- Page {p+1} ---")
    print(doc241[p].get_text())

doc231 = fitz.open("D:/pps/de_ktra/De thi HK231-Phuong phap so-23101.pdf")
print("=== De thi HK231 ===")
for p in range(len(doc231)):
    print(f"--- Page {p+1} ---")
    print(doc231[p].get_text())
