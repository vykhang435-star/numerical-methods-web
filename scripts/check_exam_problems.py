import json
from pathlib import Path

p = Path("data/ch07_fem.json")
data = json.loads(p.read_text(encoding="utf-8"))

for item in data:
    if item["id"] in ["ch07-exam-hk231", "ch07-exam-hk241-beam", "ch07-exam-hk241-truss"]:
        print(f"=== {item['id']} ===")
        print("Figure:", item.get("figure_image"))
        print("Problem EN:", item.get("problem_en"))
        print("Final answer:", item.get("final_answer"))
        print("-" * 50)
