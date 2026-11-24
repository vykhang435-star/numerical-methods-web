import fitz

doc = fitz.open("D:/pps/de_ktra/Dap an HK231-Phuong phap so-23101.pdf")
print("Total pages:", len(doc))
for p in range(len(doc)):
    print(f"=== Page {p+1} ===")
    print(doc[p].get_text()[:400])
