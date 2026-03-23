#!/usr/bin/env python3
"""
sync-check.py — Prüft ob die JS-Presets in index.html mit presets.yaml synchron sind.

Usage:
    python3 sync-check.py          # Nur prüfen
    python3 sync-check.py --fix    # JS-Parameter-Werte aus YAML anzeigen (zum manuellen Copy-Paste)
"""

import sys
import re
import json
import yaml
from pathlib import Path

DIR = Path(__file__).parent
YAML_PATH = DIR / "presets.yaml"
HTML_PATH = DIR / "index.html"


def main():
    with open(YAML_PATH) as f:
        data = yaml.safe_load(f)

    html = HTML_PATH.read_text()

    yaml_presets = data["presets"]
    issues = []

    for pk, preset in yaml_presets.items():
        yaml_params = preset["parameters"]

        # Find the JS parameters line for this preset
        # Pattern: key: { ... parameters:{...}, ...
        pattern = rf"'{pk}':\s*\{{[^}}]*?parameters:\{{([^}}]+)\}}"
        # Simpler: look for the parameters object
        param_pattern = rf"parameters:\{{([^}}]+)\}}"

        # Find all parameter blocks near the preset key
        key_pos = html.find(f"  {pk}:")
        if key_pos == -1:
            key_pos = html.find(f"'{pk}'") if pk != 'roman_zenner_shoptechblog' else html.find("roman_zenner_shoptechblog")

        if key_pos == -1:
            issues.append(f"Preset '{pk}' nicht in index.html gefunden")
            continue

        # Find parameters:{...} after the key
        param_start = html.find("parameters:{", key_pos)
        if param_start == -1 or param_start > key_pos + 2000:
            issues.append(f"Preset '{pk}': parameters nicht gefunden")
            continue

        param_end = html.find("}", param_start + 12)
        param_str = html[param_start + 12:param_end]

        # Parse JS object notation
        js_params = {}
        for match in re.finditer(r"(\w+):(\d+)", param_str):
            js_params[match.group(1)] = int(match.group(2))

        # Compare
        for k, yaml_val in yaml_params.items():
            js_val = js_params.get(k)
            if js_val is None:
                issues.append(f"  {pk}.{k}: fehlt in JS")
            elif js_val != yaml_val:
                issues.append(f"  {pk}.{k}: YAML={yaml_val}, JS={js_val}")

        for k in js_params:
            if k not in yaml_params:
                issues.append(f"  {pk}.{k}: in JS aber nicht in YAML")

    if issues:
        print("SYNC-PROBLEME gefunden:")
        for i in issues:
            print(i)

        if "--fix" in sys.argv:
            print("\n--- Fix: JS-Parameter aus YAML ---")
            for pk, preset in yaml_presets.items():
                params = preset["parameters"]
                js_obj = ",".join(f"{k}:{v}" for k, v in params.items())
                print(f"\n{pk}:")
                print(f"  parameters:{{{js_obj}}},")

        return 1
    else:
        print("YAML und JS sind synchron.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
