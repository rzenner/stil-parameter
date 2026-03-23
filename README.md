# Stil-Parameter

Parametrisierte Stilsteuerung für LLM-generierte Texte. 22 Dimensionen, 3 Presets, Micro-Instructions statt vager Beschreibungen.

## Was es tut

Stil-Parameter macht Schreibstile reproduzierbar. Statt einem LLM zu sagen "schreibe kantig, aber fundiert" (was jedes Mal anders interpretiert wird), definiert das System 22 numerische Parameter mit konkreten Handlungsanweisungen pro Stufe.

**Drei Schichten:**
1. **Anker-Texte** — echte Referenzabsätze die den Zielstil demonstrieren (Few-Shot, rotierend)
2. **Micro-Instructions** — 110 konkrete Regeln (22 Parameter × 5 Stufen), z.B. "Maximal 1 Hedge-Phrase pro 500 Wörter"
3. **Phrasen & Taboo-Topics** — Include/Exclude-Listen und Themen-Ausschlüsse

## Installation

```bash
git clone https://github.com/rzenner/stil-parameter.git
cd stil-parameter
pip3 install pyyaml
```

### Dashboard (Browser-UI)

```bash
open index.html
```

Single-File HTML-App, keine Dependencies. Zwei Tabs:
- **Vorschau** — 22 Slider mit Live-Demo-Text der sich in Echtzeit verändert
- **Analyse** — Text einfügen, gegen Preset analysieren, Abweichungen erkennen

### Prompt-Generierung (CLI)

```bash
python3 generate-prompt.py agenticpunk
python3 generate-prompt.py roman_zenner_shoptechblog
python3 generate-prompt.py hirnbrise
```

Gibt den vollständigen Drei-Schichten-Prompt auf stdout aus. Validiert die YAML-Struktur beim Start.

### Sync-Check

```bash
python3 sync-check.py        # Prüft ob YAML und JS synchron sind
python3 sync-check.py --fix  # Zeigt die korrekten JS-Werte zum Copy-Paste
```

## Die 22 Parameter

| Kategorie | Parameter | Skala |
|---|---|---|
| **Satzebene** | Satzlänge, Satzkomplexität, Kurzsatz-Frequenz, Fragen-Frequenz | 1–5 |
| **Absatz & Struktur** | Absatzlänge, Historische Einordnung, Anekdoten-Dichte | 1–5 |
| **Haltung & Ton** | Meinungsstärke, Hedging, Relativierung, Konfrontation | 1–5 |
| **Stilmittel** | Ironie-Schärfe, Metaphern-Dichte, Kulturelle Referenzen, Antithesen | 1–5 |
| **Tempo & Rhythmus** | Tempo, Rhythmus-Variation | 1–5 |
| **Register & Ansprache** | Vokabular-Register, Anglizismen, Leseransprache, Textende-Typ, Gendern | 1–5 |

Jeder Parameter hat für jede Stufe (1–5) eine konkrete Micro-Instruction mit Zahlen, Regeln und Beispielen. Definiert in `presets.yaml`.

## Presets

| Preset | Stil | Kalibriert gegen |
|---|---|---|
| `roman_zenner_shoptechblog` | Analytisch, hedgend, historisch einordnend | 8 pre-LLM Artikel (2020–2024) |
| `agenticpunk` | Meinungsstark, konfrontativ, schnell | Stilprofil + 7 Artikel |
| `hirnbrise` | Persönlich, erzählerisch, kulturelle Referenzen | Stilprofil (Kalibrierung offen) |

## Dateien

| Datei | Beschreibung |
|---|---|
| `index.html` | Dashboard (Browser-UI, Single-File, ~80 KB) |
| `presets.yaml` | Dimensionen, Micro-Instructions, Anker-Texte, Presets |
| `generate-prompt.py` | CLI-Tool: generiert Drei-Schichten-Prompt aus Preset |
| `sync-check.py` | Prüft Synchronität zwischen YAML und JS |

## Wie Micro-Instructions funktionieren

**Vorher** (deskriptiv):
```
Hedging: 2/5 → Eher kein Hedging
```

**Nachher** (instruktionsbasiert):
```
Hedging (2/5):
Fast kein Hedging. Maximal 1 Hedge-Phrase pro 500 Wörter.
Nur bei genuinen Zukunftsprognosen. Verboten als Höflichkeits-Hedge.
Erlaubt: "Das wird sich zeigen." Verboten: "Man könnte argumentieren, dass..."
```

## Kalibrierung

Preset-Werte werden nicht geschätzt, sondern gegen echte Texte gemessen. Das ShopTechBlog-Preset wurde gegen 8 handgeschriebene Artikel (2020–2024) kalibriert — 9 von 15 messbaren Parametern mussten korrigiert werden.

Die Textanalyse im Dashboard nutzt Heuristiken (Regex, Wortlisten, Satzlängen-Statistik) für ~15 automatisch messbare Parameter. 7 Parameter (Metaphern, kulturelle Referenzen, historische Tiefe, Anekdoten, Textende, Gendern, Vokabular-Register) erfordern manuelle Einschätzung.

## Lizenz

MIT
