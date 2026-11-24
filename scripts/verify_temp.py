"""
Numerical verification script for Chapter 2: Roots of Equations.
Solves 8 selected problems from Chapra & Canale using:
- Bisection
- False-Position (Regula Falsi)
- Simple Fixed-Point Iteration
- Newton-Raphson
- Secant Method

Calculates exact iteration values, f(x), approximate relative error (\\varepsilon_a%),
and true relative error (\\varepsilon_t%) where exact root is known.
Generates data/ch02_roots.json following the exact schema in AGENTS.md.
"""

import json
import math
from pathlib import Path

def bisection(f, xl, xu, max_iter=10, es=None, true_root=None):
    rows = []
    xr_prev = None
    for i in range(1, max_iter + 1):
        xr = (xl + xu) / 2.0
        ea = abs((xr - xr_prev) / xr) * 100.0 if xr_prev is not None else None
        et = abs((true_root - xr) / true_root) * 100.0 if true_root is not None else None
        f_xl = f(xl)
        f_xr = f(xr)
        rows.append({
            "iter": i,
            "xl": xl,
            "xu": xu,
            "xr": xr,
            "f_xl": f_xl,
            "f_xr": f_xr,
            "ea": ea,
            "et": et
        })
        xr_prev = xr
        if es is not None and ea is not None and ea < es:
            break
        if f_xl * f_xr < 0:
            xu = xr
        elif f_xl * f_xr > 0:
            xl = xr
        else:
            break
    return rows

def false_position(f, xl, xu, max_iter=10, es=None, true_root=None):
    rows = []
    xr_prev = None
    for i in range(1, max_iter + 1):
        f_xl = f(xl)
        f_xu = f(xu)
        xr = xu - (f_xu * (xl - xu)) / (f_xl - f_xu)
        ea = abs((xr - xr_prev) / xr) * 100.0 if xr_prev is not None else None
        et = abs((true_root - xr) / true_root) * 100.0 if true_root is not None else None
        f_xr = f(xr)
        rows.append({
            "iter": i,
            "xl": xl,
            "xu": xu,
            "xr": xr,
            "f_xl": f_xl,
            "f_xr": f_xr,
            "ea": ea,
            "et": et
        })
        xr_prev = xr
        if es is not None and ea is not None and ea < es:
            break
        if f_xl * f_xr < 0:
            xu = xr
        elif f_xl * f_xr > 0:
            xl = xr
        else:
            break
    return rows

def fixed_point(g, x0, max_iter=10, es=None, true_root=None):
    rows = []
    x = x0
    for i in range(1, max_iter + 1):
        x_next = g(x)
        ea = abs((x_next - x) / x_next) * 100.0 if x_next != 0 else 0
        et = abs((true_root - x_next) / true_root) * 100.0 if true_root is not None else None
        rows.append({
            "iter": i,
            "xi": x,
            "xi_next": x_next,
            "ea": ea,
            "et": et
        })
        x = x_next
        if es is not None and ea < es:
            break
    return rows

def newton_raphson(f, df, x0, max_iter=10, es=None, true_root=None):
    rows = []
    x = x0
    for i in range(1, max_iter + 1):
        f_x = f(x)
        df_x = df(x)
        x_next = x - f_x / df_x
        ea = abs((x_next - x) / x_next) * 100.0 if x_next != 0 else 0
        et = abs((true_root - x_next) / true_root) * 100.0 if true_root is not None else None
        rows.append({
            "iter": i,
            "xi": x,
            "f_xi": f_x,
            "df_xi": df_x,
            "xi_next": x_next,
            "ea": ea,
            "et": et
        })
        x = x_next
        if es is not None and ea < es:
            break
    return rows

def secant(f, x_minus1, x0, max_iter=10, es=None, true_root=None):
    rows = []
    xm1 = x_minus1
    x = x0
    for i in range(1, max_iter + 1):
        f_xm1 = f(xm1)
        f_x = f(x)
        x_next = x - (f_x * (xm1 - x)) / (f_xm1 - f_x)
        ea = abs((x_next - x) / x_next) * 100.0 if x_next != 0 else 0
        et = abs((true_root - x_next) / true_root) * 100.0 if true_root is not None else None
        rows.append({
            "iter": i,
            "xi_minus1": xm1,
            "xi": x,
            "f_xi_minus1": f_xm1,
            "f_xi": f_x,
            "xi_next": x_next,
            "ea": ea,
            "et": et
        })
        xm1 = x
        x = x_next
        if es is not None and ea < es:
            break
    return rows

def format_bisection_table(rows):
    header = "| $i$ | $x_l$ | $x_u$ | $x_r$ | $f(x_l)$ | $f(x_r)$ | $\\varepsilon_a$ (%) | $\\varepsilon_t$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    lines = [header]
    for r in rows:
        ea_str = f"{r['ea']:.4f}\\%" if r['ea'] is not None else "---"
        et_str = f"{r['et']:.4f}\\%" if r['et'] is not None else "---"
        lines.append(f"| {r['iter']} | {r['xl']:.4f} | {r['xu']:.4f} | {r['xr']:.4f} | {r['f_xl']:.4f} | {r['f_xr']:.4f} | {ea_str} | {et_str} |")
    return "\n".join(lines)

def format_false_pos_table(rows):
    header = "| $i$ | $x_l$ | $x_u$ | $x_r$ | $f(x_l)$ | $f(x_r)$ | $\\varepsilon_a$ (%) | $\\varepsilon_t$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    lines = [header]
    for r in rows:
        ea_str = f"{r['ea']:.4f}\\%" if r['ea'] is not None else "---"
        et_str = f"{r['et']:.4f}\\%" if r['et'] is not None else "---"
        lines.append(f"| {r['iter']} | {r['xl']:.4f} | {r['xu']:.4f} | {r['xr']:.4f} | {r['f_xl']:.4f} | {r['f_xr']:.4f} | {ea_str} | {et_str} |")
    return "\n".join(lines)

def format_fixed_point_table(rows):
    header = "| $i$ | $x_i$ | $x_{i+1} = g(x_i)$ | $\\varepsilon_a$ (%) | $\\varepsilon_t$ (%) |\n| :---: | :---: | :---: | :---: | :---: |"
    lines = [header]
    for r in rows:
        et_str = f"{r['et']:.4f}\\%" if r['et'] is not None else "---"
        lines.append(f"| {r['iter']} | {r['xi']:.6f} | {r['xi_next']:.6f} | {r['ea']:.4f}\\% | {et_str} |")
    return "\n".join(lines)

def format_newton_table(rows):
    header = "| $i$ | $x_i$ | $f(x_i)$ | $f'(x_i)$ | $x_{i+1}$ | $\\varepsilon_a$ (%) | $\\varepsilon_t$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    lines = [header]
    for r in rows:
        et_str = f"{r['et']:.4f}\\%" if r['et'] is not None else "---"
        lines.append(f"| {r['iter']} | {r['xi']:.6f} | {r['f_xi']:.6f} | {r['df_xi']:.6f} | {r['xi_next']:.6f} | {r['ea']:.4f}\\% | {et_str} |")
    return "\n".join(lines)

def format_secant_table(rows):
    header = "| $i$ | $x_{i-1}$ | $x_i$ | $f(x_{i-1})$ | $f(x_i)$ | $x_{i+1}$ | $\\varepsilon_a$ (%) | $\\varepsilon_t$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    lines = [header]
    for r in rows:
        et_str = f"{r['et']:.4f}\\%" if r['et'] is not None else "---"
        lines.append(f"| {r['iter']} | {r['xi_minus1']:.6f} | {r['xi']:.6f} | {r['f_xi_minus1']:.6f} | {r['f_xi']:.6f} | {r['xi_next']:.6f} | {r['ea']:.4f}\\% | {et_str} |")
    return "\n".join(lines)

def main():
    problems = []

    # 1. Problem 5.1 (Bisection)
    # f(x) = -0.6 x^2 + 2.4 x + 5.5
    f1 = lambda x: -0.6 * x**2 + 2.4 * x + 5.5
    # Analytical positive root: (-2.4 - sqrt(2.4^2 - 4*(-0.6)*5.5)) / (2 * -0.6) = (-2.4 - sqrt(5.76 + 13.2)) / -1.2 = (-2.4 - 4.354308) / -1.2 = 5.62859
    true1 = (-2.4 - math.sqrt(2.4**2 - 4 * (-0.6) * 5.5)) / (-1.2)
    rows1 = bisection(f1, 5.0, 10.0, max_iter=3, true_root=true1)
    table1 = format_bisection_table(rows1)
    problems.append({
        "id": "ch02-prob-5.1",
        "source_problem": "Problem 5.1 - Chapra & Canale",
        "method_tag": "Bisection",
        "exam_focus": True,
        "problem_en": "Determine the highest real root of $f(x) = -0.6x^2 + 2.4x + 5.5$ using three iterations of the bisection method with initial guesses of $x_l = 5$ and $x_u = 10$. Compute the approximate percent relative error $\\varepsilon_a$ and the true relative error $\\varepsilon_t$ after each iteration.",
        "glossary": {
            "highest real root": "nghiệm thực lớn nhất",
            "bisection method": "phương pháp chia đôi",
            "initial guesses": "các giá trị dự đoán ban đầu",
            "approximate percent relative error": "sai số xấp xỉ phần trăm tương đối",
            "true relative error": "sai số tương đối thực sự"
        },
        "hint": "Khoảng cách ly ban đầu $[5, 10]$. Nghiệm xấp xỉ tại mỗi bước: $x_r = \\frac{x_l + x_u}{2}$. Xét dấu tích $f(x_l) \\cdot f(x_r)$: nếu âm thì $x_u = x_r$, nếu dương thì $x_l = x_r$.",
        "steps": [
            "**Bước 1: Tóm tắt bài toán và công thức lặp**\n- Hàm số: $f(x) = -0.6x^2 + 2.4x + 5.5$\n- Nghiệm giải tích chính xác: $x^* = \\frac{-2.4 - \\sqrt{2.4^2 - 4(-0.6)(5.5)}}{-1.2} \\approx 5.6286$\n- Công thức nghiệm xấp xỉ: $x_r = \\frac{x_l + x_u}{2}$\n- Công thức sai số: $\\varepsilon_a = \\left|\\frac{x_r^{\\text{mới}} - x_r^{\\text{cũ}}}{x_r^{\\text{mới}}}\\right| \\times 100\\%, \\quad \\varepsilon_t = \\left|\\frac{x^* - x_r}{x^*}\\right| \\times 100\\%$",
            f"**Bước 2: Bảng tính toán chi tiết 3 vòng lặp**\n\n{table1}",
            "**Bước 3: Kết luận nghiệm và đánh giá sai số**\nSau 3 vòng lặp, nghiệm xấp xỉ thu được là $x_r = 5.6250$ với sai số xấp xỉ $\\varepsilon_a = 11.1111\\%$ và sai số thật $\\varepsilon_t = 0.0638\\%$. Phương pháp chia đôi đảm bảo hội tụ vững chắc với khoảng nghiệm thu hẹp một nửa sau mỗi bước."
        ],
        "final_answer": "x \\approx 5.6250 \\quad (\\varepsilon_a = 11.1111\\%, \\varepsilon_t = 0.0638\\%)"
    })

    # 2. Problem 5.2 (Bisection)
    # f(x) = 4x^3 - 6x^2 + 7x - 2.3, xl = 0, xu = 1, es = 10%
    f2 = lambda x: 4 * x**3 - 6 * x**2 + 7 * x - 2.3
    rows2 = bisection(f2, 0.0, 1.0, max_iter=10, es=10.0)
    table2 = format_bisection_table(rows2)
    problems.append({
        "id": "ch02-prob-5.2",
        "source_problem": "Problem 5.2 - Chapra & Canale",
        "method_tag": "Bisection",
        "exam_focus": False,
        "problem_en": "Determine the real root of $f(x) = 4x^3 - 6x^2 + 7x - 2.3$ using bisection to locate the root. Employ initial guesses of $x_l = 0$ and $x_u = 1$ and iterate until the estimated error $\\varepsilon_a$ falls below $\\varepsilon_s = 10\\%$.",
        "glossary": {
            "real root": "nghiệm thực",
            "bisection": "phương pháp chia đôi",
            "estimated error": "sai số ước lượng xấp xỉ",
            "stopping criterion": "tiêu chuẩn dừng lặp"
        },
        "hint": "Kiểm tra điều kiện ban đầu: $f(0) = -2.3 < 0$, $f(1) = 2.7 > 0 \\implies$ có nghiệm trong $(0, 1)$. Lặp đến khi $\\varepsilon_a < 10\\%$.",
        "steps": [
            "**Bước 1: Thiết lập công thức và điều kiện dừng**\n- Hàm số: $f(x) = 4x^3 - 6x^2 + 7x - 2.3$\n- Kiểm tra dấu ban đầu: $f(0) = -2.3, f(1) = 2.7 \\implies f(0)f(1) < 0$\n- Điều kiện dừng: $\\varepsilon_a = \\left|\\frac{x_r^{\\text{mới}} - x_r^{\\text{cũ}}}{x_r^{\\text{mới}}}\\right| \\times 100\\% < 10\\%$",
            f"**Bước 2: Bảng tính toán lặp theo từng bước**\n\n{table2}",
            f"**Bước 3: Kết luận nghiệm**\nTại vòng lặp thứ {len(rows2)}, nghiệm xấp xỉ đạt $x_r = {rows2[-1]['xr']:.4f}$ với $\\varepsilon_a = {rows2[-1]['ea']:.4f}\\% < 10\\%$. Đạt tiêu chuẩn dừng."
        ],
        "final_answer": f"x \\approx {rows2[-1]['xr']:.4f} \\quad (\\varepsilon_a = {rows2[-1]['ea']:.4f}\\% < 10\\%)"
    })

    # 3. Problem 5.3 (False-Position)
    # f(x) = -26 + 85x - 91x^2 + 44x^3 - 8x^4 + x^5, xl = 0.5, xu = 1.0, es = 0.2%
    f3 = lambda x: -26 + 85*x - 91*x**2 + 44*x**3 - 8*x**4 + x**5
    rows3 = false_position(f3, 0.5, 1.0, max_iter=10, es=0.2)
    table3 = format_false_pos_table(rows3)
    problems.append({
        "id": "ch02-prob-5.3",
        "source_problem": "Problem 5.3 - Chapra & Canale",
        "method_tag": "False-Position",
        "exam_focus": True,
        "problem_en": "Determine the real root of $f(x) = -26 + 85x - 91x^2 + 44x^3 - 8x^4 + x^5$ using the false-position method and a stopping criterion of $\\varepsilon_s = 0.2\\%$. Employ initial guesses of $x_l = 0.5$ and $x_u = 1.0$.",
        "glossary": {
            "false-position method": "phương pháp vị trí sai (dây cung)",
            "stopping criterion": "tiêu chuẩn dừng lặp",
            "bracket": "khoảng cách ly nghiệm"
        },
        "hint": "Công thức dây cung: $x_r = x_u - \\frac{f(x_u)(x_l - x_u)}{f(x_l) - f(x_u)}$. Cập nhật cận dựa theo dấu của $f(x_l) \\cdot f(x_r)$.",
        "steps": [
            "**Bước 1: Thiết lập phương trình và công thức lặp**\n- Hàm số bậc 5: $f(x) = -26 + 85x - 91x^2 + 44x^3 - 8x^4 + x^5$\n- Cận ban đầu: $f(0.5) = -1.4785 < 0, f(1.0) = 5.0000 > 0$\n- Công thức nội suy tuyến tính (vị trí sai): $x_r = x_u - \\frac{f(x_u)(x_l - x_u)}{f(x_l) - f(x_u)}$\n- Tiêu chuẩn dừng: $\\varepsilon_a < 0.2\\%$",
            f"**Bước 2: Bảng tính toán chi tiết từng vòng lặp**\n\n{table3}",
            f"**Bước 3: Kết luận nghiệm**\nQuá trình lặp dừng sau {len(rows3)} bước với nghiệm $x_r = {rows3[-1]['xr']:.4f}$ và sai số tương đối $\\varepsilon_a = {rows3[-1]['ea']:.4f}\\% < 0.2\\%$."
        ],
        "final_answer": f"x \\approx {rows3[-1]['xr']:.4f} \\quad (\\varepsilon_a = {rows3[-1]['ea']:.4f}\\% < 0.2\\%)"
    })

    # 4. Problem 5.6 (False-Position vs Bisection)
    # ln(x^4) = 0.7 => f(x) = 4*ln(x) - 0.7, xl = 0.5, xu = 2.0, 3 iterations
    f4 = lambda x: 4.0 * math.log(x) - 0.7
    true4 = math.exp(0.7 / 4.0) # ~ 1.191246
    rows4 = false_position(f4, 0.5, 2.0, max_iter=3, true_root=true4)
    table4 = format_false_pos_table(rows4)
    problems.append({
        "id": "ch02-prob-5.6",
        "source_problem": "Problem 5.6 - Chapra & Canale",
        "method_tag": "False-Position",
        "exam_focus": False,
        "problem_en": "Determine the positive real root of $\\ln(x^4) = 0.7$ using three iterations of the false-position method, with initial guesses of $x_l = 0.5$ and $x_u = 2.0$.",
        "glossary": {
            "positive real root": "nghiệm thực dương",
            "false-position method": "phương pháp vị trí sai",
            "logarithmic equation": "phương trình logarit"
        },
        "hint": "Viết lại thành $f(x) = 4\\ln(x) - 0.7 = 0$. Nghiệm giải tích chính xác: $x^* = e^{0.7/4} \\approx 1.1912$. Thực hiện 3 bước lặp với $x_l = 0.5, x_u = 2.0$.",
        "steps": [
            "**Bước 1: Tóm tắt bài toán**\n- Phương trình: $4\\ln(x) - 0.7 = 0 \\implies x^* = e^{0.175} \\approx 1.191246$\n- Cận ban đầu: $f(0.5) = 4\\ln(0.5) - 0.7 = -3.4726, f(2.0) = 4\\ln(2) - 0.7 = 2.0726$\n- Công thức: $x_r = x_u - \\frac{f(x_u)(x_l - x_u)}{f(x_l) - f(x_u)}$",
            f"**Bước 2: Bảng tính toán 3 vòng lặp**\n\n{table4}",
            f"**Bước 3: Đánh giá kết quả**\nSau 3 bước lặp, nghiệm xấp xỉ đạt $x_r = {rows4[-1]['xr']:.4f}$ với sai số xấp xỉ $\\varepsilon_a = {rows4[-1]['ea']:.4f}\\%$ và sai số thực $\\varepsilon_t = {rows4[-1]['et']:.4f}\\%$."
        ],
        "final_answer": f"x \\approx {rows4[-1]['xr']:.4f} \\quad (\\varepsilon_a = {rows4[-1]['ea']:.4f}\\%, \\varepsilon_t = {rows4[-1]['et']:.4f}\\%)"
    })

    # 5. Problem 6.1 (Fixed-Point Iteration)
    # f(x) = 2 sin(sqrt(x)) - x = 0 => g(x) = 2 sin(sqrt(x)), x0 = 0.5, es = 0.001%
    g5 = lambda x: 2.0 * math.sin(math.sqrt(x))
    rows5 = fixed_point(g5, 0.5, max_iter=15, es=0.001)
    table5 = format_fixed_point_table(rows5)
    problems.append({
        "id": "ch02-prob-6.1",
        "source_problem": "Problem 6.1 - Chapra & Canale",
        "method_tag": "Fixed-Point Iteration",
        "exam_focus": True,
        "problem_en": "Use simple fixed-point iteration to locate the root of $f(x) = 2\\sin(\\sqrt{x}) - x = 0$. Use an initial guess of $x_0 = 0.5$ and iterate until $\\varepsilon_a \\le 0.001\\%$.",
        "glossary": {
            "simple fixed-point iteration": "phương pháp lặp đơn giản (lặp điểm bất động)",
            "initial guess": "giá trị dự đoán ban đầu",
            "convergence": "sự hội tụ"
        },
        "hint": "Biến đổi về dạng $x_{i+1} = g(x_i) = 2\\sin(\\sqrt{x_i})$. Điều kiện hội tụ: $|g'(x)| < 1$ tại lân cận nghiệm.",
        "steps": [
            "**Bước 1: Thiết lập hàm lặp $g(x)$**\n- Phương trình: $x = 2\\sin(\\sqrt{x})$\n- Hàm lặp: $g(x) = 2\\sin(\\sqrt{x})$\n- Đạo hàm: $g'(x) = \\frac{\\cos(\\sqrt{x})}{\\sqrt{x}}$. Tại $x_0 = 0.5$, $|g'(0.5)| = |\\frac{\\cos(\\sqrt{0.5})}{\\sqrt{0.5}}| \\approx 1.07$, nhưng khi $x$ tăng về phía nghiệm $x \\approx 1.97$, $g'(1.97) \\approx \\frac{\\cos(1.405)}{1.405} \\approx 0.117 < 1$, đảm bảo quá trình hội tụ tuyến tính.",
            f"**Bước 2: Bảng tính toán lặp từng bước**\n\n{table5}",
            f"**Bước 3: Kết luận nghiệm**\nQuá trình lặp đạt tiêu chuẩn dừng $\\varepsilon_a \\le 0.001\\%$ tại vòng lặp thứ {len(rows5)} với nghiệm $x = {rows5[-1]['xi_next']:.6f}$."
        ],
        "final_answer": f"x \\approx {rows5[-1]['xi_next']:.6f} \\quad (\\varepsilon_a = {rows5[-1]['ea']:.6f}\\% \\le 0.001\\%)"
    })

    # 6. Problem 6.3 (Newton-Raphson)
    # f(x) = -x^2 + 1.8x + 2.5, x0 = 5, es = 0.05%
    # f'(x) = -2x + 1.8
    # Exact positive root: (-1.8 - sqrt(1.8^2 - 4*(-1)*2.5)) / -2 = (-1.8 - sqrt(3.24 + 10)) / -2 = (-1.8 - 3.63868) / -2 = 2.71934
    f6 = lambda x: -x**2 + 1.8 * x + 2.5
    df6 = lambda x: -2.0 * x + 1.8
    true6 = (-1.8 - math.sqrt(1.8**2 + 10.0)) / (-2.0)
    rows6 = newton_raphson(f6, df6, 5.0, max_iter=10, es=0.05, true_root=true6)
    table6 = format_newton_table(rows6)
    problems.append({
        "id": "ch02-prob-6.3",
        "source_problem": "Problem 6.3 - Chapra & Canale",
        "method_tag": "Newton-Raphson",
        "exam_focus": True,
        "problem_en": "Use the Newton-Raphson method to determine a root of $f(x) = -x^2 + 1.8x + 2.5$ using an initial guess of $x_0 = 5$. Perform the computation until $\\varepsilon_a$ is less than $\\varepsilon_s = 0.05\\%$.",
        "glossary": {
            "Newton-Raphson method": "phương pháp Newton-Raphson (tiếp tuyến)",
            "initial guess": "giá trị dự đoán ban đầu",
            "quadratic convergence": "hội tụ bậc hai"
        },
        "hint": "Công thức lặp tiếp tuyến: $x_{i+1} = x_i - \\frac{f(x_i)}{f'(x_i)}$. Với $f'(x) = -2x + 1.8$.",
        "steps": [
            "**Bước 1: Tính đạo hàm và thiết lập công thức lặp**\n- Hàm số: $f(x) = -x^2 + 1.8x + 2.5$\n- Đạo hàm cấp 1: $f'(x) = -2x + 1.8$\n- Công thức lặp: $x_{i+1} = x_i - \\frac{-x_i^2 + 1.8x_i + 2.5}{-2x_i + 1.8} = \\frac{-x_i^2 - 2.5}{-2x_i + 1.8} = \\frac{x_i^2 + 2.5}{2x_i - 1.8}$\n- Nghiệm giải tích: $x^* = \\frac{-1.8 - \\sqrt{1.8^2 - 4(-1)(2.5)}}{-2} \\approx 2.719341$\n- Điều kiện dừng: $\\varepsilon_a < 0.05\\%$",
            f"**Bước 2: Bảng tính toán chi tiết từng vòng lặp**\n\n{table6}",
            f"**Bước 3: Kết luận nghiệm và tốc độ hội tụ**\nPhương pháp Newton-Raphson đạt tiêu chuẩn dừng sau {len(rows6)} bước lặp, nghiệm xấp xỉ đạt $x = {rows6[-1]['xi_next']:.6f}$ với sai số xấp xỉ $\\varepsilon_a = {rows6[-1]['ea']:.4f}\\%$ và sai số thực $\\varepsilon_t = {rows6[-1]['et']:.4f}\\%$. Tốc độ hội tụ bậc hai giúp số chữ số tin cậy tăng gần gấp đôi sau mỗi vòng."
        ],
        "final_answer": f"x \\approx {rows6[-1]['xi_next']:.6f} \\quad (\\varepsilon_a = {rows6[-1]['ea']:.4f}\\% < 0.05\\%)"
    })

    # 7. Problem 6.2(c) (Newton-Raphson)
    # f(x) = 2x^3 - 11.7x^2 + 17.7x - 5, x0 = 3, 3 iterations
    # f'(x) = 6x^2 - 23.4x + 17.7
    f7 = lambda x: 2.0 * x**3 - 11.7 * x**2 + 17.7 * x - 5.0
    df7 = lambda x: 6.0 * x**2 - 23.4 * x + 17.7
    rows7 = newton_raphson(f7, df7, 3.0, max_iter=3)
    table7 = format_newton_table(rows7)
    problems.append({
        "id": "ch02-prob-6.2c",
        "source_problem": "Problem 6.2(c) - Chapra & Canale",
        "method_tag": "Newton-Raphson",
        "exam_focus": True,
        "problem_en": "Determine the highest real root of $f(x) = 2x^3 - 11.7x^2 + 17.7x - 5$ using three iterations of the Newton-Raphson method with an initial guess of $x_0 = 3$. Compute the approximate percent relative error after each iteration.",
        "glossary": {
            "highest real root": "nghiệm thực lớn nhất",
            "Newton-Raphson method": "phương pháp Newton-Raphson",
            "polynomial function": "hàm đa thức"
        },
        "hint": "Tính đạo hàm: $f'(x) = 6x^2 - 23.4x + 17.7$. Áp dụng $x_{i+1} = x_i - \\frac{f(x_i)}{f'(x_i)}$ trong 3 bước lặp.",
        "steps": [
            "**Bước 1: Thiết lập công thức lặp**\n- Hàm số: $f(x) = 2x^3 - 11.7x^2 + 17.7x - 5$\n- Đạo hàm: $f'(x) = 6x^2 - 23.4x + 17.7$\n- Giá trị ban đầu: $x_0 = 3$\n- Công thức: $x_{i+1} = x_i - \\frac{2x_i^3 - 11.7x_i^2 + 17.7x_i - 5}{6x_i^2 - 23.4x_i + 17.7}$",
            f"**Bước 2: Bảng tính toán 3 vòng lặp chi tiết**\n\n{table7}",
            f"**Bước 3: Kết luận nghiệm**\nSau 3 vòng lặp, nghiệm xấp xỉ đạt $x = {rows7[-1]['xi_next']:.6f}$ với sai số xấp xỉ $\\varepsilon_a = {rows7[-1]['ea']:.4f}\\%$."
        ],
        "final_answer": f"x \\approx {rows7[-1]['xi_next']:.6f} \\quad (\\varepsilon_a = {rows7[-1]['ea']:.4f}\\%)"
    })

    # 8. Problem 6.2(d) (Secant Method)
    # f(x) = 2x^3 - 11.7x^2 + 17.7x - 5, x_{-1} = 3, x_0 = 4, 3 iterations
    rows8 = secant(f7, 3.0, 4.0, max_iter=3)
    table8 = format_secant_table(rows8)
    problems.append({
        "id": "ch02-prob-6.2d",
        "source_problem": "Problem 6.2(d) - Chapra & Canale",
        "method_tag": "Secant",
        "exam_focus": True,
        "problem_en": "Determine the highest real root of $f(x) = 2x^3 - 11.7x^2 + 17.7x - 5$ using three iterations of the Secant method with initial guesses of $x_{-1} = 3$ and $x_0 = 4$. Compute the approximate percent relative error after each iteration.",
        "glossary": {
            "secant method": "phương pháp cát tuyến",
            "initial guesses": "các giá trị dự đoán ban đầu",
            "finite difference approximation": "xấp xỉ sai phân hữu hạn của đạo hàm"
        },
        "hint": "Công thức cát tuyến thay đạo hàm bằng độ dốc dây cung: $x_{i+1} = x_i - \\frac{f(x_i)(x_{i-1} - x_i)}{f(x_{i-1}) - f(x_i)}$.",
        "steps": [
            "**Bước 1: Thiết lập công thức cát tuyến**\n- Hàm số: $f(x) = 2x^3 - 11.7x^2 + 17.7x - 5$\n- Hai giá trị ban đầu: $x_{-1} = 3, x_0 = 4$\n- Giá trị hàm: $f(3) = -3.2, f(4) = 6.6$\n- Công thức: $x_{i+1} = x_i - \\frac{f(x_i)(x_{i-1} - x_i)}{f(x_{i-1}) - f(x_i)}$",
            f"**Bước 2: Bảng tính toán chi tiết 3 vòng lặp**\n\n{table8}",
            f"**Bước 3: Kết luận nghiệm**\nSau 3 vòng lặp cát tuyến, nghiệm thu được là $x = {rows8[-1]['xi_next']:.6f}$ với sai số xấp xỉ $\\varepsilon_a = {rows8[-1]['ea']:.4f}\\%$."
        ],
        "final_answer": f"x \\approx {rows8[-1]['xi_next']:.6f} \\quad (\\varepsilon_a = {rows8[-1]['ea']:.4f}\\%)"
    })

    out_file = Path("data/ch02_roots.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(problems)} verified problems to {out_file}.")

if __name__ == "__main__":
    main()
