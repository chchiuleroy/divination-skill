# divination — 塔羅 × 易經 雙系統聯合占卜 Skill

A [Claude Code](https://claude.ai/code) skill that performs dual-system divination by combining **Tarot** and **I Ching (易經)** readings, then synthesizing them through an Ensemble logic to surface resonance and contradiction between the two oracles.

---

## Features

- **Dual-system simultaneous reading** — Tarot and I Ching are drawn independently, then compared
- **Ensemble logic** — agreement = strong signal; contradiction = highest information content
- **Smart spread selection** — automatically picks the appropriate Tarot spread based on question type (6 spreads available)
- **Changing lines analysis** — I Ching moving yao (動爻) mapped to the Tarot's dynamic positions
- **Full 78-card Tarot** — Major Arcana (22) + Minor Arcana (56), with reversed cards
- **All 64 Hexagrams** — Wilhelm/Baynes translation with full yao texts

---

## Architecture

```
divination skill (skill.md)
├── tarot_cli.py          — Tarot CLI: draws cards, returns structured JSON
│   ├── tarot_cards.json  — 78-card dataset (names, keywords, elements, astrology)
│   └── spreads.json      — 6 spread definitions with positional meanings
└── iching_divination.py  — I Ching CLI: three-coin method, hexagram lookup
    └── iching/           — 64 markdown files (one per hexagram, Wilhelm text)
```

---

## Files Required

Upload the following files to your repository:

| File / Folder | Description |
|---|---|
| `skill.md` | Skill definition (triggers, execution flow, output format) |
| `tarot_cli.py` | Tarot card drawing CLI |
| `tarot_cards.json` | 78-card dataset with Chinese/English names, keywords, elements, astrology |
| `spreads.json` | 6 Tarot spread definitions |
| `iching_divination.py` | I Ching divination CLI (three-coin method) |
| `iching/` | 64 hexagram markdown files (Wilhelm/Baynes translation) |

---

## Usage

Once installed, trigger the skill in Claude Code:

```
/divination 換工作好嗎？
```

Or natural language:
```
雙系統問一下這段感情
塔羅加易經看看這個決定
```

The skill will:
1. Select the appropriate Tarot spread based on your question
2. Run `tarot_cli.py` and `iching_divination.py` simultaneously
3. Perform Ensemble cross-analysis (resonance + contradiction)
4. Output an integrated reading in the structured format below

---

## Tarot Spreads

| Spread | Use Case |
|---|---|
| `single` | Daily guidance / quick answer |
| `three_card` (variant 0) | Past · Present · Future |
| `three_card` (variant 1) | Situation · Action · Outcome |
| `three_card` (variant 2) | Mind · Body · Spirit |
| `three_card` (variant 3) | Option A vs Option B |
| `celtic_cross` | Deep analysis / complex situations |
| `horseshoe` | Multi-angle overview |
| `relationship` | Romance / interpersonal dynamics |
| `year_ahead` | Full-year monthly spread |
| `--yes-no` | Quick yes/no question |

---

## Ensemble Logic

| Scenario | Meaning |
|---|---|
| Both systems agree | Strong signal — act with confidence |
| Systems contradict | Highest information — reveals gap between inner state and external timing |

Cross-analysis rules:
- **Major Arcana ↔ Hexagram** — philosophical/archetypal layer comparison
- **Minor Arcana ↔ Yao texts** — situational detail supplement
- **Moving yao (動爻) ↔ Tarot action position** — check for directional conflict
- **Resultant hexagram (之卦) ↔ Tarot outcome card** — trajectory alignment

---

## Output Format

```
## 🔮☯️ 雙系統聯合解讀：[question]

### 塔羅｜[spread name]
① [position]
   🃏 [card name] ([name_en]) [🔄 if reversed]
   元素：[element]｜星象：[astrology]
   關鍵字：[keywords]
   📖 [2-3 sentence reading]

### 易經｜第 XX 卦 [name]（[upper trigram][lower trigram]）
本卦：[name] — [one-line summary]
動爻：[yao number]
變卦：[number] [name] — [directional summary]
[yao text] → [2-sentence interpretation]

### ⚡ 合卦
**共鳴（強訊號）**
| 塔羅 | 易經 | 說的同一件事 |
|---|---|---|

**矛盾（最有價值）**
> [contradiction and what it reveals]

### ✨ 整合建議
[3-5 sentence integrated guidance]
```

---

## Installation

1. Copy `skill.md` to `skill.md`
2. Place `tarot_cli.py`, `tarot_cards.json`, `spreads.json` in your working directory
3. Place `iching_divination.py` and the `iching/` folder in your working directory
4. Update the file paths in `skill.md` to match your environment

> **Default paths** (Windows): `C:/Users/<user>/tarot_cli.py`, `C:/Users/<user>/iching_divination.py`

---

## Data Sources

### I Ching (易經)

The 64 hexagram texts in `iching/` are based on the **Wilhelm/Baynes translation** of the I Ching (*I Ching: Or, Book of Changes*, Richard Wilhelm & Cary F. Baynes). The Wilhelm/Baynes translation entered the public domain in 2020.

Structured hexagram dataset sourced from:

> **adamblvck/iching-wilhelm-dataset** — MIT License
> Copyright (c) Adam Blvck
> https://github.com/adamblvck/iching-wilhelm-dataset/tree/master/data
> Dataset of all 64 hexagrams with judgments, images, and line texts from the Wilhelm translation.

### Tarot

`tarot_cards.json` is a custom-compiled dataset of the standard **78-card Rider-Waite-Smith Tarot** system. Card names, elemental correspondences, astrological associations, and divinatory keywords are drawn from the public domain Rider-Waite tradition. No third-party dataset is used.

---

## Notes

- Divination is a reflective tool, not a prediction system
- For health, legal, or major financial decisions, consult a professional
- I Ching: avoid repeating the same question on the same day
- If the user is emotionally sensitive, the skill softens contradiction signals automatically

---

## Related Skills

- [`tarot`](./../tarot/) — Tarot-only readings with all spreads
- [`iching`](../../iching.skill) — I Ching-only divination
