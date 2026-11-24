# AGENTS.md - Numerical Methods Web Platform

## 1. Token & File Access Rules
- NEVER open or read raw PDF files inside `raw_sources/` directly as text. Always use Python scripts (`PyMuPDF` / `fitz`) in `scripts/` to inspect TOC, extract specific page ranges to `.txt`, or crop figures.
- Only read the specific JSON file in `data/` relevant to the current prompt.

## 2. Numerical Accuracy & Verification Rule (CRITICAL)
- Never compute floating-point iterations, matrix decompositions, or numerical integrals manually in text.
- Before writing any solution to `data/*.json`, you MUST write and run a temporary Python verification script (`scripts/verify_temp.py`) using `numpy`/`scipy` or standard Python math to compute exact values at each iteration, approximate relative error ($\varepsilon_a$), and true error ($\varepsilon_t$).
- Keep 5–6 significant digits during intermediate steps and round final answers according to the problem statement (default: 4 decimal places).

## 3. JSON & KaTeX Formatting Rules
- All math expressions must use KaTeX syntax: `$ ... $` for inline and `$$ ... $$` for display math.
- Double-escape all LaTeX backslashes inside JSON strings (e.g., `\\frac`, `\\theta`, `\\times`, `\\beta`) so `JSON.parse()` never breaks on `\t` or `\f`.
- Format multi-iteration calculations as clean Markdown tables inside the `steps` array.
