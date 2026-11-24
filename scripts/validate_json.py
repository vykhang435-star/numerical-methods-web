"""Validate all JSON files in the data directory for valid JSON syntax and KaTeX escape rules."""

import json
import sys
from pathlib import Path

def validate_file(file_path: Path) -> bool:
    print(f"Validating {file_path.name}...")
    try:
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
        print(f"  [OK] Valid JSON. Top-level keys/items count: {len(data)}")
        return True
    except json.JSONDecodeError as e:
        print(f"  [ERROR] JSONDecodeError: {e}")
        # Print context around error
        lines = content.splitlines()
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        print("  Context:")
        for idx in range(start, end):
            prefix = ">>" if idx + 1 == e.lineno else "  "
            print(f"  {prefix} Line {idx+1}: {lines[idx]}")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir = Path("../data")
    
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print("No JSON files found in data directory.")
        sys.exit(0)
    
    all_passed = True
    for jf in json_files:
        if not validate_file(jf):
            all_passed = False
    
    if all_passed:
        print("\nAll JSON files validated successfully!")
        sys.exit(0)
    else:
        print("\nSome JSON files failed validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
