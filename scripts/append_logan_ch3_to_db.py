"""Verify, generate and upsert the selected Logan 5e Chapter 3 exercise cards."""

import argparse
import json
from pathlib import Path
import tempfile

import numpy as np

from logan_ch3_axial import SELECTED
from verify_logan_ch3 import BOOK, reference_value, verify_all

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "ch07_fem.json"
ID = "ch07-logan-prob-3."

BAR_TASK = ("Use the direct stiffness method to find the nodal displacements, "
            "axial forces and reactions. ")
INCLINED_TASK = (r"Compute the nodal displacements and bar stresses for the truss with inclined supports. "
                 r"Use $E=30\times10^6\,\mathrm{psi}$, $A=2\,\mathrm{in^2}$ and $L=30\,\mathrm{in}$. ")
STATEMENTS = {
    "2": BAR_TASK + r"Node $1$ is fixed and a $5\,\mathrm{kN}$ load acts to the left at node $3$. Both segments are $1\,\mathrm{m}$ long, with $E=210\,\mathrm{GPa}$ and $A=4\times10^{-4}\,\mathrm{m^2}$.",
    "3": BAR_TASK + r"Nodes $1$ and $3$ are fixed. The spans are $20\,\mathrm{in}$ and $50\,\mathrm{in}$ from left to right. A load of $8000\,\mathrm{lb}$ acts to the right at node $2$. Use $E=30\times10^6\,\mathrm{psi}$ and $A=2\,\mathrm{in^2}$.",
    "4": BAR_TASK + r"Three $30\,\mathrm{in}$ bars connect fixed nodes $1$ and $4$. Node $2$ carries $4000\,\mathrm{lb}$ to the right and node $3$ carries $10000\,\mathrm{lb}$ to the left. Use $E=30\times10^6\,\mathrm{psi}$ and $A=4\,\mathrm{in^2}$.",
    "5": BAR_TASK + r"Two $30\,\mathrm{in}$ bars of area $A=5\,\mathrm{in^2}$ have moduli $E_1=30\times10^6\,\mathrm{psi}$ and $E_2=15\times10^6\,\mathrm{psi}$, respectively. Node $1$ is fixed and node $3$ carries $15000\,\mathrm{lb}$ to the right.",
    "7": BAR_TASK + r"Nodes $1$ and $4$ are fixed. Bars $1$–$2$ and $3$–$4$ each have $L=30\,\mathrm{in}$, $E=15\times10^6\,\mathrm{psi}$ and $A=3\,\mathrm{in^2}$. A spring of stiffness $k=5000\,\mathrm{lb/in}$ connects nodes $2$ and $3$, and node $3$ carries $10000\,\mathrm{lb}$ to the right.",
    "8": BAR_TASK + r"The steel and aluminum segments each measure $1\,\mathrm{m}$. For steel, $E=200\,\mathrm{GPa}$ and $A=4\times10^{-4}\,\mathrm{m^2}$; for aluminum, $E=70\,\mathrm{GPa}$ and $A=2\times10^{-4}\,\mathrm{m^2}$. Node $1$ is fixed and node $3$ carries $20\,\mathrm{kN}$ to the left.",
    "9": BAR_TASK + r"Node $1$ is fixed, node $2$ carries $10\,\mathrm{kN}$ to the left, and the unknown rightward force $F_3$ causes $u_3=25\,\mathrm{mm}$. The two $2\,\mathrm{m}$ bars have $E=210\,\mathrm{GPa}$ and $A=4\times10^{-4}\,\mathrm{m^2}$.",
    "10": BAR_TASK + r"Nodes $1$ and $4$ are fixed. The two consecutive $2\,\mathrm{m}$ bars have $E=70\,\mathrm{GPa}$ and $A=2\times10^{-4}\,\mathrm{m^2}$. A spring with $k=2000\,\mathrm{kN/m}$ connects nodes $3$ and $4$. Node $2$ carries $8\,\mathrm{kN}$ to the right.",
    "20": r"Find the displacement of node $2$ and the stress in member $1$ by the stiffness method. The two members slope at $45^\circ$ to the horizontal, each with horizontal projection $L=100\,\mathrm{in}$. Use $A=5\,\mathrm{in^2}$, $E=10^6\,\mathrm{psi}$ and the upward load of $10\,\mathrm{kip}$ shown at node $2$.",
    "22": r"Find both displacement components at node $1$ and the stress in each member, then check equilibrium at node $1$. The three members reach fixed joints on the same wall, a horizontal distance $L=100\,\mathrm{in}$ away, at angles of $60^\circ$ above, $0^\circ$, and $30^\circ$ below the leftward horizontal. Use $A=1\,\mathrm{in^2}$, $E=10\times10^6\,\mathrm{psi}$ and rightward and upward loads of $1000\,\mathrm{lb}$ each.",
    "23": r"Find the horizontal and vertical displacements at the apex (node $1$) and the stress in member $1$. The equilateral truss has $L=100\,\mathrm{in}$, $A=1\,\mathrm{in^2}$ and $E=10\times10^6\,\mathrm{psi}$. The apex load is $12000\,\mathrm{lb}$ to the right.",
    "24": r"Find the nodal displacements and member forces for the six-member truss, with fixed nodes $1$ and $4$. The rectangle is $20\,\mathrm{ft}$ wide and $15\,\mathrm{ft}$ high, and each of nodes $2$ and $3$ carries $1000\,\mathrm{lb}$ upward. Use a common axial rigidity $EA$; the diagonals are not joined at their crossing.",
    "27": r"Find both displacement components at node $3$ and the three member forces, and verify equilibrium of node $3$. The lower members have horizontal and vertical projections of $30\,\mathrm{ft}$ and $40\,\mathrm{ft}$, respectively; the upper vertical member is $20\,\mathrm{ft}$ long. Use $A=3\,\mathrm{in^2}$, $E=30\times10^6\,\mathrm{psi}$ and node-$3$ loads of $5\,\mathrm{kip}$ rightward and $10\,\mathrm{kip}$ downward.",
    "29": r"Find both displacement components at node $1$ and each member stress. The three $3\,\mathrm{m}$ members run upward, upward-right at $45^\circ$ and rightward, in element order. Use $E=210\,\mathrm{GPa}$, $A=4\times10^{-4}\,\mathrm{m^2}$ and node-$1$ loads of $10\,\mathrm{kN}$ leftward and $20\,\mathrm{kN}$ downward.",
    "30": r"Find both displacement components at node $1$ and each member stress. The $2\,\mathrm{m}$ member runs upward, the $3\,\mathrm{m}$ member runs horizontally left, and the $5\,\mathrm{m}$ member slopes $60^\circ$ below the leftward horizontal. Use $E=210\,\mathrm{GPa}$, $A=4\times10^{-4}\,\mathrm{m^2}$ and a $40\,\mathrm{kN}$ downward load at node $1$.",
    "33a": r"Find the nodal displacements and the stresses in both bars. From node $1$, a $5\,\mathrm{m}$ bar slopes $45^\circ$ above the leftward horizontal and a $10\,\mathrm{m}$ bar runs horizontally left. A vertical spring of $2000\,\mathrm{kN/m}$ supports node $1$, where $50\,\mathrm{kN}$ acts downward. Both bars have $E=210\,\mathrm{GPa}$ and $A=5\times10^{-4}\,\mathrm{m^2}$.",
    "33b": r"Find the nodal displacements and the stresses in the symmetric two-bar truss. Each $5\,\mathrm{m}$ bar makes $60^\circ$ with the horizontal and has $E=210\,\mathrm{GPa}$ and $A=5\times10^{-4}\,\mathrm{m^2}$. Node $1$ carries $100\,\mathrm{kN}$ downward and is supported by a vertical spring with $k=4000\,\mathrm{N/m}$.",
    "49": INCLINED_TASK + r"Members $1$–$2$ and $1$–$3$ are horizontal and vertical, each of length $L$. Node $3$ is pinned, node $1$ rolls along a plane descending at $45^\circ$ to the right, and node $2$ rolls vertically under a downward load of $2000\,\mathrm{lb}$.",
    "50": INCLINED_TASK + r"Node $3$ is pinned and lies $L$ above node $1$ and $L$ left of node $2$. Node $1$ rolls along a plane descending at $45^\circ$ to the right. Node $2$ rolls vertically and carries $2000\,\mathrm{lb}$ downward.",
    "51": INCLINED_TASK + r"The truss is equilateral, with pins at nodes $1$ and $3$. Node $2$ rolls along a plane rising at $45^\circ$ to the right, and a $2000\,\mathrm{lb}$ load acts there along that plane, up and to the right.",
}

BAR_K = r"k_e=\frac{E_e A_e}{L_e},\quad K_e=k_e\begin{bmatrix}1&-1\\-1&1\end{bmatrix}"
TRUSS_K = (r"K_e=k_e b_e^{T}b_e,\quad k_e=\frac{E_e A_e}{L_e},\quad"
           r" b_e=\begin{bmatrix}-c_e&-s_e&c_e&s_e\end{bmatrix}")
TRUSS_AXES = (r"Với thứ tự $[u_i,v_i,u_j,v_j]^T$, dùng $c_e=\cos\theta_e$ và "
              r"$s_e=\sin\theta_e$, lấy từ hướng $i\to j$ trong hệ toàn cục.")
SPRING_HINT = r" Với lò xo, thay $E_e A_e/L_e$ bằng độ cứng $k$ cho trước."
NOTES = {
    "2": "Chuyển vị, phản lực và lực đầu phần tử khớp đến độ chính xác in.",
    "3": r"Chuyển vị và lực khớp gần đúng. Sách in $R_{1x}=-5715\,\mathrm{lb}$; nghiệm chưa làm tròn cho $R_{1x}=-5714.2857\,\mathrm{lb}$.",
    "4": "Chuyển vị và lực khớp với sai khác dưới $0.41\\%$ do đáp án in dùng giá trị xấp xỉ.",
    "5": "Chuyển vị, phản lực và lực đầu phần tử khớp.",
    "7": r"Các giá trị in gần nghiệm số, nhưng $R_{1x}=-33.15\,\mathrm{lb}$ và $R_{4x}=-9975\,\mathrm{lb}$ cộng lại không cân bằng tải $10000\,\mathrm{lb}$. Dùng phản lực từ hệ chưa làm tròn.",
    "8": r"Sách in $u_3=-1.678\,\mathrm{mm}$; nghiệm là $-1.678571\ldots\,\mathrm{mm}$. $u_2$ và phản lực khớp.",
    "9": r"Khớp chuyển vị, lực đầu thanh và phản lực. $R_{3x}$ chính là $F_3$ cần để duy trì chuyển vị đã cho.",
    "10": "Chuyển vị, phản lực và lực đầu phần tử khớp gần đúng (sai khác dưới $0.04\\%$).",
    "20": (r"Sách in $v_2=0.142\,\mathrm{in}$ và $\sigma_1=\sigma_2=707\,\mathrm{psi}$, "
           r"gần với kết quả nếu tải là $5\,\mathrm{kip}$, không phải $10\,\mathrm{kip}$ như hình. "
           r"Với tải trong hình, cân bằng cho $2N\sin45^\circ=10\,000\,\mathrm{lb}$; dùng nghiệm trong bảng."),
    "22": "Chuyển vị và ứng suất khớp gần đúng, với sai khác tối đa khoảng $0.584\\%$. Nghiệm chưa làm tròn thỏa cân bằng tại nút $1$.",
    "23": r"Khớp cả hai chuyển vị tại nút $1$ và ứng suất $\sigma_1$.",
    "24": (r"Các hệ số chuyển vị sách in là $26675$ và $105021$; giá trị từ hệ chưa làm tròn là "
           r"$26666.6667$ và $105000$, tính theo $\mathrm{lb\cdot ft}$ và chia cho $EA$. "
           r"Lực dọc khớp sau khi đổi từ lực đầu phần tử sang quy ước kéo dương."),
    "27": r"Chuyển vị và lực dọc khớp trong khoảng $0.24\%$ sau khi đổi quy ước lực đầu thanh; dùng lực chưa làm tròn để kiểm tra cân bằng nút $3$.",
    "29": "Chuyển vị và ứng suất khớp gần đúng. Cả ba chiều dài đều bằng $3\\,\\mathrm{m}$ như trên hình.",
    "30": "Chuyển vị và ứng suất khớp gần đúng, với sai khác tối đa khoảng $0.21\\%$.",
    "33a": "Khớp hai chuyển vị và hai ứng suất in. Lực lò xo được tính thêm, không quy thành ứng suất.",
    "33b": (r"Phụ lục chỉ liệt kê phần (a). Kiểm chứng độc lập bằng đối xứng: $u_1=0$ và "
            r"$v_1=-P/(2EA\sin^2 60^\circ/L+k)$ với $P=100\,\mathrm{kN}$, giữ đúng $k=4000\,\mathrm{N/m}$."),
    "49": "Khớp chuyển vị, phản lực ngang tại nút $2$ và các ứng suất in.",
    "50": "Khớp chuyển vị đứng tại nút $2$ được in; ứng suất được tính thêm từ chuyển vị.",
    "51": (r"$q_2$ làm tròn đến $0.001\,\mathrm{in}$ cho $0.002\,\mathrm{in}$ như sách. "
           r"Độ lớn thành phần lực tiếp tuyến tại nút $2$ là $2000\,\mathrm{lb}$, nhưng với chiều tiếp tuyến "
           r"lên phải ta được $+2000\,\mathrm{lb}$. Chiếu $R_2$ lên pháp tuyến $(-1,1)/\sqrt{2}$ cho "
           r"$-881.8540\,\mathrm{lb}$, không phải $-2828\,\mathrm{lb}$. Chiếu $R_1$ lên tiếp tuyến "
           r"$(1,-1)/\sqrt{2}$ cho $-1763.7079\,\mathrm{lb}$, không đạt độ lớn $2800\,\mathrm{lb}$ trong sách."),
}

GLOSSARY = {
    "direct stiffness method": "phương pháp độ cứng trực tiếp",
    "nodal displacement": "chuyển vị nút",
    "axial force": "lực dọc trục",
    "axial stress": "ứng suất dọc trục",
    "support reaction": "phản lực gối tựa",
    "tension / compression": "kéo / nén",
}
TARGETS = {
    "2": "d3x", "3": "d2x", "4": "d3x", "5": "d3x", "7": "d3x", "8": "d3x",
    "9": "R3x", "10": "d2x", "20": "d2y", "22": "d1y", "23": "d1x",
    "27": "d3x", "29": "d1y", "30": "d1y", "33a": "d1y", "33b": "d1y",
    "49": "d2y", "50": "d2y", "51": "q1",
}


def math(text):
    return f"${text}$"


def display(text):
    return f"$${text}$$"


def unit(text):
    return rf"\mathrm{{{text}}}"


def number(value, final=False):
    if abs(value) < 5e-11:
        return "0"
    if final:
        plain = f"{value:.4f}" if abs(value) >= .01 else f"{value:.4e}"
    else:
        plain = f"{value:.6g}"
    if "e" in plain:
        m, e = plain.split("e")
        return rf"{m}\times10^{{{int(e)}}}"
    return plain


def matrix(values):
    rows = ("&".join(x if isinstance(x, str) else number(x) for x in row) for row in values)
    return r"\begin{bmatrix}" + r"\\".join(rows) + r"\end{bmatrix}"


def vector(values):
    return matrix((x,) for x in values)


def table(headers, rows):
    def line(row):
        return "| " + " | ".join(row) + " |"
    return "\n".join([line(headers), line(["---"] * len(headers)), *(line(row) for row in rows)])


def component(node, axis):
    return f"{'uv'[axis]}_{node}"


def create_entry(key, model, result):
    bar = model.dim == 1
    spring = any(e.spring is not None for e in model.elements)
    inclined = key in {"49", "50", "51"}
    length, force = model.length_unit, model.force_unit
    length_tex, force_tex = unit(length), unit(force)
    stress_unit = unit(model.stress_unit)
    stiffness_tex = unit(f"{force}/{length}") if not model.symbolic else r"\mathrm{ft^{-1}}"
    stiffness_label = "k_e" if not model.symbolic else r"k_e/(EA)"

    glossary = dict(GLOSSARY)
    glossary.update({"bar element": "phần tử thanh 1D", "prescribed displacement": "chuyển vị đặt trước"}
                    if bar else {"plane truss": "dàn phẳng", "direction cosine": "cosin chỉ phương",
                                 "pin support": "gối khớp"})
    if spring:
        glossary["spring stiffness"] = "độ cứng lò xo"
    if inclined:
        glossary["inclined roller"] = "gối con lăn trên mặt nghiêng"

    k_eq = BAR_K if bar else TRUSS_K
    hint = ("" if bar else TRUSS_AXES + " ") + display(k_eq)
    if spring:
        hint += SPRING_HINT
    if inclined:
        hint += r" Chiếu chuyển vị con lăn lên tiếp tuyến và triệt tiêu thành phần pháp tuyến."
    if key == "9":
        hint += r" Xem $u_3$ là chuyển vị đặt trước, không gán $F_3$ vào vế tải đã biết."

    step1 = ["**Bước 1: Ma trận độ cứng phần tử**",
             r"Chọn trục $x$ sang phải" + (r", trục $y$ hướng lên." if not bar else "."),
             *([] if bar else [TRUSS_AXES]),
             display(k_eq)]
    if length == "mm":
        step1.append(r"Dùng $\mathrm{mm}$ cho chiều dài, $\mathrm{mm^2}$ cho diện tích và $\mathrm{kN}$ cho lực.")
    if spring:
        step1.append(SPRING_HINT.strip())
    if model.symbolic:
        step1.append(r"Giữ $EA$ dưới dạng tham số chung; bảng dùng $k_e/(EA)=1/L_e$.")
    elements = []
    for n, (e, L, direction, k) in enumerate(
            zip(model.elements, result.lengths, result.directions, result.stiffness), 1):
        length_value = "— (lò xo)" if e.spring is not None else math(number(L))
        row = [str(n), math(f"{e.i}\\to{e.j}"), length_value]
        if not bar:
            row += [math(number(c)) for c in direction]
        elements.append(row + [math(number(k))])
    step1.append(table(["Phần tử", "Nút", math(f"L_e\\ ({length_tex})")]
                       + ([] if bar else [math("c_e"), math("s_e")])
                       + [math(f"{stiffness_label}\\ ({stiffness_tex})")], elements))

    step2 = ["**Bước 2: Ghép nối và khử điều kiện biên**",
             r"Cộng từng $K_e$ vào các hàng/cột của hai nút tương ứng trong $K$."]
    zero_nodes = sorted(set(range(1, len(model.nodes) + 1))
                        - {d.node for d in model.free} - {x[0] for x in model.prescribed})
    if zero_nodes:
        step2.append("Khóa mọi thành phần chuyển vị tại nút "
                     + ", ".join(math(str(n)) for n in zero_nodes) + ".")
    if key == "9":
        step2.append(r"Áp đặt $u_3=25\,\mathrm{mm}$ trong $d_0$. Ẩn số duy nhất là $u_2$; chuyển $K_{23}u_3$ sang vế phải.")
    if key in {"49", "50"}:
        step2.append(r"Gối $1$: $(u_1,v_1)=q_1(1,-1)/\sqrt2$. Gối $2$: $u_2=0$, $v_2$ tự do.")
    if key == "51":
        step2.append(r"Gối $2$: $(u_2,v_2)=q_2(1,1)/\sqrt2$. Pháp tuyến chọn là $(-1,1)/\sqrt2$.")
    step2 += [
        r"Các cột của $T$ cho các hướng chuyển vị tự do; $d_0$ chứa các giá trị đặt trước.",
        display(r"d=d_0+Tq,\quad K_r=T^TKT,\quad P_r=T^T(P-Kd_0),\quad K_rq=P_r"),
        display(r"q=" + vector(d.label for d in model.free)),
        "Dạng số của hệ rút gọn (hệ số được hiển thị với tối đa 6 chữ số có nghĩa):",
        display(rf"{'K_r/(EA)' if model.symbolic else 'K_r'}={matrix(result.Kr)}\,{stiffness_tex},\quad"
                rf" P_r={vector(result.Pr)}\,{force_tex}"),
    ]

    step3 = ["**Bước 3: Chuyển vị, ứng suất và phản lực**",
             r"Giải trực tiếp $K_rq=P_r$ và thế ngược $d=d_0+Tq$."]
    if inclined:
        step3.append("Tọa độ tiếp tuyến: " + math(
            rf"{model.free[0].label}={number(result.q[0], True)}\,{length_tex}") + ".")
    if model.symbolic:
        step3.append(r"Bảng nút ghi các hệ số $EAu, EAv$; chia cho $EA$ (theo $\mathrm{lb}$) để được chuyển vị theo $\mathrm{ft}$.")
    d_labels = ["u"] if bar else ["u", "v"]
    if model.symbolic:
        d_labels = ["EAu", "EAv"]
    d_unit = r"\mathrm{lb\cdot ft}" if model.symbolic else length_tex
    reaction_labels = ["R_x"] if bar else ["R_x", "R_y"]
    step3.append(table(["Nút"] + [math(f"{label}\\ ({d_unit})") for label in d_labels]
                       + [math(f"{label}\\ ({force_tex})") for label in reaction_labels],
                       ([str(i), *(math(number(x, True)) for x in np.r_[d, reaction])]
                        for i, (d, reaction) in enumerate(zip(result.d, result.reactions), 1))))
    delta = r"u_j-u_i" if bar else r"b_e d_e"
    stress_eq = "" if model.symbolic else r",\quad \sigma_e=N_e/A_e\ \text{(thanh)}"
    step3 += [
        display(rf"R=Kd-P,\quad N_e=k_e({delta}),\quad \hat f_e=[-N_e,N_e]^T" + stress_eq),
        "Dấu dương là kéo, dấu âm là nén. Cặp lực đầu phần tử dùng trục địa phương.",
    ]
    if model.symbolic:
        step3.append(r"Không có diện tích riêng để cho giá trị số của $\sigma_e$.")
    elif length == "mm":
        step3.append(r"Đổi đơn vị ứng suất theo $1\,\mathrm{kN/mm^2}=1000\,\mathrm{MPa}$.")
    stress_header = [] if model.symbolic else [math(rf"\sigma_e\ ({stress_unit})")]
    step3.append(table(["Phần tử", math(rf"N_e\ ({force_tex})")] + stress_header,
                       ([str(i), math(number(N, True))]
                        + ([] if model.symbolic else [math(number(s, True)) if s is not None else "— (lò xo)"])
                        for i, (N, s) in enumerate(zip(result.axial, result.stress), 1))))
    if key in {"22", "27"}:
        loaded = next(iter(model.loads))
        node_forces = [(i, N * n * (1 if e.i == loaded else -1))
                       for i, (e, N, n) in enumerate(zip(model.elements, result.axial, result.directions), 1)
                       if loaded in (e.i, e.j)]
        vectors = node_forces + [("Tải ngoài", model.loads[loaded])]
        vectors.append(("Tổng", np.sum([xy for _, xy in vectors], axis=0)))
        step3 += [f"Kiểm tra cân bằng tại nút {math(str(loaded))}: lực của thanh lên nút cộng tải ngoài bằng không.",
                  table(["Nguồn lực", math(f"F_x\\ ({force_tex})"), math(f"F_y\\ ({force_tex})")],
                        ([str(i), math(number(x)), math(number(y))] for i, (x, y) in vectors))]
    step3.append(f"Đối chiếu Answers to Selected Problems (PDF tr. {BOOK[key][0]}): {NOTES[key]}")

    target = TARGETS.get(key)
    if target is None:
        expected = None
        label = None
        final = (vector(("u_2", "v_2", "u_3", "v_3")) + r"=\frac{"
                 + vector(number(x, True) for x in result.q) + r"\,\mathrm{lb\cdot ft}}{EA}")
    else:
        expected = float(reference_value(result, target))
        if target[0] == "d":
            node = int(target[1:-1])
            axis = "xy".index(target[-1])
            labels = [component(node, a) for a in range(model.dim)]
            parts = [f"{n}={number(x, True)}\\,{length_tex}" for n, x in zip(labels, result.d[node - 1])]
            if key == "20":
                parts.append(rf"\sigma_1={number(result.stress[0], True)}\,{stress_unit}")
            final = r",\quad ".join(parts)
            label = f"{component(node, axis)}\\ ({length_tex})"
        else:
            symbol = "F_3" if key == "9" else "q_2"
            tex = force_tex if key == "9" else length_tex
            label = f"{symbol}\\ ({tex})"
            final = f"{symbol}={number(expected, True)}\\,{tex}"

    entry = {
        "id": ID + key,
        "source_problem": f"Problem 3.{key} - Logan (Chapter 3: Trusses)",
        "method_tag": "1D Bar Element" if bar else "2D Plane Truss Element",
        "exam_focus": True,
        "figure_image": f"/images/logan_fig_p3_{key}_{'bar' if bar else 'truss'}.png",
        "problem_en": STATEMENTS[key],
        "glossary": glossary,
        "hint": hint,
        "steps": ["\n".join(step) for step in (step1, step2, step3)],
        "final_answer": final,
        "expected_numeric_value": expected,
    }
    if label is not None:
        entry["numeric_target_label"] = math(label)
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    results = verify_all()
    entries = {ID + key: create_entry(key, model, results[key]) for key, model in SELECTED.items()}
    original = json.loads(args.db.read_text(encoding="utf-8"))
    seen = {entry["id"] for entry in original}
    if len(seen) != len(original):
        raise ValueError("Existing exercise IDs are not unique.")
    for entry in entries.values():
        if not (ROOT / "public" / entry["figure_image"].lstrip("/")).is_file():
            raise FileNotFoundError(f"Missing figure for {entry['id']}: {entry['figure_image']}")
    updated = [entries.get(entry["id"], entry) for entry in original]
    updated.extend(entry for key, entry in entries.items() if key not in seen)
    text = json.dumps(updated, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                     dir=args.db.parent, suffix=".tmp", delete=False) as temp:
        pending = Path(temp.name)
        temp.write(text)
    try:
        pending.replace(args.db)
    finally:
        pending.unlink(missing_ok=True)
    print(f"Logan Ch. 3: {len(entries.keys() - seen)} added, "
          f"{len(entries.keys() & seen)} updated. Total exercises: {len(updated)}.")


if __name__ == "__main__":
    main()
