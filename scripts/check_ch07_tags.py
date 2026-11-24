import json
from pathlib import Path

p = Path("data/ch07_fem.json")
data = json.loads(p.read_text(encoding="utf-8"))
print(f"Total problems in ch07_fem.json: {len(data)}")
for i, item in enumerate(data):
    print(f"[{i+1}] ID: {item.get('id')} | Tag: {item.get('method_tag')} | Exam: {item.get('exam_focus')} | Fig: {item.get('figure_image')}")
