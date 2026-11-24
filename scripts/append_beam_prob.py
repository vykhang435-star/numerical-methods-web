import json
import subprocess
import sys
from pathlib import Path

# Run verify_temp.py to get the 8 problems
subprocess.run([sys.executable, 'scripts/verify_temp.py'], cwd='d:/pps/numerical-methods-web')

# Load the 8 problems
p8 = json.loads(Path('data/ch02_roots.json').read_text(encoding='utf-8'))

# Beam problem with figure
beam_prob = {
    "id": "ch02-prob-5.15-fig",
    "source_problem": "Problem 5.15 - Chapra & Canale",
    "method_tag": "Bisection",
    "exam_focus": True,
    "figure_image": "/images/chapra_fig_p5_15_beam.png",
    "expected_numeric_value": 5.6563,
    "problem_en": "A beam is loaded as shown in Fig. P5.15. The bending moment equation inside the span ($0 \\le x \\le 6$) is given by $M(x) = 141.67x - 25x^2 = 0$. Use the bisection method with initial interval $[5, 6]$ to determine the position $x$ inside the beam where there is no moment (stopping criterion $\\varepsilon_s = 1.0\\%$).",
    "glossary": {
        "bending moment": "moment uốn",
        "bisection method": "phương pháp chia đôi",
        "stopping criterion": "tiêu chuẩn dừng lặp",
        "beam": "dầm chịu lực"
    },
    "hint": "Phương trình cân bằng moment: $M(x) = 141.67x - 25x^2 = 0$. Khảo sát đoạn $[5, 6]$: $M(5) = 83.35 > 0, M(6) = -49.98 < 0$. Chia đôi đến khi $\\varepsilon_a < 1.0\\%$.",
    "steps": [
        "**Bước 1: Thiết lập phương trình moment uốn**\n- Hàm số: $M(x) = 141.67x - 25x^2$\n- Khoảng cách ly ban đầu: $[5.0, 6.0]$\n- Tiêu chuẩn dừng: $\\varepsilon_a < 1.0\\%$",
        "**Bước 2: Bảng tính toán chia đôi**\n\n| $i$ | $x_l$ | $x_u$ | $x_r$ | $M(x_l)$ | $M(x_r)$ | $\\varepsilon_a$ (%) |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n| 1 | 5.0000 | 6.0000 | 5.5000 | 83.3500 | 22.9350 | --- |\n| 2 | 5.5000 | 6.0000 | 5.7500 | 22.9350 | -13.8975 | 4.3478\\% |\n| 3 | 5.5000 | 5.7500 | 5.6250 | 22.9350 | 4.4444 | 2.2222\\% |\n| 4 | 5.6250 | 5.7500 | 5.6875 | 4.4444 | -4.7452 | 1.0989\\% |\n| 5 | 5.6250 | 5.6875 | 5.6563 | 4.4444 | -0.1550 | 0.5525\\% |",
        "**Bước 3: Kết luận**\nSau 5 bước chia đôi, vị trí triệt tiêu moment uốn trên dầm là $x \\approx 5.6563\\text{ ft}$ với $\\varepsilon_a = 0.5525\\% < 1.0\\%$."
    ],
    "final_answer": "x \\approx 5.6563\\text{ ft} \\quad (\\varepsilon_a = 0.5525\\%)"
}

all_ch02 = p8 + [beam_prob]
Path('data/ch02_roots.json').write_text(json.dumps(all_ch02, ensure_ascii=False, indent=2), encoding='utf-8')
print('Updated ch02_roots.json with', len(all_ch02), 'problems.')
