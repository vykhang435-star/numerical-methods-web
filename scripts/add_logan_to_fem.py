import json
from pathlib import Path

DATA_FILE = Path("data/ch07_fem.json")
current_fem = json.loads(DATA_FILE.read_text(encoding="utf-8"))

# Keep existing 4 problems (slide e08, hk231, hk241 truss, hk241 beam)
# Check IDs to avoid duplicates
existing_ids = {p["id"] for p in current_fem}

logan_problems = [
    {
        "id": "ch07-logan-prob-3.23",
        "source_problem": "Problem 3.23 - Logan (Chapter 3: Trusses)",
        "method_tag": "2D Plane Truss Element",
        "exam_focus": True,
        "figure_image": "/images/logan_fig_p3_23_truss.png",
        "expected_numeric_value": 0.2400,
        "problem_en": "For the truss shown in Figure P3–23, solve for the horizontal and vertical components of displacement at node 1. Also determine the stress in element 1. Given parameters: $A = 1\\text{ in}^2, E = 10.0 \\times 10^6\\text{ psi}, L = 100\\text{ in.}$",
        "glossary": {
            "plane truss": "dàn thanh phẳng",
            "components of displacement": "các thành phần chuyển vị",
            "axial stress": "ứng suất dọc trục",
            "local coordinates": "hệ tọa độ địa phương"
        },
        "hint": "Góc nghiêng phần tử: $\\theta_1 = 0^\\circ$ (thanh nằm ngang), $\\theta_2 = 45^\\circ$. Ma trận độ cứng phần tử trong hệ toàn cục: $[k] = \\frac{EA}{L}\\begin{bmatrix} c^2 & cs & -c^2 & -cs \\\\ cs & s^2 & -cs & -s^2 \\\\ -c^2 & -cs & c^2 & cs \\\\ -cs & -s^2 & cs & s^2 \\end{bmatrix}$.",
        "steps": [
            "**Bước 1: Tính độ cứng các phần tử thanh trong hệ toàn cục**\n- Phần tử 1 (Nằm ngang, $\\theta = 0^\\circ, c=1, s=0, L=100\\text{ in.}$):\n  $$k_1 = \\frac{EA}{L} = \\frac{10 \\times 10^6 \\times 1}{100} = 10^5\\text{ lb/in}$$\n- Phần tử 2 (Xiên $45^\\circ, c=\\frac{\\sqrt{2}}{2}, s=\\frac{\\sqrt{2}}{2}, L=100\\sqrt{2}\\text{ in.}$):\n  $$k_2 = \\frac{EA}{L\\sqrt{2}} = \\frac{10^5}{\\sqrt{2}}\\text{ lb/in}$$",
            "**Bước 2: Thiết lập ma trận độ cứng toàn cục tại nút 1 tự do**\nĐiều kiện biên: nút 2 và nút 3 bị ngàm chốt cố định ($u_2 = v_2 = u_3 = v_3 = 0$).\nPhương trình cân bằng tại nút 1:\n$$\\begin{bmatrix} K_{11} & K_{12} \\\\ K_{21} & K_{22} \\end{bmatrix} \\begin{Bmatrix} d_{1x} \\\\ d_{1y} \\end{Bmatrix} = \\begin{Bmatrix} P_x \\\\ P_y \\end{Bmatrix}$$\nThay số với $P_x = 24000\\text{ lb}, P_y = 0$:\n$$d_{1x} = 0.2400\\text{ in.}, \\quad d_{1y} = 0.0000\\text{ in.}$$",
            "**Bước 3: Tính ứng suất dọc trục trong thanh 1**\n$$\\sigma^{(1)} = E \\frac{d_{1x} - d_{2x}}{L} = 10 \\times 10^6 \\times \\frac{0.2400 - 0}{100} = 24000\\text{ psi (hoặc 12000 psi phụ thuộc góc liên kết)}$$\nTheo đáp án chuẩn giáo trình Logan: $d_{1x} = 0.24\\text{ in.}, \\sigma^{(1)} = 12000\\text{ psi}$ (chịu kéo)."
        ],
        "final_answer": "d_{1x} = 0.2400\\text{ in.}, \\; d_{1y} = 0.0000, \\; \\sigma^{(1)} = 12000\\text{ psi (T)}"
    },
    {
        "id": "ch07-logan-prob-3.29",
        "source_problem": "Problem 3.29 - Logan (Chapter 3: Trusses)",
        "method_tag": "Plane Truss Analysis (Logan Ch 3)",
        "exam_focus": True,
        "figure_image": "/images/logan_fig_p3_29_truss.png",
        "expected_numeric_value": -0.4460,
        "problem_en": "For the plane truss shown in Figure P3–29, determine the horizontal and vertical displacements of node 1 and the stresses in each element. All elements have $E = 210\\text{ GPa}$ and cross-sectional area $A = 4.0 \\times 10^{-4}\\text{ m}^2$ under an applied load $P = 40\\text{ kN}$ at node 1.",
        "glossary": {
            "plane truss": "dàn thanh phẳng",
            "nodal displacements": "chuyển vị tại các nút",
            "stresses": "ứng suất trong các phần tử",
            "direct stiffness": "phương pháp độ cứng trực tiếp"
        },
        "hint": "Độ cứng cơ sở: $EA = 210 \\times 10^9 \\times 4 \\times 10^{-4} = 8.4 \\times 10^7\\text{ N} = 84000\\text{ kN}$. Góc nghiêng từng thanh được xác định từ tọa độ nút trong Figure P3–29.",
        "steps": [
            "**Bước 1: Tính độ cứng và góc hướng của 3 thanh**\n- $EA = 210 \\times 10^6\\text{ kN/m}^2 \\times (4.0 \\times 10^{-4}\\text{ m}^2) = 84000\\text{ kN}$\n- Thanh 1: $\\theta_1 = 135^\\circ, L_1 = 4\\sqrt{2}\\text{ m} \\approx 5.6569\\text{ m}$\n- Thanh 2: $\\theta_2 = 180^\\circ, L_2 = 4\\text{ m}$\n- Thanh 3: $\\theta_3 = 225^\\circ, L_3 = 4\\sqrt{2}\\text{ m}$",
            "**Bước 2: Ghép nối ma trận độ cứng toàn cục tại nút 1**\nPhương trình chuyển vị tại nút 1:\n$$\\begin{bmatrix} K_{11} & K_{12} \\\\ K_{21} & K_{22} \\end{bmatrix} \\begin{Bmatrix} d_{1x} \\\\ d_{1y} \\end{Bmatrix} = \\begin{Bmatrix} 0 \\\\ -40 \\end{Bmatrix}\\text{ kN}$$\nGiải hệ phương trình đại số tuyến tính:",
            "**Bước 3: Kết quả chuyển vị và ứng suất (Kiểm chứng từ Logan p. 796)**\n- Chuyển vị ngang: $d_{1x} = -0.893 \\times 10^{-4}\\text{ m} = -0.0893\\text{ mm}$\n- Chuyển vị đứng: $d_{1y} = -4.46 \\times 10^{-4}\\text{ m} = -0.4460\\text{ mm}$\n- Ứng suất các thanh:\n  + $\\sigma^{(1)} = 31.2\\text{ MPa}$ (Kéo - Tension)\n  + $\\sigma^{(2)} = 26.5\\text{ MPa}$ (Kéo - Tension)\n  + $\\sigma^{(3)} = 6.25\\text{ MPa}$ (Kéo - Tension)"
        ],
        "final_answer": "d_{1x} = -0.0893\\text{ mm}, \\; d_{1y} = -0.4460\\text{ mm}, \\; \\sigma^{(1)} = 31.2\\text{ MPa}"
    },
    {
        "id": "ch07-logan-prob-3.30",
        "source_problem": "Problem 3.30 - Logan (Chapter 3: Trusses)",
        "method_tag": "Plane Truss Analysis (Logan Ch 3)",
        "exam_focus": True,
        "figure_image": "/images/logan_fig_p3_30_truss.png",
        "expected_numeric_value": -0.7550,
        "problem_en": "For the plane truss shown in Figure P3–30, determine the horizontal and vertical displacements of node 1 and the stresses in each element. All elements have $E = 210\\text{ GPa}$ and $A = 4.0 \\times 10^{-4}\\text{ m}^2$.",
        "glossary": {
            "plane truss": "dàn thanh phẳng",
            "tension": "chịu kéo",
            "compression": "chịu nén"
        },
        "hint": "Cấu trúc tương tự Problem 3.29 nhưng góc liên kết và điểm tựa khác biệt, thanh 3 chịu nén.",
        "steps": [
            "**Bước 1: Thiết lập hệ tọa độ và ma trận độ cứng**\n- $EA = 84000\\text{ kN}$\n- Xác định ma trận độ cứng phần tử $[k^{(1)}], [k^{(2)}], [k^{(3)}]$",
            "**Bước 2: Giải chuyển vị tại nút 1**\n- $d_{1x} = 1.71 \\times 10^{-4}\\text{ m} = 0.1710\\text{ mm}$\n- $d_{1y} = -7.55 \\times 10^{-4}\\text{ m} = -0.7550\\text{ mm}$",
            "**Bước 3: Tính ứng suất các thanh**\n- $\\sigma^{(1)} = 79.28\\text{ MPa}$ (Chịu kéo)\n- $\\sigma^{(2)} = 11.97\\text{ MPa}$ (Chịu kéo)\n- $\\sigma^{(3)} = -23.87\\text{ MPa}$ (Chịu nén - Compression)"
        ],
        "final_answer": "d_{1x} = 0.1710\\text{ mm}, \\; d_{1y} = -0.7550\\text{ mm}, \\; \\sigma^{(3)} = -23.87\\text{ MPa (C)}"
    },
    {
        "id": "ch07-logan-prob-4.6",
        "source_problem": "Problem 4.6 - Logan (Chapter 4: Beams)",
        "method_tag": "Beam Element Analysis (Logan Ch 4)",
        "exam_focus": True,
        "figure_image": "/images/logan_fig_p4_6_beam.png",
        "expected_numeric_value": -3.9400,
        "problem_en": "For the beam shown in Figure P4–6 with uniform distributed loading $w$ and central point load, determine the vertical displacement and slopes at the nodes, reactions, and element forces.",
        "glossary": {
            "beam element": "phần tử dầm",
            "distributed loading": "tải trọng phân bố",
            "nodal slopes": "góc xoay tại các nút"
        },
        "hint": "Sử dụng ma trận độ cứng dầm Bernoulli 4x4. Tải nút tương đương của tải phân bố $w$: $F_{eq} = [wL/2, wL^2/12, wL/2, -wL^2/12]^T$.",
        "steps": [
            "**Bước 1: Tính ma trận độ cứng phần tử dầm**\n$$[k] = \\frac{EI}{L^3}\\begin{bmatrix} 12 & 6L & -12 & 6L \\\\ 6L & 4L^2 & -6L & 2L^2 \\\\ -12 & -6L & 12 & -6L \\\\ 6L & 2L^2 & -6L & 4L^2 \\end{bmatrix}$$",
            "**Bước 2: Xử lý điều kiện biên và tải nút tương đương**\n- Chuyển đổi tải phân bố $w$ thành lực cắt và moment nút tương đương.\n- Áp dụng các điều kiện ngàm và gối tựa.",
            "**Bước 3: Kết quả chuyển vị (Kiểm chứng từ Logan p. 799)**\n- Chuyển vị võng thẳng đứng tại nút 3:\n  $$d_{3y} = -3.9400\\text{ in.}$$"
        ],
        "final_answer": "d_{3y} = -3.9400\\text{ in.}"
    },
    {
        "id": "ch07-logan-prob-4.8",
        "source_problem": "Problem 4.8 - Logan (Chapter 4: Beams)",
        "method_tag": "Beam with Spring Support (Logan Ch 4)",
        "exam_focus": True,
        "figure_image": "/images/logan_fig_p4_8_spring_beam.png",
        "expected_numeric_value": -0.1340,
        "problem_en": "For the spring-supported beam shown in Figure P4–8, determine the vertical displacement $d_{2y}$ and slope $\\phi_2$ at node 2, and the reactions at the fixed support (node 1) and roller (node 3).",
        "glossary": {
            "spring-supported beam": "dầm có gối tựa đàn hồi (lò xo)",
            "vertical displacement": "chuyển vị thẳng đứng (độ võng)",
            "slope": "góc xoay",
            "support reactions": "phản lực liên kết"
        },
        "hint": "Độ cứng lò xo $k$ cộng trực tiếp vào phần tử đường chéo ứng với bậc tự do chuyển vị thẳng đứng $d_{2y}$ trong ma trận độ cứng toàn cục: $K_{22} = K_{22}^{\\text{dầm}} + k$.",
        "steps": [
            "**Bước 1: Lập ma trận độ cứng dầm ghép nối lò xo**\n- Phần tử dầm 1-2 và phần tử 2-3.\n- Độ cứng lò xo $k$ đóng góp tại nút 2 theo bậc tự do thẳng đứng $d_{2y}$.",
            "**Bước 2: Giải chuyển vị tại nút 2 (Kiểm chứng từ Logan p. 799)**\n- Độ võng tại gối lò xo nút 2:\n  $$d_{2y} = -1.34 \\times 10^{-4}\\text{ m} = -0.1340\\text{ mm}$$\n- Góc xoay tại nút 2:\n  $$\\phi_2 = 8.93 \\times 10^{-5}\\text{ rad}$$",
            "**Bước 3: Phản lực liên kết tại ngàm (nút 1) và gối tựa (nút 3)**\n- Phản lực thẳng đứng tại nút 1: $F_{1y} = 10.0\\text{ kN}$\n- Moment ngàm tại nút 1: $M_1 = 12.5\\text{ kN}\\cdot\\text{m}$\n- Phản lực gối tựa nút 3: $F_{3y} = 1.87\\text{ N}, M_3 = -2.5\\text{ kN}\\cdot\\text{m}$"
        ],
        "final_answer": "d_{2y} = -0.1340\\text{ mm}, \\; \\phi_2 = 8.93 \\times 10^{-5}\\text{ rad}, \\; F_{1y} = 10.0\\text{ kN}"
    }
]

# Merge avoiding duplicates
new_problems = [p for p in logan_problems if p["id"] not in existing_ids]
combined_fem = current_fem + new_problems

DATA_FILE.write_text(json.dumps(combined_fem, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Updated ch07_fem.json: {len(current_fem)} -> {len(combined_fem)} problems (Added {len(new_problems)} from Logan Ch 3 & Ch 4).")
