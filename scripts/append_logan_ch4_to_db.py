"""Generate verified, worked Logan 5e beam exercises and upsert them by ID."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import tempfile

import numpy as np

from logan_ch4_beam import numeric_models, unit_responses
from verify_logan_ch4 import verify_all

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "ch07_fem.json"
GLOSSARY = {
    "beam deflection": "độ võng của dầm",
    "slope": "góc xoay (độ dốc đường đàn hồi)",
    "shear force": "lực cắt",
    "bending moment": "mô men uốn",
    "fixed-end moment": "mô men ngàm do tải tác dụng khi khóa hai đầu phần tử",
    "flexural rigidity": "độ cứng chống uốn",
    "equivalent nodal load": "tải nút tương đương",
    "support reaction": "phản lực gối tựa",
    "spring stiffness": "độ cứng lò xo",
    "extreme-fiber stress": "ứng suất tại thớ biên",
}
STIFFNESS = (r"k_e=\frac{E I_e}{\ell^3}\begin{bmatrix}"
             r"12&6\ell&-12&6\ell\\6\ell&4\ell^2&-6\ell&2\ell^2\\"
             r"-12&-6\ell&12&-6\ell\\6\ell&2\ell^2&-6\ell&4\ell^2\end{bmatrix}")
LOAD = r"f_e=\int_0^\ell N^Tq(x)\,dx+\sum_j N(x_j)^T P_j"
HINT = ("Dùng phần tử Euler–Bernoulli theo thứ tự $[v_i,\\theta_i,v_j,\\theta_j]^T$. "
        f"$${STIFFNESS}$$ Tải tương đương theo công ảo: $${LOAD}$$")
SIGN = r"Quy ước $v,q,R,V$ theo dấu lực/chuyển vị đứng (lên là dương), $\theta$ và ngẫu lực nút dương ngược chiều kim đồng hồ."
THREE = ("**Bước 1: Ma trận độ cứng và tải tương đương**",
         "**Bước 2: Ghép nối và khử điều kiện biên**",
         "**Bước 3: Chuyển vị, góc xoay và phản lực**")
NODAL = "Find the nodal deflections and slopes, all element end actions, and the support reactions."
DRAW = " Draw the shear-force and bending-moment diagrams."
UNITS = {"m": r"\mathrm{m}", "in": r"\mathrm{in}", "kN": r"\mathrm{kN}", "kip": r"\mathrm{kip}"}

PROBLEMS = {
    9: NODAL + DRAW + r" The supports are at $x=0,3,7,10\,\mathrm{m}$, and an $8\,\mathrm{kN}$ downward load acts at $x=5\,\mathrm{m}$. Use $E=70\,\mathrm{GPa}$ and $I=1\times10^{-4}\,\mathrm{m^4}$.",
    10: NODAL + DRAW + r" The $20\,\mathrm{ft}$ cantilever carries a downward tip load of $2\,\mathrm{kip}$ and has a grounded tip spring of stiffness $1000\,\mathrm{lb/in}$. Use $E=29\times10^6\,\mathrm{psi}$ and $I=200\,\mathrm{in^4}$.",
    11: NODAL + DRAW + r" The simply supported beam has two $4\,\mathrm{m}$ half-spans. A grounded spring of stiffness $200\,\mathrm{kN/m}$ and a downward load of $12\,\mathrm{kN}$ act at midspan. Use $E=70\,\mathrm{GPa}$ and $I=2\times10^{-4}\,\mathrm{m^4}$.",
    12: r"A fixed–fixed beam of length $L$ carries a uniform downward load $w$. The middle third has rigidity $2EI$, while the end thirds have rigidity $EI$. Find the midspan deflection and support reactions." + DRAW,
    13: r"A fixed–fixed beam has span $L$, constant rigidity $EI$, and a uniform downward load $w$. Compute the midspan deflection and reactions, and compare with the classical solution using Appendix D." + DRAW,
    14: r"A simply supported beam of span $L$ and constant rigidity $EI$ carries a uniform downward load $w$. Calculate its midspan deflection and reactions." + DRAW,
    15: r"A beam is fixed at $A$, rests on a roller at $B$, and overhangs to $C$, with $AB=BC=L$. A uniform downward load $w$ acts only on $BC$. For constant $EI$, find the free-end deflection and support reactions." + DRAW,
    16: r"Apply work equivalence to replace a downward load increasing linearly from zero at $A$ to $w$ at $B$ over a beam element of length $L$. Determine the equivalent transverse nodal forces and nodal moments.",
    18: r"A beam of span $L$ and constant $EI$ is fixed at $A$ and roller-supported at $B$. The downward load increases linearly from zero at $A$ to $w$ at $B$. Find the rotation at $B$ and the support reactions.",
    19: NODAL + r" Node $1$ is fixed, node $2$ is roller-supported, and node $3$ is free. Each span is $4\,\mathrm{m}$; only the overhang carries a uniform downward load of $8\,\mathrm{kN/m}$. Use $E=70\,\mathrm{GPa}$ and $I=3\times10^{-4}\,\mathrm{m^4}$.",
    20: NODAL + r" The pin and roller are $12\,\mathrm{m}$ apart. The downward line load is $10\,\mathrm{kN/m}$ at each end and zero at midspan, where a grounded spring has stiffness $10\,\mathrm{kN/m}$. Use $E=210\,\mathrm{GPa}$ and $I=4\times10^{-4}\,\mathrm{m^4}$.",
    21: NODAL + r" The left end is fixed and the right end is pinned. The $30\,\mathrm{ft}$ beam carries a uniform downward load of $2000\,\mathrm{lb/ft}$ and has a node at midspan. Use $E=29\times10^6\,\mathrm{psi}$ and $I=200\,\mathrm{in^4}$.",
    22: NODAL + r" The beam is fixed at node $1$, pinned at node $2$, and free at node $3$. Each span is $10\,\mathrm{ft}$. The downward load grows linearly from zero at node $1$ to $4000\,\mathrm{lb/ft}$ at node $3$. Use $E=29\times10^6\,\mathrm{psi}$ and $I=150\,\mathrm{in^4}$.",
    23: NODAL + r" The fixed ends are $40\,\mathrm{ft}$ apart, the downward load is $500\,\mathrm{lb/ft}$, and the grounded center spring has stiffness $4000\,\mathrm{lb/in}$. Use $E=1.6\times10^6\,\mathrm{psi}$ and $I=100\,\mathrm{in^4}$.",
    26: r"Find the maximum deflection magnitude and the maximum bending stress magnitude for the continuous beam supported at $A,B,C$. The downward load is $30\,\mathrm{kN/m}$ throughout; $AB=10\,\mathrm{m}$ has inertia $I$ and $BC=20\,\mathrm{m}$ has inertia $2I$. Use $c=0.25\,\mathrm{m}$, $I=500\times10^{-6}\,\mathrm{m^4}$, and $E=200\,\mathrm{GPa}$.",
    27: r"Find the maximum deflection magnitude and the maximum bending stress magnitude for the beam supported at $A,C,D$. The $30\,\mathrm{ft}$ span $AC$ has inertia $3I$ and a downward $75\,\mathrm{kip}$ load at its midpoint $B$. The $30\,\mathrm{ft}$ span $CD$ has inertia $I$ and a uniform downward load of $2\,\mathrm{kip/ft}$. Use $E=30\times10^6\,\mathrm{psi}$, $I=500\,\mathrm{in^4}$, and $c=10\,\mathrm{in}$.",
    37: r"A fixed–fixed beam of span $L$ and constant $EI$ carries a downward point load $P$ at midspan and a uniform downward load $w$ over the entire span. Find the midspan deflection and support reactions.",
    38: r"A fixed–fixed beam of span $L$ and constant $EI$ carries two downward forces $P$ at $x=L/3$ and $x=2L/3$. Use equivalent nodal loads to calculate the midspan deflection.",
    39: r"A cantilever of span $L$ and constant $EI$ carries a downward point load $P$ at $x=L/2$ and a triangular downward load that grows from zero at the clamp to $w$ at the tip. By equivalent load replacement, find the tip deflection, tip rotation, and support reactions.",
}

NOTES = {
    9: r"PDF tr. 799: khớp $v_3,\theta_2,\theta_1,R_1,R_2$ đến độ chính xác in. $R_1=R_5<0$ giả thiết gối ngoài giữ được dầm theo hai chiều; nếu chỉ tựa một chiều thì cần giải lại bài toán nhấc gối.",
    10: r"PDF tr. 799: độ võng, góc xoay và lực đứng ngàm khớp trong khoảng $0.11\%$. Sách in mô men âm, nhưng cân bằng quanh ngàm cho $M_1=(2-R_2)(240\,\mathrm{in})>0$: mô men phản lực ngược chiều kim đồng hồ; mô men uốn trong tiết diện sát ngàm âm.",
    11: r"PDF tr. 799: độ võng, góc xoay và lực lò xo khớp. Sách in $5.208\,\mathrm{kN}$ tại mỗi gối ngoài; cân bằng cho $(12-1.58678)/2\approx5.20661\,\mathrm{kN}$.",
    12: r"PDF tr. 799: khớp độ võng và góc xoay ở hai nút đổi tiết diện. Giá trị giữa nhịp in với mẫu số $507$ là xấp xỉ (sai khác $0.0801\%$). Sách ghi $M_1=wL^2/12$; điều kiện đối xứng $\int_0^{L/2}M(x)/(EI(x))\,dx=0$, với $EI(x)$ đổi tại $L/3$, cho $M_1=41wL^2/540$.",
    13: r"PDF tr. 799 và nghiệm dầm ngàm hai đầu khớp. Dùng một phần tử cho cả nhịp thì tải nút theo Phụ lục D là $[-wL/2,-wL^2/12,-wL/2,wL^2/12]^T$; phản lực là đối của véc-tơ này. Thêm nút giữa nhịp để tính $v_2$.",
    14: "PDF tr. 799: khớp độ võng giữa nhịp, góc xoay ở hai gối và phản lực.",
    15: "PDF tr. 799: khớp độ võng đầu tự do, hai góc xoay và các phản lực.",
    18: "PDF tr. 799: khớp góc xoay đầu phải và ba thành phần phản lực.",
    19: "PDF tr. 799: khớp chuyển vị, góc xoay, phản lực và nội lực đầu phần tử được liệt kê.",
    20: "PDF tr. 800: khớp chuyển vị, góc xoay, phản lực và bốn nội lực đầu phần tử thứ nhất đến độ chính xác in.",
    21: r"PDF tr. 800: khớp độ võng, góc xoay và phản lực đứng. Đáp án in $225\,\mathrm{kip\cdot in}$, nhưng cân bằng cho $M_1=60(15)-22.5(30)=225\,\mathrm{kip\cdot ft}=2700\,\mathrm{kip\cdot in}$.",
    22: "PDF tr. 800: khớp chuyển vị, góc xoay và phản lực sau khi đổi đơn vị mô men.",
    23: "PDF tr. 800: khớp chuyển vị và phản lực ngàm đến độ chính xác in. Phản lực đứng của lò xo được tính thêm từ độ võng nút giữa.",
    26: r"PDF tr. 800: tại trung điểm $BC$, $v=-0.1953125\,\mathrm{m}$ khớp giá trị in. Đó không phải cực trị vì $\theta\ne0$ tại đó; nghiệm cực trị nằm xa hơn về phía $C$. Ứng suất thớ dưới tại $B^-$ là $-468.75\,\mathrm{MPa}$, khớp $-469\,\mathrm{MPa}$ trong sách.",
    27: r"PDF tr. 800: $v_B\approx-1.028\,\mathrm{in}$ và các cực trị ứng suất thớ dưới khớp khi làm tròn. Dòng đáp án ghi tải $7.5\,\mathrm{kip}$, nhưng hình ghi $75\,\mathrm{kip}$; dùng $75\,\mathrm{kip}$. Nghiệm $\theta=0$ nằm hơi lệch về phía $A$ so với $B$.",
    37: "PDF tr. 800: khớp độ võng giữa nhịp và các phản lực được liệt kê.",
    38: "PDF tr. 800: khớp độ võng giữa nhịp.",
    39: "PDF tr. 800: khớp độ võng, góc xoay đầu tự do và phản lực ngàm.",
}

MODEL = {
    9: r"Mô hình bốn phần tử dài $3,2,2,3\,\mathrm{m}$; đặt lực đứng $-8\,\mathrm{kN}$ tại nút $3$.",
    10: r"Đổi $20\,\mathrm{ft}=240\,\mathrm{in}$ và $k_s=1\,\mathrm{kip/in}$. Đặt lực $-2\,\mathrm{kip}$ tại nút $2$.",
    11: r"Hai phần tử dài $4\,\mathrm{m}$; đặt $-12\,\mathrm{kN}$ tại nút $2$. Lò xo thẳng đứng có $k_s=200\,\mathrm{kN/m}$.",
    12: r"Chia tại $x=L/3,L/2,2L/3$. Các phần tử theo thứ tự có độ cứng chống uốn $EI,2EI,2EI,EI$; tải đứng không đổi $q=-w$.",
    13: r"Đặt nút $2$ tại giữa nhịp; hai phần tử đều dài $L/2$ và có tải $q=-w$.",
    14: r"Hai phần tử dài $L/2$ đều chịu tải $q=-w$; giữ tự do góc xoay ở hai gối.",
    15: r"Dùng phần tử $AB$ không tải và phần tử $BC$ có $q=-w$, cùng chiều dài $L$.",
    18: r"Dùng một phần tử, $q=-wx/L$. Véc-tơ tải của phần tử được tính như bài 4.16.",
    19: r"Chỉ phần tử thứ hai mang tải $q=-8\,\mathrm{kN/m}$ trên đoạn dài $4\,\mathrm{m}$.",
    20: r"Tải phần tử thứ nhất biến thiên từ $-10$ đến $0\,\mathrm{kN/m}$, phần tử thứ hai từ $0$ đến $-10\,\mathrm{kN/m}$. Gắn lò xo $k_s=10\,\mathrm{kN/m}$ vào nút $2$.",
    21: r"Hai phần tử dài $180\,\mathrm{in}$; tải đứng $q=-2/12\,\mathrm{kip/in}$.",
    22: r"Hai phần tử dài $120\,\mathrm{in}$, tải tại các nút lần lượt là $0,-2/12,-4/12\,\mathrm{kip/in}$ (cường độ tải đường, không phải lực nút).",
    23: r"Hai phần tử dài $240\,\mathrm{in}$; $q=-0.5/12\,\mathrm{kip/in}$ và $k_s=4\,\mathrm{kip/in}$ tại nút $2$.",
    26: r"Dùng phần tử $AB$ và $BC$, độ cứng lần lượt $EI$ và $2EI$. Cường độ tải đứng $q=-30\,\mathrm{kN/m}$ ở cả hai phần tử.",
    27: r"Chia tại $B$ để đặt trực tiếp lực đứng $-75\,\mathrm{kip}$. Các phần tử $AB,BC,CD$ có chiều dài $180,180,360\,\mathrm{in}$ và độ cứng chống uốn $3EI,3EI,EI$; chỉ $CD$ chịu tải đường.",
    37: r"Chia tại giữa nhịp. Đặt $-P$ vào phương trình chuyển vị của nút $2$; tính tải đường $q=-w$ cho cả hai phần tử.",
    38: r"Chia tại giữa nhịp; tải trong phần tử bên trái ở $\xi=2/3$, bên phải ở $\xi=1/3$. Với $\xi=x/\ell$ tính từ đầu trái từng phần tử, thay mỗi lực bằng $-P N(\xi)^T$.",
    39: r"Dùng một phần tử với $q=-wx/L$ và lực nằm trong phần tử. Tải tập trung đóng góp $-P N(1/2)^T=[-P/2,-PL/8,-P/2,PL/8]^T$.",
}

IMPERIAL = {10, 21, 22, 23, 27}
DIAGRAMS = {9, 10, 11, 12, 13, 14, 15}
SPRING_GROUND = {10: 3, 11: 4, 20: 4, 23: 4}
TARGET_DOF = {9: 4, 10: 2, 11: 2, 12: 4, 13: 2, 14: 2, 15: 4, 18: 3, 19: 4, 20: 2,
              21: 2, 22: 4, 23: 2, 37: 2, 38: 2, 39: 2}
NAMES = {26: ("A", "B", "C"), 27: ("A", "B", "C", "D")}


def tex_number(value, final=False):
    if abs(value) < 1e-12:
        return "0"
    if final:
        text = f"{value:.4f}" if abs(value) >= .01 else f"{value:.4e}"
    else:
        text = f"{value:.6g}"
    if "e" in text:
        mantissa, exponent = text.split("e")
        return rf"{mantissa}\times10^{{{int(exponent)}}}"
    return text


def symbolic(w, p, w_unit, p_unit):
    result = ""
    for value, unit in ((p, p_unit), (w, w_unit)):
        if abs(value) < 1e-12:
            continue
        f = Fraction(abs(float(value))).limit_denominator(1_000_000)
        sign = ("-" if value < 0 else ("+" if result else ""))
        # Split the coefficient and symbols between numerator and denominator.
        num, _, den = unit.partition("/")
        a = ("" if f.numerator == 1 and num else str(f.numerator)) + num
        b = ("" if f.denominator == 1 else str(f.denominator)) + den
        result += sign + (rf"\frac{{{a}}}{{{b}}}" if b else a)
    return result or "0"


def table(headings, rows):
    return "\n".join("| " + " | ".join(row) + " |"
                     for row in [headings, [":---:"]*len(headings), *rows])


def math(value):
    return f"${value}$"


def vector(values):
    return "[" + ",\\,".join(values) + "]^T"


def matrix(rows):
    return r"\begin{bmatrix}" + r"\\".join("&".join(row) for row in rows) + r"\end{bmatrix}"


def dof_label(dof, names):
    return (r"\theta" if dof % 2 else "v") + f"_{{{names[dof//2]}}}"


def problem_16():
    load = r"\left[-\frac{3wL}{20},-\frac{wL^2}{30},-\frac{7wL}{20},\frac{wL^2}{20}\right]^T"
    return [
        f"{THREE[0]}\n{SIGN} Dùng hàm dạng Hermite với $\\xi=x/L$:\n"
        r"$$N=[1-3\xi^2+2\xi^3,\ L(\xi-2\xi^2+\xi^3),\ 3\xi^2-2\xi^3,\ L(-\xi^2+\xi^3)].$$",
        f"{THREE[1]}\nBài này chỉ quy đổi tải trên một phần tử: không có gối, không ghép hệ và không áp điều kiện biên.\n"
        r"$$\delta W=\delta d_e^T f_e=\int_0^L\delta v\,q\,dx,\qquad f_e=-wL\int_0^1 N^T\xi\,d\xi.$$",
        "**Bước 3: Lực và mô men nút tương đương**\n"
        f"$$f_e={load}.$$\n"
        r"Kiểm tra: $F_A+F_B=-wL/2$ và $M_A+M_B+L F_B=-wL^2/3$, đúng với hợp lực tam giác đặt tại $2L/3$ từ $A$. Cả bốn thành phần khớp đáp án PDF tr. 799.",
    ], f"f_e={load}", None


def structural_problem(n, numerical):
    is_numeric = n in numerical
    if is_numeric:
        model = numerical[n]
        sol = model.solve()
    else:
        model, uniform, point = unit_responses(n)
        sol = uniform
    span_count = len(model.spans)
    names = NAMES.get(n, tuple(str(i) for i in range(1, span_count+2)))
    length_unit, force_unit = (("in", "kip") if n in IMPERIAL else ("m", "kN"))
    lu, fu = UNITS[length_unit], UNITS[force_unit]
    mu = fu + r"\cdot" + lu
    fixed_names = vector([dof_label(i, names) for i in sorted(model.fixed)])
    d_expr, r_expr = [], []
    for i in range(len(sol.d)):
        if is_numeric:
            d_expr.append(tex_number(sol.d[i], final=True))
            r_expr.append(tex_number(sol.reactions[i], final=True))
        else:
            d_expr.append(symbolic(uniform.d[i], point.d[i],
                                   "wL^3/EI" if i % 2 else "wL^4/EI",
                                   "PL^2/EI" if i % 2 else "PL^3/EI"))
            r_expr.append(symbolic(uniform.reactions[i], point.reactions[i],
                                   "wL^2" if i % 2 else "wL", "PL" if i % 2 else "P"))

    rows_load, rows_end = [], []
    for e, span in enumerate(model.spans):
        name = f"{names[e]}–{names[e+1]}"
        if is_numeric:
            length_tex = tex_number(span.length) + r"\," + lu
            load = [tex_number(a) for a in span.load()]
            end = [tex_number(a, final=True) for a in sol.end_actions[e]]
        else:
            length_tex = symbolic(span.length, 0, "L", "")
            w_load, p_load = uniform.model.spans[e].load(), point.model.spans[e].load()
            w_end, p_end = uniform.end_actions[e], point.end_actions[e]
            load, end = [[symbolic(a, b, "wL^2" if j % 2 else "wL", "PL" if j % 2 else "P")
                          for j, (a, b) in enumerate(zip(wv, pv))]
                         for wv, pv in [(w_load, p_load), (w_end, p_end)]]
        rows_load.append([name, math(length_tex), math(vector(load))])
        rows_end.append([name, *(math(x) for x in end)])

    if n in SPRING_GROUND:
        i, ks = model.springs[0]
        end = ks*sol.d[i]
        rows_end.append([f"{names[i//2]}–{SPRING_GROUND[n]} (lò xo)", math(tex_number(end, True)), "$0$",
                         math(tex_number(-end, True)), "$0$"])
    unit_note = f"Dùng {math(lu)} và {math(fu)}; mô men tính bằng {math(mu)}." if is_numeric else ""
    step1 = "\n".join([THREE[0], SIGN, MODEL[n], unit_note,
                       f"$${STIFFNESS},\\qquad {LOAD}.$$",
                       table(["Phần tử", r"$\ell$", "Véc-tơ tải tương đương"], rows_load)])

    free_names = vector([dof_label(i, names) for i in sol.free])
    sub = sol.k[np.ix_(sol.free, sol.free)]
    if is_numeric:
        reduced = (matrix([[tex_number(a) for a in row] for row in sub]) +
                   r"\,d_f=" + matrix([[tex_number(sol.f[i])] for i in sol.free]))
        scaling = "Hệ rút gọn dưới đây làm tròn để trình bày; nghiệm dùng các hệ số chưa làm tròn."
    else:
        r = lambda x: symbolic(x, 0, "", "")
        reduced = (matrix([[r(a) for a in row] for row in sub]) + r"\,\bar d_f=" +
                   matrix([[symbolic(uniform.f[i], point.f[i], "W", "P")] for i in sol.free]))
        scaling = (r"Đặt $W=wL$ và chuẩn hóa $\bar v=EI\,v/L^3$, "
                   r"$\bar\theta=EI\,\theta/L^2$. Đây là hệ theo các ẩn chuẩn hóa.")
    spring_note = (r" Với chân lò xo bất động, cộng $k_s$ vào đường chéo ứng với chuyển vị đứng "
                   f"của nút ${names[model.springs[0][0]//2]}$."
                   if model.springs else "")
    step2 = "\n".join([THREE[1], r"Ghép theo bậc tự do chung, $K=\sum_e A_e^T k_e A_e$ và "
                       r"$F=\sum_e A_e^T f_e+F_{\mathrm{nodal}}$." + spring_note,
                       f"Đặt ${fixed_names}=\\mathbf{{0}}$. Theo thứ tự $d_f={free_names}$, giải $K_{{ff}}d_f=F_f$.",
                       scaling, f"$${reduced}.$$"])

    node_rows = [[f"${name}$", *(math(a) for a in [*d_expr[2*i:2*i+2], *r_expr[2*i:2*i+2]])]
                 for i, name in enumerate(names)]
    suffix = lambda unit: f" ({math(unit)})" if is_numeric else ""
    spring_result = (r" Lực lò xo tác dụng lên dầm là $R_s=-k_s v$; cột $R$ ghi lực này "
                     r"tại nút nối dầm, không lặp lại ở nút nền." if model.springs else "")
    step3 = "\n".join([THREE[2],
                       r"Tính phản lực tại các bậc tự do bị khóa từ $R_c=(Kd-F)_c$, "
                       r"và lực tác dụng lên đầu phần tử từ $s_e=k_ed_e-f_e=[V_i,M_i^{(e)},V_j,M_j^{(e)}]^T$."
                       + spring_result,
                       table(["Nút", "$v$"+suffix(lu), r"$\theta$ (rad)", "$R$"+suffix(fu), "$M_R$"+suffix(mu)], node_rows),
                       table(["Phần tử", "$V_i$"+suffix(fu), "$M_i^{(e)}$"+suffix(mu),
                              "$V_j$"+suffix(fu), "$M_j^{(e)}$"+suffix(mu)], rows_end)])
    if n in DIAGRAMS:
        step3 += ("\nBiểu đồ với mô men võng xuống lấy dương; tọa độ cục bộ bắt đầu ở đầu trái phần tử: "
                  r"$V(x)=V_i+\int_0^x q(s)\,ds$ và $M(x)=-M_i^{(e)}+V_i x+\int_0^x(x-s)q(s)\,ds$."
                  f"\n![Biểu đồ lực cắt và mô men uốn](/images/logan_p4_{n}_shear_moment.svg)")
    if n in (26, 27):
        extra, final, target = design_results(n, sol)
        step3 += "\n" + extra
    else:
        idx = TARGET_DOF[n]
        target = float(sol.d[idx]) if is_numeric else None
        units = r"\," + (r"\mathrm{rad}" if idx % 2 else lu) if is_numeric else ""
        final = f"{dof_label(idx, names)}" + (r"\approx " if is_numeric else "=") + d_expr[idx] + units
        if n == 39:
            final += r",\quad\theta_2=" + d_expr[3]
    step3 += "\nĐối chiếu Answers to Selected Problems (Logan, 5e). " + NOTES[n]
    return [step1, step2, step3], final, target


def design_results(n, sol):
    v, top_over_e = sol.extrema((.25, .25) if n == 26 else (10, 10, 10))
    x_peak, v_peak, _ = max(v, key=lambda x: abs(x[1]))
    e_modulus = 200e3 if n == 26 else 30e6
    unit = r"\mathrm{MPa}" if n == 26 else r"\mathrm{psi}"
    length = UNITS["m" if n == 26 else "in"]
    # Report lower-fiber signs, matching Logan's signed values for these problems.
    bottom = [(x, -s*e_modulus, e) for x, s, e in top_over_e]
    stress_critical = max(bottom, key=lambda x: abs(x[1]))
    first = (r"Trong mỗi phần tử, phục hồi đúng đường đàn hồi từ $EI_e v''=M$, "
             r"tích phân từ đầu trái với $v_i,\theta_i$ đã biết. So sánh giá trị tại hai đầu "
             r"và các nghiệm $\theta(x)=0$. Với $M$ võng xuống dương, tính $\sigma_\mathrm{bot}=Mc/I_e$ ở thớ dưới "
             r"tại hai đầu và tại $V(x)=0$, kiểm tra riêng cả hai phía chỗ đổi $I_e$. "
             r"Thớ trên có ứng suất ngược dấu. Với tải đều có dấu $q$, trên mỗi phần tử dùng "
             r"$M(x)=-M_i^{(e)}+V_i x+q x^2/2$ và "
             r"$v(x)=v_i+\theta_i x+(-M_i^{(e)}x^2/2+V_i x^3/6+q x^4/24)/(EI_e)$.")
    rows = [[f"${tex_number(x, True)}$", f"${tex_number(d, True)}$"] for x, d, _ in sorted(v)]
    # At continuous nodes the same deflection is returned by both adjoining spans.
    rows = [list(row) for row in dict.fromkeys(tuple(row) for row in rows)]
    stress_rows = [
        [names, math(tex_number(x, True)), math(tex_number(s, True))]
        for x, s, e in bottom
        for names in [f"{NAMES[n][e]}–{NAMES[n][e+1]}"]
    ]
    extra = "\n".join([first,
                       table(["$x$ (từ $A$), "+math(length), "$v$, "+math(length)], rows),
                       table(["Phần tử", "$x$, "+math(length), r"$\sigma_\mathrm{bot}$, "+math(unit)], stress_rows),
                       f"Cực trị độ võng ở $x={tex_number(x_peak, True)}\\,{length}$ tính từ $A$; "
                       f"ứng suất trị tuyệt đối lớn nhất trên thớ biên nằm tại "
                       f"$x={tex_number(stress_critical[0], True)}\\,{length}$, "
                       f"phía phần tử {stress_rows[bottom.index(stress_critical)][0]}."])
    final = (rf"v_{{\mathrm{{crit}}}}\approx {tex_number(v_peak, True)}\,{length},\quad "
             rf"\lvert\sigma\rvert_{{\max}}={tex_number(abs(stress_critical[1]), True)}\,{unit}")
    return extra, final, float(v_peak)


def build_entries():
    numeric = numeric_models()
    for n, problem in PROBLEMS.items():
        steps, final, target = problem_16() if n == 16 else structural_problem(n, numeric)
        entry = {
            "id": f"ch07-logan-prob-4.{n}",
            "source_problem": f"Problem 4.{n} - Logan (Chapter 4: Beams)",
            "method_tag": "Beam Element",
            "exam_focus": False,
            "figure_image": f"/images/logan_fig_p4_{n}_beam.png",
            "problem_en": problem,
            "glossary": GLOSSARY,
            "hint": HINT,
            "steps": steps,
            "final_answer": final,  # ExerciseCard supplies its own KaTeX delimiters.
            "expected_numeric_value": target,
        }
        if target is not None:
            variable = (r"v_{\mathrm{crit}}" if n in (26, 27)
                        else dof_label(TARGET_DOF[n], tuple(map(str, range(1, 6)))))
            unit = UNITS["in" if n in IMPERIAL else "m"]
            entry["numeric_target_label"] = f"${variable}$ (đơn vị ${unit}$)"
        yield entry


def upsert(db, entries):
    existing = json.loads(db.read_text(encoding="utf-8"))
    if not isinstance(existing, list) or len({e["id"] for e in existing}) != len(existing):
        raise ValueError("Expected a list of exercises with unique IDs.")
    pending = {e["id"]: e for e in entries}
    combined = [pending.pop(e["id"], e) for e in existing] + list(pending.values())
    output = json.dumps(combined, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                     dir=db.parent, delete=False) as out:
        temporary = Path(out.name)
        try:
            out.write(output)
            out.close()
            temporary.replace(db)
        finally:
            temporary.unlink(missing_ok=True)
    return len(combined)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    verify_all()
    from draw_logan_ch4_diagrams import draw_diagrams
    draw_diagrams(ROOT / "public" / "images", DIAGRAMS)
    entries = list(build_entries())
    total = upsert(args.db, entries)
    print(f"Updated {len(entries)} Logan beam exercises. Total in {args.db.name}: {total}")


if __name__ == "__main__":
    main()
