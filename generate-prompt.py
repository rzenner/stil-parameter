#!/usr/bin/env python3
"""
generate-prompt.py — Generiert einen Drei-Schichten-Stilprompt aus presets.yaml.

Usage:
    python3 generate-prompt.py agenticpunk
    python3 generate-prompt.py roman_zenner_shoptechblog
    python3 generate-prompt.py hirnbrise
"""

import sys
import random
import yaml
from pathlib import Path

PRESETS_DIR = Path(__file__).parent / "presets"
LEGACY_YAML = Path(__file__).parent / "presets.yaml"

# Gruppierung der Dimensionen (gleiche Reihenfolge wie im Dashboard)
GROUPS = [
    ("Satzebene", ["sentence_length", "syntax_complexity", "short_sentence_frequency", "question_frequency"]),
    ("Absatz & Struktur", ["paragraph_length", "historical_depth", "anecdote_density"]),
    ("Haltung & Ton", ["opinion_strength", "hedging", "counterbalance", "confrontation"]),
    ("Stilmittel", ["irony_edge", "metaphor_density", "cultural_references", "antithesis_density"]),
    ("Tempo & Rhythmus", ["pacing", "rhythm_variation"]),
    ("Register & Ansprache", ["vocabulary_register", "anglicism_density", "reader_address", "ending_type", "gendering"]),
]


def load_yaml():
    """Lädt shared config + alle Preset-Dateien aus presets/ Ordner.
    Fallback: monolithische presets.yaml falls presets/ nicht existiert."""
    if PRESETS_DIR.is_dir():
        # Load shared config (dimensions, taboo_catalog)
        shared_path = PRESETS_DIR / "_shared.yaml"
        if not shared_path.exists():
            print(f"Fehlend: {shared_path}", file=sys.stderr)
            sys.exit(1)
        with open(shared_path, "r") as f:
            data = yaml.safe_load(f)
        # Load each preset file
        data["presets"] = {}
        for p in sorted(PRESETS_DIR.glob("*.yaml")):
            if p.name.startswith("_"):
                continue
            with open(p, "r") as f:
                preset_data = yaml.safe_load(f)
            data["presets"].update(preset_data)
    else:
        # Fallback: legacy monolithic file
        with open(LEGACY_YAML, "r") as f:
            data = yaml.safe_load(f)
    validate(data)
    return data


def validate(data):
    """Prüft YAML-Struktur auf häufige Fehler."""
    errors = []
    if "dimensions" not in data:
        errors.append("Fehlender Key: 'dimensions'")
    if "presets" not in data:
        errors.append("Fehlender Key: 'presets'")

    dims = data.get("dimensions", {})
    for dk, dim in dims.items():
        if "label" not in dim:
            errors.append(f"Dimension '{dk}': fehlendes 'label'")
        if "instructions" in dim:
            instr = dim["instructions"]
            for level in [1, 2, 3, 4, 5]:
                if level not in instr:
                    errors.append(f"Dimension '{dk}': fehlende instruction für Stufe {level}")

    presets = data.get("presets", {})
    dim_keys = set(dims.keys())
    for pk, preset in presets.items():
        if "label" not in preset:
            errors.append(f"Preset '{pk}': fehlendes 'label'")
        if "parameters" not in preset:
            errors.append(f"Preset '{pk}': fehlende 'parameters'")
        else:
            param_keys = set(preset["parameters"].keys())
            missing = dim_keys - param_keys
            if missing:
                errors.append(f"Preset '{pk}': fehlende Parameter: {', '.join(sorted(missing))}")
            for k, v in preset["parameters"].items():
                if not isinstance(v, (int, float)) or v < 1 or v > 5:
                    errors.append(f"Preset '{pk}', Parameter '{k}': Wert {v} außerhalb 1–5")

    if errors:
        print("YAML-Validierung fehlgeschlagen:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)


def build_prompt(preset_key: str) -> str:
    data = load_yaml()
    dims = data["dimensions"]
    presets = data["presets"]

    if preset_key not in presets:
        available = ", ".join(presets.keys())
        print(f"Preset '{preset_key}' nicht gefunden. Verfügbar: {available}", file=sys.stderr)
        sys.exit(1)

    preset = presets[preset_key]
    label = preset["label"]
    params = preset["parameters"]

    # --- Schicht A: Anker-Texte (2 zufällig ausgewählt für Varianz) ---
    anchor_texts = preset.get("anchor_texts", [])
    # Fallback: altes Format (anchor_text als String)
    if not anchor_texts and preset.get("anchor_text"):
        anchor_texts = [{"text": preset["anchor_text"], "source": preset.get("anchor_source", ""), "topic": ""}]

    anchor_block = ""
    if anchor_texts:
        # Wähle 2 zufällige Anker-Texte (oder alle, wenn weniger als 2)
        selected = random.sample(anchor_texts, min(2, len(anchor_texts)))
        quotes = "\n\n".join(f"> {a['text'].strip()}" for a in selected)
        topics = ", ".join(a.get("topic", "") for a in selected if a.get("topic"))
        anchor_block = f"""
## Referenz-Stil (schreibe in diesem Ton)

Die folgenden Absätze zeigen den Zielstil an unterschiedlichen Themen ({topics}). Orientiere dich an Tonfall, Satzrhythmus, Haltung und Wortwahl — nicht am Inhalt.

{quotes}
"""

    # --- Schicht B: Micro-Instructions ---
    param_block = ""
    for group_label, dim_keys in GROUPS:
        param_block += f"\n### {group_label}\n"
        for dk in dim_keys:
            val = params.get(dk, 3)
            dim_def = dims.get(dk, {})
            dim_label = dim_def.get("label", dk)
            instructions = dim_def.get("instructions", {})
            instr = instructions.get(val, instructions.get(3, ""))
            if isinstance(instr, str):
                instr = instr.strip()
            param_block += f"\n**{dim_label}** ({val}/5):\n{instr}\n"

    # --- Schicht C: Phrasen, Taboo-Topics, Konflikte ---
    phrase_block = ""
    if preset.get("include_phrases"):
        phrase_block += "\n## Phrasen-Bausteine (1–2 pro Text natürlich einbauen)\n"
        phrase_block += "\n".join(f'- "{p}"' for p in preset["include_phrases"]) + "\n"
    if preset.get("exclude_phrases"):
        phrase_block += "\n## Verbotene Phrasen (nie verwenden)\n"
        phrase_block += "\n".join(f'- "{p}"' for p in preset["exclude_phrases"]) + "\n"
    if preset.get("include_terms"):
        phrase_block += "\n## Bevorzugtes Vokabular (natürlich einstreuen)\n"
        phrase_block += "\n".join(f"- {t}" for t in preset["include_terms"]) + "\n"
    if preset.get("exclude_terms"):
        phrase_block += "\n## Verbotene Wörter (harte Regel)\n"
        phrase_block += "\n".join(f"- {t}" for t in preset["exclude_terms"]) + "\n"

    taboo_block = ""
    if preset.get("taboo_topics"):
        catalog = data.get("taboo_catalog", {})
        taboo_block = "\n## Themen-Ausschlüsse (Taboo Topics)\nFolgende Themenbereiche und ihre typische Sprache NICHT verwenden:\n"
        for topic in preset["taboo_topics"]:
            info = catalog.get(topic, {})
            desc = info.get("description", "")
            examples = info.get("examples", "")
            taboo_block += f"- **{topic}**: {desc}. {examples}\n"

    # --- Zusammenbauen ---
    prompt = f"""# Stil-Anweisung: {label}

Du schreibst im Stil-Preset **{label}**. Befolge die folgenden Anweisungen exakt.
{anchor_block}
## Stil-Anweisungen
{param_block}
{phrase_block}{taboo_block}
## Wichtig
- Die Anweisungen oben sind konkrete Regeln — befolge sie wörtlich. Zählbare Angaben (Satzlänge, Häufigkeiten) sind Richtwerte mit ±10% Toleranz.
- Phrasen-Bausteine sind Vorschläge — nutze 1–2 pro Text, nicht alle auf einmal.
- Verbotene Wörter und Phrasen sind harte Regeln. Verwende sie nie, auch nicht in Varianten.
- Taboo Topics: Vermeide nicht nur die Begriffe, sondern die gesamte Metaphorik des Themenbereichs.
- Wenn Anweisungen in Spannung zueinander stehen (z.B. kurze Sätze + hohe Satzkomplexität), löse das kreativ auf statt eine Seite zu ignorieren."""

    return prompt.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate-prompt.py <preset_key>", file=sys.stderr)
        print("  Preset keys: agenticpunk, roman_zenner_shoptechblog, hirnbrise", file=sys.stderr)
        sys.exit(1)

    print(build_prompt(sys.argv[1]))
