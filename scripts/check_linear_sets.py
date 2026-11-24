import fitz

doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")

sections = [
    ("Set 6.1", 385, 389, ["1.", "2.", "5.", "6."]),
    ("Set 6.3", 409, 413, ["1.", "2.", "3.", "4."]),
    ("Set 6.4", 415, 417, ["1.", "2.", "3.", "4."]),
    ("Set 6.6", 441, 445, ["7.", "8.", "9.", "10."]),
    ("Set 7.2", 465, 467, ["1.", "2."]),
    ("Set 9.3", 606, 610, ["1.", "2."]),
]

for name, start_p, end_p, nums in sections:
    print(f"\n================ {name} (PDF pages {start_p+1}-{end_p+1}) ================")
    for p in range(start_p, end_p + 1):
        text = doc[p].get_text()
        for line in text.splitlines():
            line_s = line.strip()
            if any(line_s.startswith(n) for n in nums):
                print(f"p.{p+1}: {line_s[:80]}")
