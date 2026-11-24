"""Extract and solve Burden & Faires 9th Ed Calculus & ODE problems (Chapters 5 & 6 of Web App)."""

import json
from pathlib import Path
import numpy as np
import scipy.integrate as spi

CALC_FILE = Path("data/ch05_calculus.json")
ODE_FILE = Path("data/ch06_ode.json")

def m(v, d=6):
    if v is None:
        return r"\text{N/A}"
    if isinstance(v, (int, np.integer)):
        return str(v)
    if isinstance(v, (float, np.floating)):
        if abs(v) < 1e-12:
            return "0"
        if abs(v) >= 10000 or (abs(v) < 0.0001 and abs(v) > 0):
            return f"{v:.4e}"
        return f"{v:.{d}f}".rstrip("0").rstrip(".")
    return str(v)

def card(prob_id, source_name, method_tag, exam_focus, statement, hint, formula, steps_detail, conclusion, final_answer, target_value):
    return {
        "id": prob_id,
        "source_problem": source_name,
        "method_tag": method_tag,
        "exam_focus": exam_focus,
        "problem_en": statement,
        "glossary": {
            "numerical differentiation": "đạo hàm số / vi phân số",
            "three-point central difference": "sai phân hướng tâm 3 điểm",
            "second derivative": "đạo hàm cấp hai",
            "Composite Trapezoidal rule": "công thức hình thang mở rộng",
            "Composite Simpson rule": "công thức Simpson 1/3 mở rộng",
            "Euler's method": "phương pháp Euler",
            "Runge-Kutta method": "phương pháp Runge-Kutta",
            "local truncation error": "sai số chặt cụt địa phương",
            "step size": "bước nhảy h"
        },
        "hint": hint,
        "steps": [
            f"**Bước 1: Thiết lập công thức và điều kiện ban đầu**\n{formula}",
            f"**Bước 2: Bảng tính toán lặp số học (Kiểm chứng từ Python)**\n{steps_detail}",
            f"**Bước 3: Kết luận nghiệm và đánh giá sai số**\n{conclusion}"
        ],
        "final_answer": final_answer,
        "expected_numeric_value": float(target_value) if target_value is not None else 0.0
    }

# ==================== CHAPTER 5: CALCULUS ====================

def solve_diff_4_1():
    cards = []
    # 4.1 Problem 5a & 6a: 3-point central difference
    # Table from 6a:
    xs = np.array([-0.3, -0.2, -0.1, 0.0])
    fs = np.array([-0.27652, -0.25074, -0.16134, 0.0])
    h = 0.1
    # 3-point endpoint at -0.3: f'(-0.3) approx (-3f0 + 4f1 - f2) / (2h)
    d_m03 = (-3*fs[0] + 4*fs[1] - fs[2]) / (2*h)
    # 3-point central at -0.2: (f2 - f0) / (2h)
    d_m02 = (fs[2] - fs[0]) / (2*h)
    # 3-point central at -0.1: (f3 - f1) / (2h)
    d_m01 = (fs[3] - fs[1]) / (2*h)
    # 3-point endpoint at 0.0: (f1 - 4f2 + 3f3) / (2h)
    d_00 = (fs[1] - 4*fs[2] + 3*fs[3]) / (2*h)

    table_6a = (
        "| $x$ | $f(x)$ | Công thức 3 điểm sử dụng | $f'(x)$ tính toán |\n"
        "| :---: | :---: | :---: | :---: |\n"
        f"| -0.3 | -0.27652 | Đầu mút tiến: $\\frac{{-3f_0 + 4f_1 - f_2}}{{2h}}$ | {d_m03:.5f} |\n"
        f"| -0.2 | -0.25074 | Hướng tâm: $\\frac{{f(-0.1) - f(-0.3)}}{{2h}}$ | {d_m02:.5f} |\n"
        f"| -0.1 | -0.16134 | Hướng tâm: $\\frac{{f(0.0) - f(-0.2)}}{{2h}}$ | {d_m01:.5f} |\n"
        f"| 0.0 | 0.00000 | Đầu mút lùi: $\\frac{{f(-0.2) - 4f(-0.1) + 3f(0)}}{{2h}}$ | {d_00:.5f} |"
    )

    c6a = card(
        "ch05-burden-sec4.1-p6a",
        "Exercise 4.1 - Problem 6(a) (Burden & Faires 9th)",
        "Numerical Differentiation",
        True,
        "Use the most accurate three-point formula to determine each missing entry $f'(x)$ in the table:\n$$\\begin{array}{c|cccc} x & -0.3 & -0.2 & -0.1 & 0 \\\\ \\hline f(x) & -0.27652 & -0.25074 & -0.16134 & 0 \\end{array}$$",
        "Với các điểm bên trong ($x = -0.2, -0.1$), dùng công thức 3 điểm hướng tâm: $f'(x_0) = \\frac{f(x_0+h) - f(x_0-h)}{2h}$. Với hai đầu mút ($x = -0.3, 0$), dùng công thức 3 điểm đầu mút tương ứng.",
        "- Bước lưới đều: $h = 0.1$\n- Công thức hướng tâm (sai số $O(h^2)$): $f'(x_0) = \\frac{f(x_0+h) - f(x_0-h)}{2h}$\n- Công thức đầu mút tiến: $f'(x_0) = \\frac{-3f(x_0) + 4f(x_0+h) - f(x_0+2h)}{2h}$\n- Công thức đầu mút lùi: $f'(x_0) = \\frac{f(x_0-2h) - 4f(x_0-h) + 3f(x_0)}{2h}$",
        table_6a,
        f"Tại điểm $x = -0.2$, đạo hàm xấp xỉ đạt $f'(-0.2) \\approx {d_m02:.5f}$.",
        f"f'(-0.2) \\approx {d_m02:.5f}, \\; f'(-0.1) \\approx {d_m01:.5f}",
        d_m02
    )
    cards.append(c6a)

    # 4.1 Problem 19: Second derivative formula
    # f''(x0) approx [f(x0-h) - 2f(x0) + f(x0+h)] / h^2
    # Example function f(x) = cos(x) at x0 = 0.5, h = 0.1
    x0 = 0.5
    h_d2 = 0.1
    f_val = np.cos(x0)
    f_p = np.cos(x0 + h_d2)
    f_m = np.cos(x0 - h_d2)
    d2_app = (f_m - 2*f_val + f_p) / (h_d2**2)
    d2_exact = -np.cos(x0)
    err_d2 = abs(d2_exact - d2_app)

    c19 = card(
        "ch05-burden-sec4.1-p19",
        "Exercise 4.1 - Problem 19 (Burden & Faires 9th)",
        "Numerical Differentiation",
        True,
        "Use the second derivative formula $f''(x_0) \\approx \\frac{f(x_0-h) - 2f(x_0) + f(x_0+h)}{h^2}$ to approximate $f''(0.5)$ for $f(x) = \\cos x$ with step size $h = 0.1$. Compare with the analytical second derivative.",
        "Công thức sai phân trung tâm bậc 2 có sai số chặt cụt là $O(h^2)$: $f''(x_0) = \\frac{f(x_0-h) - 2f(x_0) + f(x_0+h)}{h^2} - \\frac{h^2}{12}f^{(4)}(\\xi)$.",
        "- Hàm số: $f(x) = \\cos x \\implies f''(x) = -\\cos x$\n- Điểm tính: $x_0 = 0.5, h = 0.1$\n- $f(0.4) = \\cos(0.4) \\approx 0.921061$\n- $f(0.5) = \\cos(0.5) \\approx 0.877583$\n- $f(0.6) = \\cos(0.6) \\approx 0.825336$",
        f"$$f''(0.5) \\approx \\frac{{0.921061 - 2(0.877583) + 0.825336}}{{0.01}} = \\frac{{-0.008769}}{{0.01}} = {d2_app:.6f}$$\n- Đạo hàm chính xác: $f''(0.5) = -\\cos(0.5) = {d2_exact:.6f}$\n- Sai số tuyệt đối: $|E| = {err_d2:.6e}$",
        f"Đạo hàm cấp 2 xấp xỉ đạt $f''(0.5) \\approx {d2_app:.4f}$, sai số nhỏ hơn $10^{{-3}}$ phù hợp với chặn lý thuyết $\\frac{{h^2}}{{12}}M = \\frac{{0.01}}{{12}}(1) \\approx 8.33 \\times 10^{{-4}}$.",
        f"f''(0.5) \\approx {d2_app:.4f} \\quad (\\text{{Exact: }} {d2_exact:.4f})",
        d2_app
    )
    cards.append(c19)
    return cards

def solve_integration_4_4():
    cards = []
    # Problem 1a: Composite Trapezoidal on int_1^2 x ln(x) dx, n=4
    # Exact integral: [x^2/2 ln x - x^2/4]_1^2 = 2 ln 2 - 1 - (0 - 1/4) = 2 ln 2 - 3/4 approx 0.636294
    a, b, n = 1.0, 2.0, 4
    h = (b - a) / n
    xs = np.linspace(a, b, n + 1)
    def f_1a(x): return x * np.log(x)
    ys = f_1a(xs)
    # Composite Trapezoidal: h/2 * [y0 + 2(y1 + y2 + y3) + y4]
    trap_1a = (h / 2.0) * (ys[0] + 2 * np.sum(ys[1:-1]) + ys[-1])
    # Composite Simpson: h/3 * [y0 + 4*y1 + 2*y2 + 4*y3 + y4]
    simp_1a = (h / 3.0) * (ys[0] + 4 * ys[1] + 2 * ys[2] + 4 * ys[3] + ys[-1])
    exact_1a = 2.0 * np.log(2.0) - 0.75

    table_1a = (
        "| $i$ | $x_i$ | $f(x_i) = x_i \\ln x_i$ | Trọng số Hình thang | Trọng số Simpson 1/3 |\n"
        "| :---: | :---: | :---: | :---: | :---: |\n" +
        "\n".join(f"| {i} | {xs[i]:.4f} | {ys[i]:.6f} | {1 if i in (0, n) else 2} | {1 if i in (0, n) else (4 if i % 2 == 1 else 2)} |" for i in range(n + 1))
    )

    c1a = card(
        "ch05-burden-sec4.4-p1a",
        "Exercise 4.4 - Problem 1(a) & 3(a) (Burden & Faires 9th)",
        "Composite Numerical Integration",
        True,
        "Use (a) the Composite Trapezoidal rule and (b) the Composite Simpson's rule with $n = 4$ subintervals to approximate the integral:\n$$\\int_1^2 x \\ln x \\, dx$$",
        "Bước chia $h = \\frac{b-a}{n} = \\frac{2-1}{4} = 0.25$. Lập bảng giá trị tại 5 mốc $x_i = 1.0, 1.25, 1.5, 1.75, 2.0$.",
        "- Công thức Hình thang mở rộng: $T(h) = \\frac{h}{2}\\left[f(x_0) + 2\\sum_{i=1}^{n-1} f(x_i) + f(x_n)\\right]$\n- Công thức Simpson 1/3 mở rộng: $S(h) = \\frac{h}{3}\\left[f(x_0) + 4\\sum_{\\text{lẻ}} f(x_i) + 2\\sum_{\\text{chẵn}} f(x_i) + f(x_n)\\right]$",
        table_1a,
        f"- Hình thang ($n=4$): $T = {trap_1a:.6f}$ (sai số $|E| = {abs(exact_1a - trap_1a):.6f}$)\n- Simpson ($n=4$): $S = {simp_1a:.6f}$ (sai số $|E| = {abs(exact_1a - simp_1a):.6f}$)\n- Giá trị giải tích chính xác: $I = 2\\ln 2 - \\frac{{3}}{{4}} \\approx {exact_1a:.6f}$. Simpson 1/3 đạt độ chính xác rất cao.",
        f"T = {trap_1a:.4f}, \\; S = {simp_1a:.6f} \\quad (I_{{\\text{{exact}}}} = {exact_1a:.6f})",
        simp_1a
    )
    cards.append(c1a)

    # Problem 1c: int_0^2 2/(x^2 + 4) dx, n=6 -> exact = arctan(1) = pi/4 approx 0.785398
    a, b, n = 0.0, 2.0, 6
    h = (b - a) / n
    xs = np.linspace(a, b, n + 1)
    def f_1c(x): return 2.0 / (x**2 + 4.0)
    ys = f_1c(xs)
    trap_1c = (h / 2.0) * (ys[0] + 2 * np.sum(ys[1:-1]) + ys[-1])
    simp_1c = (h / 3.0) * (ys[0] + 4 * np.sum(ys[1:-1:2]) + 2 * np.sum(ys[2:-1:2]) + ys[-1])
    exact_1c = np.pi / 4.0

    c1c = card(
        "ch05-burden-sec4.4-p1c",
        "Exercise 4.4 - Problem 1(c) & 3(c) (Burden & Faires 9th)",
        "Composite Numerical Integration",
        True,
        "Use the Composite Simpson's rule with $n = 6$ subintervals to approximate the integral:\n$$\\int_0^2 \\frac{2}{x^2 + 4} \\, dx$$",
        "Tích phân giải tích chính xác là $\\left[\\arctan(x/2)\\right]_0^2 = \\arctan(1) = \\frac{\\pi}{4} \\approx 0.785398$. Áp dụng công thức Simpson 1/3 với $n = 6, h = 1/3$.",
        "- Mốc tích phân: $x_i = 0, \\frac{1}{3}, \\frac{2}{3}, 1, \\frac{4}{3}, \\frac{5}{3}, 2$\n- Hàm số: $f(x) = \\frac{2}{x^2+4}$",
        f"Bảng 7 mốc nội suy:\n" + "\n".join(f"- $x_{i} = {xs[i]:.4f} \\implies f(x_{i}) = {ys[i]:.6f}$" for i in range(n+1)) + f"\n\nTổng hợp:\n$$S(h) = \\frac{{1/3}}{{3}}\\left[f_0 + 4(f_1+f_3+f_5) + 2(f_2+f_4) + f_6\\right] = {simp_1c:.6f}$$",
        f"Kết quả xấp xỉ đạt $S = {simp_1c:.6f}$, sai số so với $\\pi/4$ chỉ là $|{exact_1c - simp_1c:.2e}|$.",
        f"S = {simp_1c:.6f} \\quad (\\text{{Exact: }} \\frac{{\\pi}}{{4}} \\approx {exact_1c:.6f})",
        simp_1c
    )
    cards.append(c1c)
    return cards

# ==================== CHAPTER 6: ODE (IVP) ====================

def solve_ode_5_2():
    cards = []
    # Problem 1a: y' = y/t - (y/t)^2, 1 <= t <= 1.2, y(1) = 1, h = 0.1
    # Exact: y(t) = t / (1 + ln t)
    t0, y0, h, N = 1.0, 1.0, 0.1, 2
    def f_ode(t, y): return y/t - (y/t)**2
    def exact_y(t): return t / (1.0 + np.log(t))

    t_vals = [t0]
    w_euler = [y0]
    for i in range(N):
        ti = t_vals[-1]
        wi = w_euler[-1]
        w_next = wi + h * f_ode(ti, wi)
        t_vals.append(ti + h)
        w_euler.append(w_next)

    table_euler = (
        "| $i$ | $t_i$ | Nghiệm xấp xỉ $w_i$ (Euler) | Nghiệm chính xác $y(t_i)$ | Sai số tuyệt đối $|y(t_i) - w_i|$ |\n"
        "| :---: | :---: | :---: | :---: | :---: |\n" +
        "\n".join(f"| {i} | {t_vals[i]:.2f} | {w_euler[i]:.6f} | {exact_y(t_vals[i]):.6f} | {abs(exact_y(t_vals[i]) - w_euler[i]):.6f} |" for i in range(N + 1))
    )

    c1a = card(
        "ch06-burden-sec5.2-p1a",
        "Exercise 5.2 - Problem 1(a) (Burden & Faires 9th)",
        "Euler's Method",
        True,
        "Use Euler's method with step size $h = 0.1$ to approximate the solution to the initial-value problem:\n$$y' = \\frac{y}{t} - \\left(\\frac{y}{t}\\right)^2, \\quad 1 \\le t \\le 1.2, \\quad y(1) = 1$$\nCompare with the actual solution $y(t) = \\frac{t}{1 + \\ln t}$.",
        "Công thức lặp Euler: $w_{i+1} = w_i + h f(t_i, w_i)$ với $t_{i+1} = t_i + h$.",
        "- Điều kiện ban đầu: $t_0 = 1.0, w_0 = 1.0, h = 0.1$\n- Hàm vế phải: $f(t, y) = \\frac{y}{t} - \\left(\\frac{y}{t}\\right)^2$",
        table_euler,
        f"Tại $t = 1.2$, nghiệm xấp xỉ là $w_2 = {w_euler[-1]:.6f}$ so với nghiệm chính xác $y(1.2) = {exact_y(1.2):.6f}$ (sai số {abs(exact_y(1.2) - w_euler[-1]):.6f}).",
        f"w(1.2) \\approx {w_euler[-1]:.4f} \\quad (y_{{\\text{{exact}}}} = {exact_y(1.2):.4f})",
        w_euler[-1]
    )
    cards.append(c1a)

    # Problem 1b: y' = 1 + (t - y)^2, 2 <= t <= 3, y(2) = 1, h = 0.5
    # Exact: y(t) = t + 1/(1 - t)
    t0, y0, h, N = 2.0, 1.0, 0.5, 2
    def f_ode_1b(t, y): return 1.0 + (t - y)**2
    def exact_1b(t): return t + 1.0 / (1.0 - t)

    t_vals_b = [t0]
    w_euler_b = [y0]
    for i in range(N):
        ti = t_vals_b[-1]
        wi = w_euler_b[-1]
        w_next = wi + h * f_ode_1b(ti, wi)
        t_vals_b.append(ti + h)
        w_euler_b.append(w_next)

    c1b = card(
        "ch06-burden-sec5.2-p1b",
        "Exercise 5.2 - Problem 1(b) (Burden & Faires 9th)",
        "Euler's Method",
        True,
        "Use Euler's method with step size $h = 0.5$ to approximate the solution to:\n$$y' = 1 + (t - y)^2, \\quad 2 \\le t \\le 3, \\quad y(2) = 1$$\nCompare with the actual solution $y(t) = t + \\frac{1}{1 - t}$.",
        "Công thức lặp: $w_{i+1} = w_i + h [1 + (t_i - w_i)^2]$.",
        "- Ban đầu: $t_0 = 2, w_0 = 1, h = 0.5$\n- Nghiệm giải tích: $y(t) = t + \\frac{1}{1-t}$",
        f"- Bước 1 ($t_1 = 2.5$): $f(2, 1) = 1 + (2-1)^2 = 2 \\implies w_1 = 1 + 0.5(2) = 2.0000$\n  Nghiệm chính xác: $y(2.5) = 2.5 + \\frac{{1}}{{1-2.5}} = 2.5 - 0.6667 = 1.8333$\n- Bước 2 ($t_2 = 3.0$): $f(2.5, 2.0) = 1 + (2.5-2)^2 = 1.25 \\implies w_2 = 2.0 + 0.5(1.25) = 2.6250$\n  Nghiệm chính xác: $y(3.0) = 3 + \\frac{{1}}{{1-3}} = 2.5000$",
        f"Tại $t = 3.0$, nghiệm Euler là $w_2 = 2.6250$, sai số tuyệt đối là $|2.5000 - 2.6250| = 0.1250$.",
        "w(3.0) \\approx 2.6250 \\quad (y_{\\text{exact}} = 2.5000)",
        w_euler_b[-1]
    )
    cards.append(c1b)
    return cards

def solve_rk_5_4():
    cards = []
    # Problem 13a: Runge-Kutta Order 4 (RK4) for y' = y/t - (y/t)^2, 1 <= t <= 1.2, y(1) = 1, h = 0.1
    t0, y0, h, N = 1.0, 1.0, 0.1, 2
    def f_ode(t, y): return y/t - (y/t)**2
    def exact_y(t): return t / (1.0 + np.log(t))

    t_rk = [t0]
    w_rk = [y0]
    rows = []
    for i in range(N):
        ti = t_rk[-1]
        wi = w_rk[-1]
        k1 = h * f_ode(ti, wi)
        k2 = h * f_ode(ti + h/2.0, wi + k1/2.0)
        k3 = h * f_ode(ti + h/2.0, wi + k2/2.0)
        k4 = h * f_ode(ti + h, wi + k3)
        w_next = wi + (k1 + 2*k2 + 2*k3 + k4) / 6.0
        t_next = ti + h
        t_rk.append(t_next)
        w_rk.append(w_next)
        rows.append(f"| {i+1} | {t_next:.2f} | {k1:.6f} | {k2:.6f} | {k3:.6f} | {k4:.6f} | {w_next:.6f} | {exact_y(t_next):.6f} |")

    table_rk = (
        "| Bước $i$ | $t_i$ | $K_1$ | $K_2$ | $K_3$ | $K_4$ | $w_i$ (RK4) | $y(t_i)$ chính xác |\n"
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n" +
        "\n".join(rows)
    )

    c13a = card(
        "ch06-burden-sec5.4-p13a",
        "Exercise 5.4 - Problem 13(a) (Burden & Faires 9th)",
        "Runge-Kutta 4 (RK4)",
        True,
        "Use the Runge-Kutta method of order four (RK4) with $h = 0.1$ to approximate the solution of:\n$$y' = \\frac{y}{t} - \\left(\\frac{y}{t}\\right)^2, \\quad 1 \\le t \\le 1.2, \\quad y(1) = 1$$\nCompare with the actual solution $y(t) = \\frac{t}{1 + \\ln t}$.",
        "Tại mỗi bước tính 4 hệ số: $K_1 = h f(t, w)$, $K_2 = h f(t+h/2, w+K_1/2)$, $K_3 = h f(t+h/2, w+K_2/2)$, $K_4 = h f(t+h, w+K_3)$. Cập nhật: $w_{i+1} = w_i + \\frac{1}{6}(K_1 + 2K_2 + 2K_3 + K_4)$.",
        "- Bước nhảy: $h = 0.1$\n- Sai số chặt cụt địa phương đạt cấp 4: $O(h^4)$",
        table_rk,
        f"Tại $t = 1.2$, nghiệm RK4 là $w_2 = {w_rk[-1]:.6f}$ so với nghiệm chính xác $y(1.2) = {exact_y(1.2):.6f}$, sai số cực nhỏ $|E| = {abs(exact_y(1.2) - w_rk[-1]):.2e}$. Vượt trội hoàn toàn so với Euler.",
        f"w(1.2) \\approx {w_rk[-1]:.6f} \\quad (|E| = {abs(exact_y(1.2) - w_rk[-1]):.2e})",
        w_rk[-1]
    )
    cards.append(c13a)
    return cards

def main():
    # 1. Update Chapter 5 (Calculus)
    calc_cards = []
    calc_cards.extend(solve_diff_4_1())
    calc_cards.extend(solve_integration_4_4())

    ch05 = json.loads(CALC_FILE.read_text(encoding="utf-8")) if CALC_FILE.exists() else []
    existing_calc = {x["id"] for x in ch05}
    added_calc = 0
    for c in calc_cards:
        if c["id"] not in existing_calc:
            ch05.append(c)
            existing_calc.add(c["id"])
            added_calc += 1
    CALC_FILE.write_text(json.dumps(ch05, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {CALC_FILE}: added {added_calc}, total {len(ch05)} problems.")

    # 2. Update Chapter 6 (ODE)
    ode_cards = []
    ode_cards.extend(solve_ode_5_2())
    ode_cards.extend(solve_rk_5_4())

    ch06 = json.loads(ODE_FILE.read_text(encoding="utf-8")) if ODE_FILE.exists() else []
    existing_ode = {x["id"] for x in ch06}
    added_ode = 0
    for c in ode_cards:
        if c["id"] not in existing_ode:
            ch06.append(c)
            existing_ode.add(c["id"])
            added_ode += 1
    ODE_FILE.write_text(json.dumps(ch06, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {ODE_FILE}: added {added_ode}, total {len(ch06)} problems.")

if __name__ == "__main__":
    main()
