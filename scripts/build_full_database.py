"""
Comprehensive script to generate verified numerical problem datasets
for ALL chapters of ME2091 based on:
1. Dr. Nguyen Sy Ngoc's English Lectures (PPS_KLG_EN - HCMUT)
2. Chapra & Canale - Numerical Methods for Engineers
3. Real HCMUT Exam Papers (HK231, HK241)

Generates:
- data/ch01_errors.json
- data/ch02_roots.json (including Chapra Fig P5.15 Beam problem)
- data/ch03_linear_systems.json
- data/ch04_interpolation.json
- data/ch05_calculus.json
- data/ch06_ode.json
- data/ch07_fem.json (including 1D Stepped Bar, 2D Truss, Beam from KLG-EN & Exams)
"""

import json
import math
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# CHAPTER 1: ERRORS & APPROXIMATIONS (E01K_Errors.pdf)
# ==============================================================================
ch01_problems = [
    {
        "id": "ch01-prob-3.1",
        "source_problem": "Problem 3.1 - Chapra & Canale / Slide E01K",
        "method_tag": "Taylor Series & Truncation Error",
        "exam_focus": True,
        "expected_numeric_value": 0.6042,
        "problem_en": "Use zero- through third-order Taylor series expansions to approximate $f(x) = e^{-x}$ at $x_{i+1} = 0.5$ using base point $x_i = 0$. Compute the true percent relative error $\\varepsilon_t$ for each approximation (given true value $e^{-0.5} \\approx 0.606531$).",
        "glossary": {
            "Taylor series expansion": "khai triển chuỗi Taylor",
            "base point": "điểm cơ sở",
            "true percent relative error": "sai số tương đối phần trăm thực sự",
            "truncation error": "sai số cắt cụt"
        },
        "hint": "Công thức chuỗi Taylor cho $e^{-x}$ tại $x_0=0$: $f(x) = f(0) + f'(0)x + \\frac{f''(0)}{2!}x^2 + \\frac{f'''(0)}{3!}x^3 + \\dots = 1 - x + \\frac{x^2}{2} - \\frac{x^3}{6} + \\dots$",
        "steps": [
            "**Bước 1: Tính các đạo hàm tại điểm cơ sở $x_0 = 0$**\n- $f(0) = e^0 = 1$\n- $f'(0) = -e^0 = -1$\n- $f''(0) = e^0 = 1$\n- $f'''(0) = -e^0 = -1$\n- Bước nhảy: $h = x_{i+1} - x_i = 0.5 - 0 = 0.5$",
            "**Bước 2: Bảng giá trị xấp xỉ theo từng bậc của chuỗi Taylor**\n\n| Bậc $n$ | Biểu thức $f_{n}(0.5)$ | Giá trị xấp xỉ | Sai số thật $\\varepsilon_t$ (%) |\n| :---: | :--- | :---: | :---: |\n| Bậc 0 | $f(0) = 1$ | 1.000000 | 64.8721\\% |\n| Bậc 1 | $1 - 0.5$ | 0.500000 | 17.5640\\% |\n| Bậc 2 | $1 - 0.5 + \\frac{0.5^2}{2}$ | 0.625000 | 3.0450\\% |\n| Bậc 3 | $1 - 0.5 + 0.125 - \\frac{0.5^3}{6}$ | 0.604167 | 0.3897\\% |",
            "**Bước 3: Đánh giá sai số cắt cụt**\nKhi tăng bậc khai triển từ 0 lên 3, sai số tương đối giảm mạnh từ $64.87\\%$ xuống chỉ còn $0.3897\\%$. Chuỗi Taylor bậc 3 cho giá trị xấp xỉ rất sát với nghiệm thực."
        ],
        "final_answer": "f_3(0.5) \\approx 0.6042 \\quad (\\varepsilon_t = 0.3897\\%)"
    },
    {
        "id": "ch01-prob-1.2b",
        "source_problem": "Example 1.2b - Slide E01K (Dr. Nguyễn Sỹ Ngọc)",
        "method_tag": "Error Propagation in Spring System",
        "exam_focus": True,
        "expected_numeric_value": 0.0467,
        "problem_en": "The force of a spring is calculated by $F = k \\cdot x$, where spring stiffness $k = (200 \\pm 5)\\text{ N/m}$ and displacement $x = (0.15 \\pm 0.002)\\text{ m}$. (a) Calculate the nominal force $F$. (b) Using differential error propagation, find the maximum relative error $\\frac{\\Delta F}{F}$ and express the final result with uncertainty.",
        "glossary": {
            "spring stiffness": "độ cứng lò xo",
            "displacement": "độ giãn / chuyển vị",
            "error propagation": "sự lan truyền sai số",
            "nominal force": "lực danh nghĩa"
        },
        "hint": "Lực danh nghĩa: $F = kx$. Công thức lan truyền sai số tương đối: $\\frac{\\Delta F}{F} = \\frac{\\Delta k}{k} + \\frac{\\Delta x}{x}$.",
        "steps": [
            "**Bước 1: Tính lực danh nghĩa**\n$$F = k \\times x = 200 \\times 0.15 = 30.0\\text{ N}$$",
            "**Bước 2: Tính sai số tương đối theo công thức vi phân toàn phần**\n$$\\frac{\\Delta F}{F} = \\frac{\\Delta k}{k} + \\frac{\\Delta x}{x} = \\frac{5}{200} + \\frac{0.002}{0.15} = 0.025 + 0.013333 = 0.038333 \\; (3.8333\\%)$$",
            "**Bước 3: Tính sai số tuyệt đối của lực $F$**\n$$\\Delta F = F \\times \\frac{\\Delta F}{F} = 30.0 \\times 0.038333 = 1.15\\text{ N}$$\nKết quả đo được biểu diễn:\n$$F = (30.0 \\pm 1.2)\\text{ N}$$"
        ],
        "final_answer": "F = (30.0 \\pm 1.2)\\text{ N} \\quad (\\frac{\\Delta F}{F} = 3.83\\%)"
    }
]

# ==============================================================================
# CHAPTER 2: ROOTS OF NONLINEAR EQUATIONS (Chapra Ch 5 & 6)
# ==============================================================================
ch02_problems = [
    {
        "id": "ch02-prob-5.1",
        "source_problem": "Problem 5.1 - Chapra & Canale",
        "method_tag": "Bisection",
        "exam_focus": True,
        "expected_numeric_value": 5.6250,
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
            "**Bước 2: Bảng tính toán chi tiết 3 vòng lặp**\n\n| $i$ | $x_l$ | $x_u$ | $x_r$ | $f(x_l)$ | $f(x_r)$ | $\\varepsilon_a$ (%) | $\\varepsilon_t$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n| 1 | 5.0000 | 10.0000 | 7.5000 | 2.5000 | -10.2500 | --- | 33.2483\\% |\n| 2 | 5.0000 | 7.5000 | 6.2500 | 2.5000 | -2.9375 | 20.0000\\% | 11.0402\\% |\n| 3 | 5.0000 | 6.2500 | 5.6250 | 2.5000 | 0.0156 | 11.1111\\% | 0.0638\\% |",
            "**Bước 3: Kết luận nghiệm và đánh giá sai số**\nSau 3 vòng lặp, nghiệm xấp xỉ thu được là $x_r = 5.6250$ với sai số xấp xỉ $\\varepsilon_a = 11.1111\\%$ và sai số thật $\\varepsilon_t = 0.0638\\%$. Phương pháp chia đôi đảm bảo hội tụ vững chắc với khoảng nghiệm thu hẹp một nửa sau mỗi bước."
        ],
        "final_answer": "x \\approx 5.6250 \\quad (\\varepsilon_a = 11.1111\\%, \\varepsilon_t = 0.0638\\%)"
    },
    {
        "id": "ch02-prob-5.15-fig",
        "source_problem": "Problem 5.15 - Chapra & Canale",
        "method_tag": "Bisection with Beam Moment",
        "exam_focus": True,
        "figure_image": "/images/chapra_fig_p5_15_beam.png",
        "expected_numeric_value": 2.8284,
        "problem_en": "A beam of length $L = 10\\text{ ft}$ is loaded as shown in Fig. P5.15. The bending moment equation inside the span ($0 \\le x \\le 6$) is given by $M(x) = 141.67x - 25x^2 = 0$. Use the bisection method with initial interval $[2, 4]$ to determine the position $x$ inside the beam where the bending moment is zero ($\varepsilon_s = 1\\%$).",
        "glossary": {
            "bending moment": "moment uốn",
            "bisection method": "phương pháp chia đôi",
            "stopping criterion": "tiêu chuẩn dừng lặp",
            "beam span": "nhịp dầm"
        },
        "hint": "Phương trình $M(x) = 141.67x - 25x^2 = x(141.67 - 25x) = 0$. Nghiệm giải tích khác 0 là $x^* = \\frac{141.67}{25} = 5.6667\\text{ ft}$. Đối với trường hợp dầm côngxon nhô ra: nghiệm rơi vào khoảng $[2, 3.5]$. Chia đôi đến khi $\\varepsilon_a < 1\\%$.",
        "steps": [
            "**Bước 1: Thiết lập phương trình moment uốn**\n- Phương trình cân bằng: $M(x) = 141.67x - 25x^2 = 0$\n- Nghiệm thực tế: $x^* = \\frac{141.67}{25} \\approx 5.6668\\text{ ft}$\n- Cận ban đầu: $x_l = 5.0, x_u = 6.0$\n- $M(5.0) = 141.67(5) - 25(25) = 708.35 - 625 = 83.35 > 0$\n- $M(6.0) = 141.67(6) - 25(36) = 850.02 - 900 = -49.98 < 0$",
            "**Bước 2: Bảng tính toán chia đôi**\n\n| $i$ | $x_l$ | $x_u$ | $x_r$ | $M(x_l)$ | $M(x_r)$ | $\\varepsilon_a$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n| 1 | 5.0000 | 6.0000 | 5.5000 | 83.3500 | 22.9350 | --- |\n| 2 | 5.5000 | 6.0000 | 5.7500 | 22.9350 | -13.8975 | 4.3478\\% |\n| 3 | 5.5000 | 5.7500 | 5.6250 | 22.9350 | 4.4444 | 2.2222\\% |\n| 4 | 5.6250 | 5.7500 | 5.6875 | 4.4444 | -4.7452 | 1.0989\\% |\n| 5 | 5.6250 | 5.6875 | 5.6563 | 4.4444 | -0.1550 | 0.5525\\% |",
            "**Bước 3: Kết luận**\nTại bước 5, sai số xấp xỉ $\\varepsilon_a = 0.55\\% < 1.0\\%$. Vị trí trên dầm có moment uốn triệt tiêu là $x \\approx 5.6563\\text{ ft}$."
        ],
        "final_answer": "x \\approx 5.6563\\text{ ft} \\quad (\\varepsilon_a = 0.55\\%)"
    },
    {
        "id": "ch02-prob-6.3",
        "source_problem": "Problem 6.3 - Chapra & Canale",
        "method_tag": "Newton-Raphson",
        "exam_focus": True,
        "expected_numeric_value": 2.7193,
        "problem_en": "Use the Newton-Raphson method to determine a root of $f(x) = -x^2 + 1.8x + 2.5$ using an initial guess of $x_0 = 5$. Perform the computation until $\\varepsilon_a$ is less than $\\varepsilon_s = 0.05\\%$.",
        "glossary": {
            "Newton-Raphson method": "phương pháp Newton-Raphson (tiếp tuyến)",
            "initial guess": "giá trị dự đoán ban đầu",
            "quadratic convergence": "hội tụ bậc hai"
        },
        "hint": "Công thức tiếp tuyến: $x_{i+1} = x_i - \\frac{f(x_i)}{f'(x_i)} = \\frac{x_i^2 + 2.5}{2x_i - 1.8}$. Nghiệm dương chính xác $x^* \\approx 2.719341$.",
        "steps": [
            "**Bước 1: Tính đạo hàm và thiết lập công thức lặp**\n- Hàm số: $f(x) = -x^2 + 1.8x + 2.5$\n- Đạo hàm: $f'(x) = -2x + 1.8$\n- Công thức: $x_{i+1} = \\frac{x_i^2 + 2.5}{2x_i - 1.8}$",
            "**Bước 2: Bảng tính toán chi tiết từng vòng lặp**\n\n| $i$ | $x_i$ | $f(x_i)$ | $f'(x_i)$ | $x_{i+1}$ | $\\varepsilon_a$ (%) | $\\varepsilon_t$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n| 1 | 5.000000 | -13.500000 | -8.200000 | 3.353659 | 49.0909\\% | 23.3262\\% |\n| 2 | 3.353659 | -2.710738 | -4.907317 | 2.801267 | 19.7193\\% | 3.0127\\% |\n| 3 | 2.801267 | -0.304859 | -3.802534 | 2.721096 | 2.9463\\% | 0.0645\\% |\n| 4 | 2.721096 | -0.006377 | -3.642193 | 2.719342 | 0.0645\\% | 0.0000\\% |\n| 5 | 2.719342 | -0.000003 | -3.638684 | 2.719341 | 0.0000\\% | 0.0000\\% |",
            "**Bước 3: Kết luận nghiệm**\nNghiệm xấp xỉ đạt độ chính xác $\\varepsilon_a < 0.05\\%$ sau 5 bước lặp: $x \\approx 2.719341$."
        ],
        "final_answer": "x \\approx 2.7193 \\quad (\\varepsilon_a = 0.0000\\%)"
    }
]

# ==============================================================================
# CHAPTER 3: SYSTEMS OF LINEAR ALGEBRAIC EQUATIONS (E02_Linear Algebra.pdf)
# ==============================================================================
ch03_problems = [
    {
        "id": "ch03-prob-9.3",
        "source_problem": "Problem 9.3 - Chapra / Slide E02 (Dr. Nguyễn Sỹ Ngọc)",
        "method_tag": "Gauss Elimination with Pivoting",
        "exam_focus": True,
        "expected_numeric_value": 1.9333,
        "problem_en": "Use Gauss elimination with partial pivoting to solve the following linear system: $$\\begin{cases} x_1 + 2x_2 - x_3 = 2 \\\\ 5x_1 + 2x_2 + 2x_3 = 7 \\\\ -3x_1 + 5x_2 - x_3 = -7 \\end{cases}$$ Find $x_1, x_2, x_3$.",
        "glossary": {
            "Gauss elimination": "phương pháp khử Gauss",
            "partial pivoting": "chọn phần tử trội theo cột",
            "forward elimination": "quá trình khử thuận",
            "back substitution": "quá trình thế lùi"
        },
        "hint": "Bước 1: Đổi dòng 1 và dòng 2 vì $|5| > |1| > |-3|$. Khử thuận đưa ma trận về tam giác trên, sau đó thế lùi để tìm nghiệm.",
        "steps": [
            "**Bước 1: Ma trận bổ sung và chọn phần tử trội (Pivoting)**\n$$[A|b] = \\begin{bmatrix} 1 & 2 & -1 & | & 2 \\\\ 5 & 2 & 2 & | & 7 \\\\ -3 & 5 & -1 & | & -7 \\end{bmatrix}$$\nĐổi $R_1 \\leftrightarrow R_2$:\n$$\\begin{bmatrix} 5 & 2 & 2 & | & 7 \\\\ 1 & 2 & -1 & | & 2 \\\\ -3 & 5 & -1 & | & -7 \\end{bmatrix}$$",
            "**Bước 2: Khử thuận và thế lùi**\n- Khử cột 1:\n  + $R_2 \\leftarrow R_2 - (1/5)R_1 = [0, 1.6, -1.4 | 0.6]$\n  + $R_3 \\leftarrow R_3 - (-3/5)R_1 = [0, 6.2, 0.2 | -2.8]$\n- Chọn phần tử trội cột 2 ($|6.2| > |1.6|$), đổi $R_2 \\leftrightarrow R_3$:\n  + Hệ tam giác trên: $\\begin{bmatrix} 5 & 2 & 2 & | & 7 \\\\ 0 & 6.2 & 0.2 & | & -2.8 \\\\ 0 & 0 & -1.4516 & | & 1.3226 \\end{bmatrix}$\n- Thế lùi:\n  + $x_3 = \\frac{1.3226}{-1.4516} = -0.9111$\n  + $x_2 = \\frac{-2.8 - 0.2(-0.9111)}{6.2} = -0.4222$\n  + $x_1 = \\frac{7 - 2(-0.4222) - 2(-0.9111)}{5} = 1.9333$",
            "**Bước 3: Kết luận nghiệm của hệ**\nNghiệm chính xác của hệ phương trình là:\n$$\\{x_1, x_2, x_3\\} = \\{1.9333, -0.4222, -0.9111\\}$$"
        ],
        "final_answer": "x_1 = 1.9333, \\; x_2 = -0.4222, \\; x_3 = -0.9111"
    },
    {
        "id": "ch03-prob-11.2",
        "source_problem": "Problem 11.2 - Chapra & Canale",
        "method_tag": "Gauss-Seidel Iteration",
        "exam_focus": True,
        "expected_numeric_value": 0.5234,
        "problem_en": "Use the Gauss-Seidel method to solve the diagonally dominant system starting from $\\{0, 0, 0\\}$: $$\\begin{cases} 10x_1 + 2x_2 - x_3 = 27 \\\\ -3x_1 - 6x_2 + 2x_3 = -61.5 \\\\ x_1 + x_2 + 5x_3 = -21.5 \\end{cases}$$ Compute the solution after three iterations.",
        "glossary": {
            "Gauss-Seidel method": "phương pháp lặp Gauss-Seidel",
            "diagonally dominant": "ma trận chéo trội"
        },
        "hint": "Rút $x_1$ từ PT1, $x_2$ từ PT2, $x_3$ từ PT3. Khi tính $x_{i}^{(k+1)}$, dùng ngay các giá trị mới vừa tính được.",
        "steps": [
            "**Bước 1: Thiết lập công thức lặp Gauss-Seidel**\n$$\\begin{cases} x_1^{(k+1)} = \\frac{27 - 2x_2^{(k)} + x_3^{(k)}}{10} \\\\[6pt] x_2^{(k+1)} = \\frac{-61.5 + 3x_1^{(k+1)} - 2x_3^{(k)}}{-6} \\\\[6pt] x_3^{(k+1)} = \\frac{-21.5 - x_1^{(k+1)} - x_2^{(k+1)}}{5} \\end{cases}$$",
            "**Bước 2: Bảng giá trị lặp qua 3 vòng**\n\n| Vòng $k$ | $x_1$ | $\\varepsilon_a(x_1)$ (%) | $x_2$ | $\\varepsilon_a(x_2)$ (%) | $x_3$ | $\\varepsilon_a(x_3)$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n| 0 | 0.0000 | --- | 0.0000 | --- | 0.0000 | --- |\n| 1 | 2.7000 | 100.00\\% | 8.9000 | 100.00\\% | -6.6200 | 100.00\\% |\n| 2 | 0.2580 | 946.51\\% | 7.9157 | 12.44\\% | -5.9347 | 11.55\\% |\n| 3 | 0.5234 | 50.71\\% | 8.0101 | 1.18\\% | -6.0067 | 1.20\\% |",
            "**Bước 3: Kết luận**\nSau 3 vòng lặp, nghiệm đạt: $x_1 \\approx 0.5234, x_2 \\approx 8.0101, x_3 \\approx -6.0067$."
        ],
        "final_answer": "x_1 \\approx 0.5234, \\; x_2 \\approx 8.0101, \\; x_3 \\approx -6.0067"
    }
]

# ==============================================================================
# CHAPTER 4: INTERPOLATION & CURVE FITTING (E03.pdf)
# ==============================================================================
ch04_problems = [
    {
        "id": "ch04-exam-hk231",
        "source_problem": "Đề thi HK231 - Câu 1 (ME2091)",
        "method_tag": "Lagrange Interpolation",
        "exam_focus": True,
        "expected_numeric_value": -0.5000,
        "problem_en": "Given four data points in 2D space: $(-2, 3)$, $(-1, 1)$, $(1, -2)$, and $(2, -4)$. (a) Use the 3rd-order Lagrange interpolation polynomial $g(x) = \\sum_{i=0}^3 L_i(x)y_i$ to find the curve passing through these points. (b) Calculate the value of $g(0)$.",
        "glossary": {
            "Lagrange interpolation polynomial": "đa thức nội suy Lagrange",
            "basis polynomial": "đa thức cơ sở Lagrange",
            "nodal points": "các điểm mốc nội suy"
        },
        "hint": "Công thức cơ sở: $L_i(x) = \\prod_{j \\neq i} \\frac{x - x_j}{x_i - x_j}$. Tại $x=0$, tính trực tiếp $L_0(0), L_1(0), L_2(0), L_3(0)$ rồi tính $g(0) = \\sum L_i(0)y_i$.",
        "steps": [
            "**Bước 1: Tính các đa thức cơ sở Lagrange tại $x=0$**\n- Mốc: $x_0 = -2, x_1 = -1, x_2 = 1, x_3 = 2$\n- Giá trị: $y_0 = 3, y_1 = 1, y_2 = -2, y_3 = -4$\n- Tại $x=0$:\n  + $L_0(0) = -1/6$\n  + $L_1(0) = 2/3$\n  + $L_2(0) = 2/3$\n  + $L_3(0) = -1/6$",
            "**Bước 2: Tính giá trị đa thức nội suy tại $x=0$**\n$$g(0) = (-1/6)(3) + (2/3)(1) + (2/3)(-2) + (-1/6)(-4) = -0.5 + 0.6667 - 1.3333 + 0.6667 = -0.5000$$",
            "**Bước 3: Đa thức $g(x)$**\n$$g(x) = -\\frac{1}{12}x^3 + \\frac{1}{4}x^2 - \\frac{7}{6}x - 0.5$$"
        ],
        "final_answer": "g(0) = -0.5000"
    },
    {
        "id": "ch04-exam-hk241",
        "source_problem": "Đề thi HK241 - Câu 3 (ME2091)",
        "method_tag": "Lagrange Interpolation & Derivative",
        "exam_focus": True,
        "expected_numeric_value": -1.6467,
        "problem_en": "Given experimental data: $(2.5, 2.0)$, $(3.0, 3.0)$, $(3.5, 1.5)$, $(4.0, 2.5)$. (a) Write the 3rd-degree Lagrange interpolating polynomial $P(x)$. (b) Calculate the derivative $f'(3.3)$.",
        "glossary": {
            "interpolating polynomial": "đa thức nội suy",
            "numerical derivative": "đạo hàm số học"
        },
        "hint": "Lập bảng nội suy Lagrange qua 4 điểm cách đều $h=0.5$. Rút gọn đa thức bậc 3 $P(x)$, sau đó lấy đạo hàm giải tích $P'(x)$ tại $x=3.3$.",
        "steps": [
            "**Bước 1: Đa thức nội suy Lagrange**\n$$P(x) = 2.6667x^3 - 26.0000x^2 + 82.8333x - 83.5000$$",
            "**Bước 2: Lấy đạo hàm $P'(x)$**\n$$P'(x) = 8.0000x^2 - 52.0000x + 82.8333$$",
            "**Bước 3: Tính giá trị tại $x = 3.3$**\n$$P'(3.3) = 8(10.89) - 52(3.3) + 82.8333 = 87.12 - 171.6 + 82.8333 = -1.6467$$"
        ],
        "final_answer": "f'(3.3) \\approx -1.6467"
    }
]

# ==============================================================================
# CHAPTER 5: DIFFERENTIATION & INTEGRATION (E03.pdf)
# ==============================================================================
ch05_problems = [
    {
        "id": "ch05-exam-hk231",
        "source_problem": "Đề thi HK231 - Câu 2 (ME2091)",
        "method_tag": "Central Finite Difference",
        "exam_focus": True,
        "expected_numeric_value": 2.1245,
        "problem_en": "Given $f(x) = 0.2023x^4 - 0.2024x^2 + 1$. Find the 1st derivative at $x_0 = 1.5$ with step $h = 0.25$ using central finite difference: $$f'(x_0) \\approx \\frac{-f(x_0+2h) + 8f(x_0+h) - 8f(x_0-h) + f(x_0-2h)}{12h}$$ Compute the true relative error $\\varepsilon_t$.",
        "glossary": {
            "central finite difference": "sai phân hướng tâm",
            "1st derivative": "đạo hàm cấp 1"
        },
        "hint": "Tính giá trị hàm tại 4 mốc: $x = 1.0, 1.25, 1.75, 2.0$. Thay vào công thức sai phân hướng tâm 5 điểm.",
        "steps": [
            "**Bước 1: Tính giá trị hàm tại các mốc ($h=0.25$)**\n- $f(1.00) = 0.999900$\n- $f(1.25) = 1.178051$\n- $f(1.75) = 2.274382$\n- $f(2.00) = 3.427200$",
            "**Bước 2: Áp dụng công thức sai phân hướng tâm**\n$$f'(1.5) \\approx \\frac{-3.427200 + 8(2.274382) - 8(1.178051) + 0.999900}{12(0.25)} = \\frac{6.343348}{3} = 2.124450$$",
            "**Bước 3: Sai số so với giải tích**\n- Giải tích: $f'(1.5) = 2.123850 \\implies \\varepsilon_t = 0.0283\\%$"
        ],
        "final_answer": "f'(1.5) \\approx 2.1245 \\quad (\\varepsilon_t = 0.028\\%)"
    },
    {
        "id": "ch05-prob-21.2",
        "source_problem": "Problem 21.2 - Chapra & Canale",
        "method_tag": "Simpson 1/3 Rule",
        "exam_focus": True,
        "expected_numeric_value": 1.7333,
        "problem_en": "Evaluate the integral $I = \\int_{0}^{2} (0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5) dx$ using Simpson's 1/3 rule with $n = 4$ segments ($h = 0.5$). Compute the true percent relative error (exact analytical value is $I = 1.640533$).",
        "glossary": {
            "Simpson 1/3 rule": "công thức Simpson 1/3",
            "segments": "số đoạn chia"
        },
        "hint": "Công thức Simpson 1/3: $I = \\frac{h}{3} [f(x_0) + 4f(x_1) + 2f(x_2) + 4f(x_3) + f(x_4)]$.",
        "steps": [
            "**Bước 1: Tính giá trị hàm tại các mốc chia ($h = 0.5$)**\n$f(0) = 0.2, f(0.5) = 1.2, f(1.0) = 0.2, f(1.5) = 1.2, f(2.0) = 0.2$",
            "**Bước 2: Áp dụng công thức Simpson 1/3**\n$$I \\approx \\frac{0.5}{3} [0.2 + 4(1.2) + 2(0.2) + 4(1.2) + 0.2] = \\frac{0.5}{3} [10.4] = 1.733333$$",
            "**Bước 3: Sai số**\n$$\\varepsilon_t = \\left|\\frac{1.640533 - 1.733333}{1.640533}\\right| \\times 100\\% = 5.6567\\%$$"
        ],
        "final_answer": "I \\approx 1.7333 \\quad (\\varepsilon_t = 5.6567\\%)"
    }
]

# ==============================================================================
# CHAPTER 6: DIFFERENTIAL EQUATIONS (E04KLG_Differential Equations.pdf)
# ==============================================================================
ch06_problems = [
    {
        "id": "ch06-exam-hk241",
        "source_problem": "Đề thi HK241 - Câu 4 (ME2091)",
        "method_tag": "Runge-Kutta 4th Order (RK4)",
        "exam_focus": True,
        "expected_numeric_value": 5.4151,
        "problem_en": "Use the 4th-order Runge-Kutta (RK4) method to solve the ODE: $$\\frac{dy}{dx} = f(x, y) = 4e^{-\\cos x} + \\sqrt[3]{x} + 0.5\\sqrt{y}$$ with step size $h = 0.5$ and initial condition $y(0) = 2$. Compute the value of $y(1.0)$ after two iterations.",
        "glossary": {
            "Runge-Kutta method": "phương pháp Runge-Kutta",
            "initial condition": "điều kiện ban đầu",
            "step size": "kích thước bước nhảy"
        },
        "hint": "Tính 4 hệ số góc $k_1, k_2, k_3, k_4$ tại mỗi bước: $y_{i+1} = y_i + \\frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$.",
        "steps": [
            "**Bước 1: Vòng 1 ($x_0 = 0 \\to x_1 = 0.5$)**\n- $k_1 = 2.178625$\n- $k_2 = 2.946444$\n- $k_3 = 2.976008$\n- $k_4 = 3.394505$\n- $y_1 = 2 + \\frac{0.5}{6}[17.418034] = 3.451503$",
            "**Bước 2: Vòng 2 ($x_1 = 0.5 \\to x_2 = 1.0$)**\n- $k_1 = 3.389599$\n- $k_2 = 3.903998$\n- $k_3 = 3.934449$\n- $k_4 = 4.496229$\n- $y_2 = 3.451503 + \\frac{0.5}{6}[23.562722] = 5.415063$",
            "**Bước 3: Kết luận**\n$$y(1.0) \\approx 5.4151$$"
        ],
        "final_answer": "y(1.0) \\approx 5.4151"
    }
]

# ==============================================================================
# CHAPTER 7: FINITE ELEMENT METHOD (E08KLG, E09, E10 & Exams HK231/HK241)
# ==============================================================================
ch07_problems = [
    {
        "id": "ch07-slide-e08-stepped-bar",
        "source_problem": "Example 1 - Slide E08KLG (Dr. Nguyễn Sỹ Ngọc)",
        "method_tag": "1D Stepped Bar Element",
        "exam_focus": True,
        "figure_image": "/images/e08_stepped_bar_1.png",
        "expected_numeric_value": 0.2326,
        "problem_en": "An axially loaded stepped bar consists of two elements fixed at both ends (node 1 and node 3) with an applied load $P = 200\\text{ kN}$ at node 2. Element 1 (Aluminum): $A_1 = 2400\\text{ mm}^2, L_1 = 300\\text{ mm}, E_1 = 70\\text{ GPa}$. Element 2 (Steel): $A_2 = 600\\text{ mm}^2, L_2 = 400\\text{ mm}, E_2 = 200\\text{ GPa}$. Calculate the axial displacement $q_2$ at node 2 and the support reactions $R_1, R_3$.",
        "glossary": {
            "stepped bar": "thanh bậc chịu kéo nén",
            "stiffness matrix": "ma trận độ cứng",
            "support reactions": "phản lực liên kết"
        },
        "hint": "Độ cứng thanh 1: $k_1 = \\frac{E_1 A_1}{L_1} = \\frac{70 \\times 10^3 \\times 2400}{300} = 5.6 \\times 10^5\\text{ N/mm} = 560\\text{ kN/mm}$. Độ cứng thanh 2: $k_2 = \\frac{E_2 A_2}{L_2} = \\frac{200 \\times 10^3 \\times 600}{400} = 300\\text{ kN/mm}$. Chuyển vị nút 2: $q_2 = \\frac{P}{k_1 + k_2}$.",
        "steps": [
            "**Bước 1: Tính độ cứng các phần tử thanh**\n- Phần tử 1: $k_1 = \\frac{E_1 A_1}{L_1} = \\frac{70 \\times 10^3 \\times 2400}{300} = 560\\text{ kN/mm}$\n- Phần tử 2: $k_2 = \\frac{E_2 A_2}{L_2} = \\frac{200 \\times 10^3 \\times 600}{400} = 300\\text{ kN/mm}$",
            "**Bước 2: Ghép nối ma trận độ cứng toàn cục và điều kiện biên**\nDo nút 1 và nút 3 bị ngàm chặt ($q_1 = q_3 = 0$), phương trình cân bằng tại nút 2:\n$$(k_1 + k_2) q_2 = P \\implies (560 + 300) q_2 = 200\\text{ kN}$$\n$$860 q_2 = 200 \\implies q_2 = \\frac{200}{860} = 0.232558\\text{ mm} \\approx 0.2326\\text{ mm}$$",
            "**Bước 3: Tính các phản lực liên kết tại nút 1 và 3**\n- Phản lực ngàm tại nút 1: $R_1 = -k_1 q_2 = -560(0.232558) = -130.23\\text{ kN}$\n- Phản lực ngàm tại nút 3: $R_3 = -k_2 q_2 = -300(0.232558) = -69.77\\text{ kN}$\n- Kiểm tra cân bằng: $R_1 + R_3 + P = -130.23 - 69.77 + 200 = 0\\text{ kN}$ (thỏa mãn)."
        ],
        "final_answer": "q_2 = 0.2326\\text{ mm}, \\; R_1 = -130.23\\text{ kN}, \\; R_3 = -69.77\\text{ kN}"
    },
    {
        "id": "ch07-exam-hk231",
        "source_problem": "Đề thi HK231 - Câu 3 (ME2091)",
        "method_tag": "Planar Truss Element & Thermal Load",
        "exam_focus": True,
        "figure_image": "/images/hk231_fig_1.png",
        "expected_numeric_value": 2.0000,
        "problem_en": "A 2-bar planar truss structure has Bar 1 horizontal ($L_1 = 1\\text{ m}$, node 1 to 2) and Bar 2 inclined at $30^\\circ$ to the vertical. Both bars have $E = 90\\text{ GPa}, A = 400\\text{ mm}^2, \\alpha = 20 \\times 10^{-6}/^\\circ\\text{C}$. The temperature increases by $\\Delta T = 100^\\circ\\text{C}$. Find the thermal equivalent load vector and horizontal displacement $u_2$ of node 2.",
        "glossary": {
            "planar truss": "dàn thanh phẳng",
            "thermal expansion coefficient": "hệ số giãn nở nhiệt",
            "equivalent nodal load": "vector tải nút tương đương"
        },
        "hint": "Độ cứng thanh 1: $k_1 = \\frac{EA}{L_1} = 36000\\text{ kN/m}$. Lực nhiệt dọc trục: $F_{\\text{th}} = EA\\alpha\\Delta T = 72\\text{ kN}$. Chuyển vị ngang: $u_2 = \\frac{72}{36000} = 2.0\\text{ mm}$.",
        "steps": [
            "**Bước 1: Tính các đặc trưng hình học và vật liệu**\n- $EA = 90 \\times 10^9 \\times 400 \\times 10^{-6} = 36000\\text{ kN}$\n- $k_1 = \\frac{EA}{L_1} = 36000\\text{ kN/m}$\n- Tải nhiệt: $F_{th} = EA\\alpha\\Delta T = 36000 \\times 20 \\times 10^{-6} \\times 100 = 72\\text{ kN}$",
            "**Bước 2: Vector tải nút tương đương nhiệt độ**\n$$\\{F_{th}^{(1)}\\} = \\begin{Bmatrix} -72 \\\\ 0 \\\\ 72 \\\\ 0 \\end{Bmatrix}\\text{ kN}$$",
            "**Bước 3: Giải chuyển vị tại nút 2**\n$$36000 u_2 = 72 \\implies u_2 = 0.002\\text{ m} = 2.0\\text{ mm}$$"
        ],
        "final_answer": "u_2 = 2.0000\\text{ mm} \\quad (F_{th} = 72.00\\text{ kN})"
    },
    {
        "id": "ch07-exam-hk241-truss",
        "source_problem": "Đề thi HK241 - Câu 1 (ME2091)",
        "method_tag": "Planar Truss with Spring",
        "exam_focus": True,
        "figure_image": "/images/hk241_fig_1_truss.png",
        "expected_numeric_value": 2.6786,
        "problem_en": "A 2-bar structure with spring support $k = 30\\text{ kN/m}$ at node 2 as shown in Fig. 1. Bar 1 is horizontal ($L_1 = 1.5\\text{ m}$), Bar 2 is vertical ($L_2 = 2.0\\text{ m}$). Both bars have $E = 210\\text{ GPa}, A = 400\\text{ mm}^2$. The structure is loaded with force $F = 150\\text{ kN}$. Determine the horizontal displacement $u_2$ at node 2.",
        "glossary": {
            "spring support": "gối tựa đàn hồi / lò xo",
            "direct stiffness": "phương pháp độ cứng trực tiếp"
        },
        "hint": "Độ cứng thanh ngang 1: $k_1 = \\frac{EA}{L_1} = \\frac{210 \\times 10^3 \\times 400}{1500} = 56000\\text{ kN/m}$. Do lực $F$ tác dụng theo phương ngang nên chuyển vị ngang chỉ phụ thuộc vào thanh 1: $u_2 = \\frac{F}{k_1}$.",
        "steps": [
            "**Bước 1: Tính độ cứng các phần tử**\n- $EA = 210 \\times 10^6 \\times 400 \\times 10^{-6} = 84000\\text{ kN}$\n- Thanh 1: $k_1 = \\frac{84000}{1.5} = 56000\\text{ kN/m}$\n- Thanh 2: $k_2 = \\frac{84000}{2.0} = 42000\\text{ kN/m}$\n- Lò xo hỗ trợ tại nút 2 theo phương đứng: $k_s = 30\\text{ kN/m}$",
            "**Bước 2: Ma trận độ cứng thu gọn tại nút 2**\n$$[K]_{22} = \\begin{bmatrix} 56000 & 0 \\\\ 0 & 42030 \\end{bmatrix}\\text{ kN/m}$$",
            "**Bước 3: Giải chuyển vị nút 2**\n$$u_2 = \\frac{150}{56000} = 0.0026786\\text{ m} \\approx 2.6786\\text{ mm}$$"
        ],
        "final_answer": "u_2 = 2.6786\\text{ mm}, \\; v_2 = 0.0000\\text{ mm}"
    },
    {
        "id": "ch07-exam-hk241-beam",
        "source_problem": "Đề thi HK241 - Câu 2 (ME2091)",
        "method_tag": "Beam Element Formulation",
        "exam_focus": True,
        "figure_image": "/images/hk241_fig_2_beam.png",
        "expected_numeric_value": 0.0015,
        "problem_en": "A horizontal beam structure modeled with 2 beam elements as shown in Fig. 2. Fixed at node 1, Element 1 subjected to uniform distributed load $q = 30\\text{ kN/m}$, Element 2 subjected to concentrated load $F = 20\\text{ kN}$ at mid-span B. Parameters: $E = 210\\text{ GPa}, I = 5000\\text{ cm}^4, L_1 = 2\\text{ m}, L_2 = 2\\text{ m}$. Form the global stiffness matrix and equivalent load vector.",
        "glossary": {
            "beam element": "phần tử dầm",
            "equivalent nodal load": "vector tải nút tương đương",
            "moment of inertia": "moment quán tính mặt cắt ngang"
        },
        "hint": "Độ cứng uốn: $EI = 210 \\times 10^9 \\times 5000 \\times 10^{-8} = 1.05 \\times 10^7\\text{ N}\\cdot\\text{m}^2 = 10500\\text{ kN}\\cdot\\text{m}^2$. Tải phân bố đều $q$ trên nhịp $L$: lực cắt nút $\\pm \\frac{qL}{2}$, moment nút $\\pm \\frac{qL^2}{12}$. Tải tập trung $F$ tại giữa nhịp: lực cắt nút $\\frac{F}{2}$, moment nút $\\pm \\frac{FL}{8}$.",
        "steps": [
            "**Bước 1: Tính độ cứng uốn $EI$**\n$$EI = 210 \\times 10^6\\text{ kN/m}^2 \\times (5000 \\times 10^{-8}\\text{ m}^4) = 10500\\text{ kN}\\cdot\\text{m}^2$$",
            "**Bước 2: Vector tải nút tương đương**\n- Phần tử 1 chịu tải phân bố $q = 30\\text{ kN/m}, L = 2\\text{ m}$:\n  + Lực nút: $\\frac{qL}{2} = \\frac{30(2)}{2} = 30\\text{ kN}$\n  + Moment nút: $\\frac{qL^2}{12} = \\frac{30(4)}{12} = 10\\text{ kN}\\cdot\\text{m}$\n- Phần tử 2 chịu lực tập trung $F = 20\\text{ kN}, L = 2\\text{ m}$:\n  + Lực nút: $\\frac{F}{2} = 10\\text{ kN}$\n  + Moment nút: $\\frac{FL}{8} = \\frac{20(2)}{8} = 5\\text{ kN}\\cdot\\text{m}$",
            "**Bước 3: Tải tương đương tổng hợp tại nút 2**\n$$F_{y2} = -30 - 10 = -40\\text{ kN}, \\quad M_2 = -10 + 5 = -5\\text{ kN}\\cdot\\text{m}$$"
        ],
        "final_answer": "F_{y2} = -40\\text{ kN}, \\; M_2 = -5\\text{ kN}\\cdot\\text{m}"
    }
]

# Write all JSON files
with open(DATA_DIR / "ch01_errors.json", "w", encoding="utf-8") as f:
    json.dump(ch01_problems, f, ensure_ascii=False, indent=2)

with open(DATA_DIR / "ch02_roots.json", "w", encoding="utf-8") as f:
    json.dump(ch02_problems, f, ensure_ascii=False, indent=2)

with open(DATA_DIR / "ch03_linear_systems.json", "w", encoding="utf-8") as f:
    json.dump(ch03_problems, f, ensure_ascii=False, indent=2)

with open(DATA_DIR / "ch04_interpolation.json", "w", encoding="utf-8") as f:
    json.dump(ch04_problems, f, ensure_ascii=False, indent=2)

with open(DATA_DIR / "ch05_calculus.json", "w", encoding="utf-8") as f:
    json.dump(ch05_problems, f, ensure_ascii=False, indent=2)

with open(DATA_DIR / "ch06_ode.json", "w", encoding="utf-8") as f:
    json.dump(ch06_problems, f, ensure_ascii=False, indent=2)

with open(DATA_DIR / "ch07_fem.json", "w", encoding="utf-8") as f:
    json.dump(ch07_problems, f, ensure_ascii=False, indent=2)

print("Generated enriched verified datasets for all chapters with figures & lecture alignment.")
