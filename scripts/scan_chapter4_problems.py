import fitz

doc = fitz.open("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
print("Total pages:", len(doc))

# Let's search pages 220 to 245 for Figure P4- and Problem 4.
problem_nums = [9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 26, 27, 37, 38, 39]

fig_targets = [f"P4–{n}" for n in problem_nums] + [f"P4-{n}" for n in problem_nums]
prob_targets = [f"4.{n}" for n in problem_nums]

results = {}
for p_idx in range(220, 250):
    text = doc[p_idx].get_text()
    for f in fig_targets:
        if f in text:
            results.setdefault(f, []).append(p_idx + 1)
    for pr in prob_targets:
        if pr in text:
            results.setdefault(pr, []).append(p_idx + 1)

print("Found targets:")
for k, v in sorted(results.items()):
    print(f"  {k}: pages {v}")
