import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
print("Scanning Logan Chapter 3...")

bar1d_nums = [2, 3, 4, 5, 7, 8, 9, 10]
truss2d_nums = [20, 22, 23, 27, 29, 30, "33", 49, 50, 51]

# Chapter 3 problems are usually between page 140 and 175
for p_idx in range(145, 175):
    text = doc[p_idx].get_text()
    found = []
    for n in bar1d_nums:
        if f"P3–{n}" in text or f"P3-{n}" in text or f"3.{n}" in text:
            found.append(f"1D-3.{n}")
    for n in truss2d_nums:
        if f"P3–{n}" in text or f"P3-{n}" in text or f"3.{n}" in text:
            found.append(f"2D-3.{n}")
    if found:
        print(f"Page {p_idx + 1} (idx {p_idx}): {', '.join(set(found))}")
