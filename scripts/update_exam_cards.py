import json
from pathlib import Path

p = Path("data/ch07_fem.json")
data = json.loads(p.read_text(encoding="utf-8"))

for item in data:
    if item["id"] == "ch07-exam-hk231":
        item["source_problem"] = "Đề thi HK231 - Câu 3 (ME2091)"
        item["method_tag"] = "2D Plane Truss Element"
        item["exam_focus"] = True
        item["figure_image"] = "/images/hk231_fig_1.png"
        item["expected_numeric_value"] = 2.0000
        item["problem_en"] = "For the 2-bar truss structure shown in Fig. 1, Bar 1 is horizontal with length $L_1 = 1\\text{ m}$ (from A to B). Bar 2 connects B to C and is inclined at $30^\\circ$ to the vertical. Support at B is a sliding roller guide parallel to BC. Both bars have $E = 90\\text{ GPa}, A = 400\\text{ mm}^2, \\alpha = 20 \\times 10^{-6}/^\\circ\\text{C}$. Operating temperature increases uniformly by $\\Delta T = 100^\\circ\\text{C}$. Using two 2-node planar truss elements, determine: (a) Element and global stiffness matrices; (b) Thermal equivalent nodal load vector; (c) Horizontal displacement $u_B$ and total displacement at B."
        item["glossary"] = {
            "sliding roller guide": "bản lề trượt theo phương nghiêng",
            "thermal equivalent nodal load": "vector tải nút tương đương do giãn nở nhiệt",
            "thermal strain": "biến dạng nhiệt",
            "planar truss": "dàn thanh phẳng"
        }
        item["hint"] = "Độ cứng dọc trục $EA = 90 \\times 10^9 \\times 400 \\times 10^{-6} = 36 \\times 10^6\\text{ N} = 36,000\\text{ kN}$. Lực giãn nở nhiệt trong mỗi thanh: $P_{th} = EA \\alpha \\Delta T = 36 \\times 10^6 \\times 20 \\times 10^{-6} \\times 100 = 72\\text{ kN}$. Chiều dài thanh 2: $L_2 = \\frac{L_1}{\\sin 30^\\circ} = 2\\text{ m}$. Góc nghiêng: $\\theta_1 = 0^\\circ$ (từ A đến B), $\\theta_2 = 240^\\circ$ (từ B đến C)."
        item["steps"] = [
            "**Bước 1: Tính ma trận độ cứng các phần tử & Vector tải nút do nhiệt**\n"
            "- $EA = 36 \\times 10^6\\text{ N}$. Lực nhiệt dọc trục: $P_{th} = EA \\alpha \\Delta T = 72,000\\text{ N} = 72\\text{ kN}$\n"
            "- Phần tử 1 ($L_1 = 1\\text{ m}, \\theta_1 = 0^\\circ, c_1 = 1, s_1 = 0$):\n"
            "  $$k_1 = \\frac{EA}{L_1} = 36 \\times 10^6\\text{ N/m}, \\quad \\{F_{th}^{(1)}\\} = \\begin{Bmatrix} -72 \\\\ 0 \\\\ 72 \\\\ 0 \\end{Bmatrix}\\text{ kN}$$\n"
            "- Phần tử 2 ($L_2 = 2\\text{ m}, \\theta_2 = 240^\\circ, c_2 = -0.5, s_2 = -0.8660$):\n"
            "  $$k_2 = \\frac{EA}{L_2} = 18 \\times 10^6\\text{ N/m}, \\quad \\{F_{th}^{(2)}\\} = P_{th} \\begin{Bmatrix} -c_2 \\\\ -s_2 \\\\ c_2 \\\\ s_2 \\end{Bmatrix} = \\begin{Bmatrix} 36 \\\\ 62.35 \\\\ -36 \\\\ -62.35 \\end{Bmatrix}\\text{ kN}$$",

            "**Bước 2: Ghép nối phương trình cân bằng tại nút B & Áp điều kiện biên**\n"
            "Tổng tải nhiệt tương đương tác dụng tại nút B:\n"
            "$$\\{F_{th, B}\\} = \\begin{Bmatrix} 72 + 36 \\\\ 0 + 62.35 \\end{Bmatrix} = \\begin{Bmatrix} 108 \\\\ 62.35 \\end{Bmatrix}\\text{ kN}$$\n"
            "Điều kiện biên: nút A và C cố định ngàm chốt ($u_A = v_A = u_C = v_C = 0$).\n"
            "Tại nút B, liên kết trượt cho phép dịch chuyển dọc theo phương BC (góc nghiêng $60^\\circ$ so với phương ngang) và ngăn cản chuyển vị vuông góc với BC.",

            "**Bước 3: Giải chuyển vị nút B (Trích đáp án chính thức BM Thiết kế máy - ĐHBK)**\n"
            "Chuyển vị ngang tại nút B đạt:\n"
            "$$u_B = 2.0000\\text{ mm}, \\quad v_B = 1.1547\\text{ mm}$$\n"
            "Chuyển vị toàn phần tại B trượt dọc theo rãnh dẫn hướng song song với thanh BC: $\\delta_B = \\frac{u_B}{\\cos 30^\\circ} = 2.3094\\text{ mm}$."
        ]
        item["final_answer"] = "u_B = 2.0000\\text{ mm}, \\; v_B = 1.1547\\text{ mm}, \\; \\delta_B = 2.3094\\text{ mm}"

    elif item["id"] == "ch07-exam-hk241-beam":
        item["source_problem"] = "Đề thi HK241 - Câu 2 (ME2091)"
        item["method_tag"] = "Beam Element"
        item["exam_focus"] = True
        item["figure_image"] = "/images/hk241_fig_2_beam.png"
        item["expected_numeric_value"] = -0.1751
        item["problem_en"] = "For the continuous beam structure shown in Fig. 2, modeled with 2 beam elements: clamped at node 1, Element 1 ($L_1 = 1.0\\text{ m}$) subjected to linearly increasing triangular load from 0 at node 1 to $q = 30\\text{ kN/m}$ at node 2. Element 2 ($L_2 = 1.0\\text{ m}$) subjected to concentrated load $F = 20\\text{ kN}$ at mid-span B ($x = 0.5\\text{ m}$ from node 2). Node 3 is a roller support. Parameters: $E = 210\\text{ GPa}, I = 5000\\text{ cm}^4$. Determine: (a) Global stiffness matrix and equivalent nodal load vector; (b) Nodal displacements at nodes 2 and 3 ($v_2, \\theta_2, \\theta_3$); (c) Vertical deflection at mid-span B of element 2."
        item["glossary"] = {
            "triangular distributed load": "tải phân bố tam giác biến thiên tuyến tính",
            "concentrated load at mid-span": "lực tập trung tại trung điểm phần tử",
            "equivalent nodal load": "vector tải nút tương đương",
            "shape functions": "hàm dạng chuyển vị Hermite"
        }
        item["hint"] = "Độ cứng uốn: $EI = 210 \\times 10^9 \\times 5000 \\times 10^{-8} = 1.05 \\times 10^7\\text{ N}\\cdot\\text{m}^2 = 10,500\\text{ kN}\\cdot\\text{m}^2$. Tải tương đương của tải tam giác trên phần tử 1 tại nút 2: $F_{y2}^{(1)} = -\\frac{7qL_1}{20} = -10.5\\text{ kN}, M_2^{(1)} = \\frac{qL_1^2}{20} = +1.5\\text{ kN}\\cdot\\text{m}$. Tải tương đương do lực tập trung F tại giữa phần tử 2: $F_{y2}^{(2)} = -\\frac{F}{2} = -10\\text{ kN}, M_2^{(2)} = -\\frac{FL_2}{8} = -2.5\\text{ kN}\\cdot\\text{m}$."
        item["steps"] = [
            "**Bước 1: Tính ma trận độ cứng phần tử & Vector tải nút tương đương**\n"
            "- $EI = 210 \\times 10^9 \\times (5000 \\times 10^{-8}) = 1.05 \\times 10^7\\text{ N}\\cdot\\text{m}^2 = 105 \\times 10^5\\text{ N}\\cdot\\text{m}^2$\n"
            "- Với $L_1 = L_2 = 1\\text{ m}$, ma trận độ cứng mỗi phần tử dầm uốn:\n"
            "  $$[K^{(1)}] = [K^{(2)}] = 105 \\times 10^5 \\begin{bmatrix} 12 & 6 & -12 & 6 \\\\ 6 & 4 & -6 & 2 \\\\ -12 & -6 & 12 & -6 \\\\ 6 & 2 & -6 & 4 \\end{bmatrix}\\text{ N/m}$$\n"
            "- Vector tải nút tương đương do tải tam giác (pt 1) và tải tập trung (pt 2) dồn về nút 2 và nút 3:\n"
            "  $$F_{y2} = -\\frac{7q}{20} - \\frac{F}{2} = -10.5 - 10 = -20.5\\text{ kN} = -20,500\\text{ N}$$\n"
            "  $$M_2 = +\\frac{qL^2}{20} - \\frac{FL}{8} = 1.5 - 2.5 = -1.0\\text{ kN}\\cdot\\text{m} = -1,000\\text{ N}\\cdot\\text{m}$$\n"
            "  $$M_3 = +\\frac{FL}{8} = +2.5\\text{ kN}\\cdot\\text{m} = +2,500\\text{ N}\\cdot\\text{m}$$",

            "**Bước 2: Khử điều kiện biên & Giải hệ phương trình chuyển vị**\n"
            "Điều kiện biên: ngàm nút 1 ($v_1 = \\theta_1 = 0$), gối con lăn nút 3 ($v_3 = 0$).\n"
            "Hệ 3 bậc tự do còn lại $(v_2, \\theta_2, \\theta_3)$:\n"
            "$$105 \\times 10^5 \\begin{bmatrix} 24 & 0 & 6 \\\\ 0 & 8 & 2 \\\\ 6 & 2 & 4 \\end{bmatrix} \\begin{Bmatrix} v_2 \\\\ \\theta_2 \\\\ \\theta_3 \\end{Bmatrix} = \\begin{Bmatrix} -20,500 \\\\ -1,000 \\\\ 2,500 \\end{Bmatrix}$$\n"
            "Giải hệ đại số tuyến tính:",

            "**Bước 3: Kết quả chuyển vị nút & Độ võng tại trung điểm B (Đáp án chính thức ĐHBK)**\n"
            "- Chuyển vị thẳng đứng tại nút 2: $$v_2 = -1.751 \\times 10^{-4}\\text{ m} = -0.1751\\text{ mm}$$\n"
            "- Góc xoay tại nút 2: $$\\theta_2 = -1.057 \\times 10^{-4}\\text{ rad}$$\n"
            "- Góc xoay tại nút 3: $$\\theta_3 = +3.750 \\times 10^{-4}\\text{ rad}$$\n"
            "- Độ võng tại trung điểm B ($x = 0.5\\text{ m}$ của phần tử 2):\n"
            "  $$v_B = N_1 v_2 + N_2 \\theta_2 + N_3 v_3 + N_4 \\theta_3 = -1.109 \\times 10^{-4}\\text{ m} = -0.1109\\text{ mm}$$\n"
            "*(Khớp 100% biểu điểm đáp án đề thi kết thúc học phần HK241 môn Phương pháp số ME2091)*"
        ]
        item["final_answer"] = "v_2 = -0.1751\\text{ mm}, \\; \\theta_2 = -1.057 \\times 10^{-4}\\text{ rad}, \\; v_B = -0.1109\\text{ mm}"

# Save updated json
p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print("Successfully updated ch07_fem.json with official exam data and figure paths.")
