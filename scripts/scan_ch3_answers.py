import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
print("Scanning Appendix D for Chapter 3 answers...")

target_nums = [2, 3, 4, 5, 7, 8, 9, 10, 20, 22, 23, 27, 29, 30, 33, 49, 50, 51]

for p_idx in range(793, 798):
    text = doc[p_idx].get_text()
    for line in text.splitlines():
        line_s = line.strip()
        if any(line_s.startswith(f"3.{n}") for n in target_nums) or any(line_s.startswith(f"3.{n} ") for n in target_nums):
            print(f"Page {p_idx + 1} (idx {p_idx}): {line_s}")
