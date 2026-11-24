"""Extract and solve Burden & Faires 9th Ed Linear Algebra problems (Chapter 3 of Web App)."""

import json
import re
from pathlib import Path
import numpy as np
import fitz

DATA_FILE = Path("data/ch03_linear_systems.json")

def m(v, d=4):
    if v is None:
        return r"\text{N/A}"
    if isinstance(v, (int, np.integer)):
        return str(v)
    if isinstance(v, (float, np.floating)):
        if abs(v) < 1e-12:
            return "0"
        if abs(v) >= 1000 or (abs(v) < 0.001 and abs(v) > 0):
            return f"{v:.4e}"
        return f"{v:.{d}f}".rstrip("0").rstrip(".")
    return str(v)

def matrix_to_katex(arr, d=4):
    arr = np.asarray(arr)
    if arr.ndim == 1:
        inner = r" \\ ".join(m(x, d) for x in arr)
        return rf"\begin{{Bmatrix}} {inner} \end{{Bmatrix}}"
    rows = []
    for r in arr:
        rows.append(" & ".join(m(x, d) for x in r))
    inner = r" \\ ".join(rows)
    return rf"\begin{{bmatrix}} {inner} \end{{bmatrix}}"

def card(prob_id, source_name, method_tag, exam_focus, statement, hint, formula, steps_detail, conclusion, final_answer, target_value):
    return {
        "id": prob_id,
        "source_problem": source_name,
        "method_tag": method_tag,
        "exam_focus": exam_focus,
        "problem_en": statement,
        "glossary": {
            "Gaussian elimination": "phương pháp khử Gauss",
            "backward substitution": "phép thế ngược",
            "matrix inversion": "tìm ma trận nghịch đảo",
            "determinant": "định thức của ma trận",
            "Cholesky factorization": "phân tích Cholesky LL^T",
            "eigenvalue": "giá trị riêng",
            "eigenvector": "vector riêng",
            "Power method": "phương pháp lũy thừa tìm trị riêng trội"
        },
        "hint": hint,
        "steps": [
            f"**Bước 1: Thiết lập công thức và ma trận ban đầu**\n{formula}",
            f"**Bước 2: Quá trình biến đổi số học (Kiểm chứng từ Python)**\n{steps_detail}",
            f"**Bước 3: Kết luận nghiệm và đối chiếu đáp án**\n{conclusion}"
        ],
        "final_answer": final_answer,
        "expected_numeric_value": float(target_value) if target_value is not None else 0.0
    }

def solve_gauss_6_1():
    # Problems 5a, 5b, 6a, 6b
    cards = []
    # 5a:
    A = np.array([[1.0, -1.0, 3.0], [3.0, -3.0, 1.0], [1.0, 1.0, 0.0]])
    b = np.array([2.0, -1.0, 3.0])
    # Elimination:
    # m21 = 3 -> R2 = R2 - 3R1 -> [0, 0, -8, -7]
    # m31 = 1 -> R3 = R3 - R1 -> [0, 2, -3, 1]
    # Pivot at a22 is 0 -> Row interchange R2 <-> R3 necessary!
    sol = np.linalg.solve(A, b)
    c5a = card(
        "ch03-burden-sec6.1-p5a",
        "Exercise 6.1 - Problem 5(a) (Burden & Faires 9th)",
        "Gaussian Elimination",
        True,
        "Use the Gaussian Elimination Algorithm to solve the following linear system, and determine whether row interchanges are necessary:\n$$\\begin{aligned} x_1 - x_2 + 3x_3 &= 2 \\\\ 3x_1 - 3x_2 + x_3 &= -1 \\\\ x_1 + x_2 &= 3 \\end{aligned}$$",
        "Lập ma trận bổ sung $[A|b]$. Thực hiện khử Gauss theo từng cột. Nếu phần tử chốt $a_{kk} = 0$, bắt buộc phải đổi hàng.",
        "Hệ phương trình tuyến tính ban đầu: $[A|b] = \\begin{bmatrix} 1 & -1 & 3 & 2 \\\\ 3 & -3 & 1 & -1 \\\\ 1 & 1 & 0 & 3 \\end{bmatrix}$",
        "- Khử cột 1: $m_{21} = 3, m_{31} = 1$.\n  + $R_2 \\leftarrow R_2 - 3R_1 = [0, 0, -8 | -7]$\n  + $R_3 \\leftarrow R_3 - R_1 = [0, 2, -3 | 1]$\n- Tại bước 2, phần tử chốt $a_{22} = 0$. Bắt buộc **hoán vị hàng $R_2 \\leftrightarrow R_3$**.\n- Ma trận tam giác trên thu được:\n  $$\\begin{bmatrix} 1 & -1 & 3 & 2 \\\\ 0 & 2 & -3 & 1 \\\\ 0 & 0 & -8 & -7 \\end{bmatrix}$$\n- Phép thế ngược:\n  + $x_3 = \\frac{-7}{-8} = 0.8750 = \\frac{7}{8}$\n  + $x_2 = \\frac{1 + 3(0.8750)}{2} = 1.8125 = \\frac{29}{16}$\n  + $x_1 = 2 + x_2 - 3x_3 = 2 + 1.8125 - 2.6250 = 1.1875 = \\frac{19}{16}$",
        f"Nghiệm giải tích: $x_1 = \\frac{{19}}{{16}} = 1.1875$, $x_2 = \\frac{{29}}{{16}} = 1.8125$, $x_3 = \\frac{{7}}{{8}} = 0.8750$. Bắt buộc hoán vị hàng $R_2 \\leftrightarrow R_3$.",
        "x_1 = 1.1875, \\; x_2 = 1.8125, \\; x_3 = 0.8750",
        sol[0]
    )
    cards.append(c5a)

    # 5b:
    A5b = np.array([[2.0, -1.5, 3.0], [-1.0, 0.0, 2.0], [4.0, -4.5, 5.0]])
    b5b = np.array([1.0, 3.0, 1.0])
    sol5b = np.linalg.solve(A5b, b5b)
    c5b = card(
        "ch03-burden-sec6.1-p5b",
        "Exercise 6.1 - Problem 5(b) (Burden & Faires 9th)",
        "Gaussian Elimination",
        True,
        "Use the Gaussian Elimination Algorithm to solve the following linear system, and determine whether row interchanges are necessary:\n$$\\begin{aligned} 2x_1 - 1.5x_2 + 3x_3 &= 1 \\\\ -x_1 + 2x_3 &= 3 \\\\ 4x_1 - 4.5x_2 + 5x_3 &= 1 \\end{aligned}$$",
        "Khử Gauss theo thứ tự. Kiểm tra các phần tử chốt trên đường chéo chính.",
        "Ma trận bổ sung $[A|b] = \\begin{bmatrix} 2 & -1.5 & 3 & 1 \\\\ -1 & 0 & 2 & 3 \\\\ 4 & -4.5 & 5 & 1 \\end{bmatrix}$",
        "- Khử cột 1: $m_{21} = -0.5, m_{31} = 2.0$.\n  + $R_2 \\leftarrow R_2 - (-0.5)R_1 = [0, -0.75, 3.5 | 3.5]$\n  + $R_3 \\leftarrow R_3 - 2R_1 = [0, -1.5, -1 | -1]$\n- Khử cột 2: chốt $a_{22} = -0.75 \\neq 0$ (không cần đổi hàng), $m_{32} = \\frac{-1.5}{-0.75} = 2.0$.\n  + $R_3 \\leftarrow R_3 - 2R_2 = [0, 0, -8 | -8]$\n- Phép thế ngược:\n  + $x_3 = \\frac{-8}{-8} = 1.0000$\n  + $x_2 = \\frac{3.5 - 3.5(1)}{-0.75} = 0.0000$\n  + $x_1 = \\frac{1 + 1.5(0) - 3(1)}{2} = -1.0000$",
        "Không cần hoán vị hàng. Nghiệm nguyên đẹp: $x_1 = -1$, $x_2 = 0$, $x_3 = 1$.",
        "x_1 = -1.0000, \\; x_2 = 0.0000, \\; x_3 = 1.0000",
        sol5b[0]
    )
    cards.append(c5b)

    # 6a:
    A6a = np.array([[0.0, 1.0, -2.0], [1.0, -1.0, 1.0], [1.0, 0.0, -1.0]])
    b6a = np.array([4.0, 6.0, 2.0])
    # Matrix A6a is singular because system is inconsistent / no solution
    c6a = card(
        "ch03-burden-sec6.1-p6a",
        "Exercise 6.1 - Problem 6(a) (Burden & Faires 9th)",
        "Gaussian Elimination",
        True,
        "Use Gaussian elimination to solve the system:\n$$\\begin{aligned} x_2 - 2x_3 &= 4 \\\\ x_1 - x_2 + x_3 &= 6 \\\\ x_1 - x_3 &= 2 \\end{aligned}$$",
        "Phần tử chốt đầu tiên $a_{11} = 0$, phải hoán vị hàng 1 với hàng 2 ngay bước đầu tiên.",
        "Ma trận bổ sung $[A|b] = \\begin{bmatrix} 0 & 1 & -2 & 4 \\\\ 1 & -1 & 1 & 6 \\\\ 1 & 0 & -1 & 2 \\end{bmatrix}$",
        "- $a_{11} = 0 \\implies$ Hoán vị $R_1 \\leftrightarrow R_2$:\n  $$\\begin{bmatrix} 1 & -1 & 1 & 6 \\\\ 0 & 1 & -2 & 4 \\\\ 1 & 0 & -1 & 2 \\end{bmatrix}$$\n- Khử cột 1: $R_3 \\leftarrow R_3 - R_1 = [0, 1, -2 | -4]$\n- Khử cột 2: $R_3 \\leftarrow R_3 - R_2 = [0, 0, 0 | -8]$\n- Phương trình cuối cùng cho kết quả $0x_3 = -8$ (mâu thuẫn vô lý).",
        "Hệ phương trình vô nghiệm (inconsistent / no solution).",
        "\\text{Vô nghiệm (No solution)}",
        0.0
    )
    cards.append(c6a)

    return cards

def solve_inversion_6_3():
    cards = []
    # Problem 1: matrix inverse
    A1 = np.array([[1.0, 2.0], [3.0, 4.0]])
    inv1 = np.linalg.inv(A1)
    c1 = card(
        "ch03-burden-sec6.3-p1",
        "Exercise 6.3 - Problem 1 (Burden & Faires 9th)",
        "Matrix Inversion",
        True,
        "Find the inverse of the matrix $A = \\begin{bmatrix} 1 & 2 \\\\ 3 & 4 \\end{bmatrix}$ using Gaussian elimination on $[A | I]$.",
        "Ghép ma trận đơn vị $I_2$ vào bên phải: $[A | I_2]$. Biến đổi Gauss-Jordan đưa vế trái về ma trận đơn vị, vế phải sẽ là $A^{-1}$.",
        f"Ma trận ban đầu: $[A | I] = \\begin{{bmatrix}} 1 & 2 & 1 & 0 \\\\ 3 & 4 & 0 & 1 \\end{{bmatrix}}$",
        f"- $R_2 \\leftarrow R_2 - 3R_1 = [0, -2, -3, 1]$\n- $R_2 \\leftarrow -\\frac{{1}}{{2}}R_2 = [0, 1, 1.5, -0.5]$\n- $R_1 \\leftarrow R_1 - 2R_2 = [1, 0, -2, 1]$\n- Thu được $A^{{-1}} = {matrix_to_katex(inv1)}$",
        "Ma trận nghịch đảo tồn tại vì $\\det(A) = 1(4) - 2(3) = -2 \\neq 0$.",
        f"A^{{-1}} = \\begin{{bmatrix}} -2 & 1 \\\\ 1.5 & -0.5 \\end{{bmatrix}}",
        inv1[0, 0]
    )
    cards.append(c1)

    # Problem 3: 3x3 matrix inverse
    A3 = np.array([[1.0, 2.0, -1.0], [2.0, 1.0, 0.0], [-1.0, 1.0, 2.0]])
    inv3 = np.linalg.inv(A3)
    c3 = card(
        "ch03-burden-sec6.3-p3",
        "Exercise 6.3 - Problem 3 (Burden & Faires 9th)",
        "Matrix Inversion",
        True,
        f"Find the inverse of the matrix $A = {matrix_to_katex(A3)}$ if it exists.",
        "Thiết lập ma trận mở rộng $[A | I_3]$. Dùng phép khử Gauss-Jordan để đưa nửa trái về $I_3$.",
        f"Ma trận mở rộng $[A | I_3]$ kích thước $3 \\times 6$.",
        f"Khử thuận và khử nghịch trên 3 hàng:\n- Nghịch đảo thu được: $$A^{{-1}} = {matrix_to_katex(inv3)}$$",
        f"Định thức $\\det(A) = -9 \\neq 0 \\implies$ ma trận khả nghịch.",
        f"A^{{-1}} = {matrix_to_katex(inv3)}",
        inv3[0, 0]
    )
    cards.append(c3)
    return cards

def solve_determinants_6_4():
    cards = []
    # Problem 1 & 2
    A1 = np.array([[2.0, 0.0, 1.0], [1.0, 2.0, 1.0], [0.0, 3.0, 1.0]])
    det1 = np.linalg.det(A1)
    c1 = card(
        "ch03-burden-sec6.4-p1",
        "Exercise 6.4 - Problem 1 (Burden & Faires 9th)",
        "Determinant",
        True,
        f"Find the determinant of the matrix $A = {matrix_to_katex(A1)}$ using row operations to reduce it to triangular form.",
        "Dùng các phép biến đổi sơ cấp theo hàng để đưa ma trận về dạng tam giác trên $U$. Khi đó $\\det(A) = (-1)^k \\prod u_{ii}$ với $k$ là số lần đổi hàng.",
        f"Ma trận cấp 3: $A = {matrix_to_katex(A1)}$",
        "- Biến đổi $R_2 \\leftarrow R_2 - 0.5R_1 = [0, 2, 0.5]$\n- Biến đổi $R_3 \\leftarrow R_3 - 1.5R_2 = [0, 0, 1 - 1.5(0.5)] = [0, 0, 0.25]$\n- Ma trận tam giác trên:\n  $$U = \\begin{bmatrix} 2 & 0 & 1 \\\\ 0 & 2 & 0.5 \\\\ 0 & 0 & 0.25 \\end{bmatrix}$$\n- Định thức: $\\det(A) = 2 \\times 2 \\times 0.25 = 1.0000$",
        "Định thức tính bằng tích các phần tử đường chéo của ma trận tam giác trên: $\\det(A) = 1$.",
        "\\det(A) = 1.0000",
        det1
    )
    cards.append(c1)
    return cards

def solve_cholesky_6_6():
    cards = []
    # Cholesky: A = L L^T for symmetric positive definite matrix
    # Problem 7:
    A7 = np.array([[2.0, -1.0, 0.0], [-1.0, 2.0, -1.0], [0.0, -1.0, 2.0]])
    L7 = np.linalg.cholesky(A7)
    c7 = card(
        "ch03-burden-sec6.6-p7",
        "Exercise 6.6 - Problem 7 (Burden & Faires 9th)",
        "Cholesky Factorization",
        True,
        f"Find the Cholesky factorization $A = LL^t$ for the symmetric positive definite tridiagonal matrix:\n$$A = {matrix_to_katex(A7)}$$",
        "Công thức Cholesky: $l_{11} = \\sqrt{a_{11}}$, $l_{j1} = a_{j1}/l_{11}$. Với $i > 1$: $l_{ii} = \\sqrt{a_{ii} - \\sum_{k=1}^{i-1} l_{ik}^2}$, $l_{ji} = \\frac{1}{l_{ii}}\\left(a_{ji} - \\sum_{k=1}^{i-1} l_{ik} l_{jk}\\right)$.",
        f"Ma trận đối xứng xác định dương $A = {matrix_to_katex(A7)}$",
        f"- Cột 1:\n  + $l_{{11}} = \\sqrt{{2}} \\approx 1.4142$\n  + $l_{{21}} = -1/\\sqrt{{2}} \\approx -0.7071$\n  + $l_{{31}} = 0$\n- Cột 2:\n  + $l_{{22}} = \\sqrt{{2 - (-1/\\sqrt{{2}})^2}} = \\sqrt{{2 - 0.5}} = \\sqrt{{1.5}} \\approx 1.2247$\n  + $l_{{32}} = (-1 - 0)/\\sqrt{{1.5}} = -\\sqrt{{2/3}} \\approx -0.8165$\n- Cột 3:\n  + $l_{{33}} = \\sqrt{{2 - (-0.8165)^2}} = \\sqrt{{2 - 2/3}} = \\sqrt{{4/3}} = \\frac{{2}}{{\\sqrt{{3}}}} \\approx 1.1547$\n- Ma trận tam giác dưới $L$:\n  $$L = {matrix_to_katex(L7)}$$",
        f"Kiểm chứng lại: $L L^t = A$. Các phần tử đường chéo $l_{{ii}} > 0$.",
        f"L = {matrix_to_katex(L7)}",
        L7[0, 0]
    )
    cards.append(c7)

    # Problem 9:
    A9 = np.array([[4.0, 1.0, 1.0, 1.0], [1.0, 3.0, -1.0, 1.0], [1.0, -1.0, 2.0, 0.0], [1.0, 1.0, 0.0, 2.0]])
    L9 = np.linalg.cholesky(A9)
    c9 = card(
        "ch03-burden-sec6.6-p9",
        "Exercise 6.6 - Problem 9 (Burden & Faires 9th)",
        "Cholesky Factorization",
        True,
        f"Find the Cholesky factorization $A = LL^t$ for the $4 \\times 4$ matrix:\n$$A = {matrix_to_katex(A9)}$$",
        "Áp dụng thuật toán Cholesky cấp 4 từng cột từ trái sang phải.",
        f"Ma trận $A$ cấp 4 đối xứng.",
        f"Quá trình phân tích Cholesky tính được ma trận tam giác dưới $L$:\n$$L = {matrix_to_katex(L9)}$$",
        f"Kiểm tra tính xác định dương: các phần tử đường chéo của $L$ đều thực và dương: $l_{{11}}=2, l_{{22}}=\\sqrt{{11/4}}\\dots$",
        f"l_{{11}} = 2.0000, \\; l_{{22}} \\approx {m(L9[1,1])}, \\; l_{{33}} \\approx {m(L9[2,2])}",
        L9[0, 0]
    )
    cards.append(c9)
    return cards

def solve_eigenvalues_7_2():
    cards = []
    # Problem 1: Eigenvalues and eigenvectors
    A1 = np.array([[2.0, -1.0], [-1.0, 2.0]])
    w, v = np.linalg.eig(A1)
    c1 = card(
        "ch03-burden-sec7.2-p1",
        "Exercise 7.2 - Problem 1 (Burden & Faires 9th)",
        "Eigenvalues and Eigenvectors",
        True,
        f"Find the eigenvalues and associated eigenvectors of the matrix $A = {matrix_to_katex(A1)}$.",
        "Giải phương trình đặc trưng $\\det(A - \\lambda I) = 0$ để tìm các giá trị riêng $\\lambda$. Với mỗi $\\lambda$, giải hệ thuần nhất $(A - \\lambda I)v = 0$ để tìm vector riêng tương ứng.",
        f"Phương trình đặc trưng:\n$$\\det(A - \\lambda I) = \\begin{{vmatrix}} 2 - \\lambda & -1 \\\\ -1 & 2 - \\lambda \\end{{vmatrix}} = (2-\\lambda)^2 - 1 = \\lambda^2 - 4\\lambda + 3 = 0$$",
        "- Nghiệm phương trình đặc trưng: $\\lambda_1 = 3, \\lambda_2 = 1$.\n- Vector riêng tương ứng với $\\lambda_1 = 3$:\n  $$(A - 3I)v = \\begin{bmatrix} -1 & -1 \\\\ -1 & -1 \\end{bmatrix} \\begin{Bmatrix} v_1 \\\\ v_2 \\end{Bmatrix} = 0 \\implies v^{(1)} = \\begin{Bmatrix} 1 \\\\ -1 \\end{Bmatrix}$$\n- Vector riêng tương ứng với $\\lambda_2 = 1$:\n  $$(A - I)v = \\begin{bmatrix} 1 & -1 \\\\ -1 & 1 \\end{bmatrix} \\begin{Bmatrix} v_1 \\\\ v_2 \\end{Bmatrix} = 0 \\implies v^{(2)} = \\begin{Bmatrix} 1 \\\\ 1 \\end{Bmatrix}$$",
        "Hai giá trị riêng thực: $\\lambda_1 = 3$ (vector riêng $[1, -1]^T$) và $\\lambda_2 = 1$ (vector riêng $[1, 1]^T$). Bán kính phổ $\\rho(A) = 3$.",
        "\\lambda_1 = 3.0000, \\; \\lambda_2 = 1.0000",
        3.0
    )
    cards.append(c1)
    return cards

def solve_power_method_9_3():
    cards = []
    # Problem 1a: Power method
    A = np.array([[2.0, 1.0, 1.0], [1.0, 2.0, 1.0], [1.0, 1.0, 2.0]])
    x = np.array([1.0, -1.0, 2.0])
    
    # Run 3 iterations
    table_rows = []
    y = x.copy()
    mu = 0
    for it in range(1, 4):
        y_next = A @ y
        # find max component
        p = np.argmax(np.abs(y_next))
        mu = y_next[p]
        y = y_next / mu
        table_rows.append(f"| {it} | {matrix_to_katex(y_next)} | {mu:.4f} | {matrix_to_katex(y)} |")

    table_md = "| Bước $k$ | $y^{(k)} = A x^{(k-1)}$ | $\\mu^{(k)}$ (Trị riêng xấp xỉ) | $x^{(k)} = y^{(k)} / \\mu^{(k)}$ |\n| :---: | :---: | :---: | :---: |\n" + "\n".join(table_rows)

    c1a = card(
        "ch03-burden-sec9.3-p1a",
        "Exercise 9.3 - Problem 1(a) (Burden & Faires 9th)",
        "The Power Method",
        True,
        f"Find the first three iterations obtained by the Power method applied to the matrix\n$$A = {matrix_to_katex(A)}$$\nusing the initial vector $x^{{(0)}} = (1, -1, 2)^t$.",
        "Tại mỗi bước lặp: tính $y^{(k)} = A x^{(k-1)}$, chọn $\\mu^{(k)} = y^{(k)}_{p_k}$ có độ lớn cực đại (chuẩn $L_\\infty$), và chuẩn hóa vector $x^{(k)} = y^{(k)} / \\mu^{(k)}$.",
        f"Ma trận $A = {matrix_to_katex(A)}$, vector xuất phát $x^{{(0)}} = [1, -1, 2]^T$",
        table_md,
        f"Sau 3 bước lặp, giá trị riêng trội xấp xỉ là $\\mu^{{(3)}} = {mu:.4f}$. Giá trị riêng chính xác của $A$ là $\\lambda_1 = 4.0000$. Phương pháp lũy thừa hội tụ nhanh về trị riêng trội.",
        f"\\mu^{{(3)}} \\approx {mu:.4f}, \\; \\lambda_1 = 4.0000",
        mu
    )
    cards.append(c1a)
    return cards

def main():
    cards = []
    cards.extend(solve_gauss_6_1())
    cards.extend(solve_inversion_6_3())
    cards.extend(solve_determinants_6_4())
    cards.extend(solve_cholesky_6_6())
    cards.extend(solve_eigenvalues_7_2())
    cards.extend(solve_power_method_9_3())

    print(f"Generated {len(cards)} Linear Algebra cards from Burden 9th.")

    # Load existing ch03
    ch03 = json.loads(DATA_FILE.read_text(encoding="utf-8")) if DATA_FILE.exists() else []
    existing_ids = {x["id"] for x in ch03}
    added = 0
    for c in cards:
        if c["id"] not in existing_ids:
            ch03.append(c)
            existing_ids.add(c["id"])
            added += 1

    DATA_FILE.write_text(json.dumps(ch03, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {DATA_FILE}: added {added}, total {len(ch03)} problems.")

if __name__ == "__main__":
    main()
