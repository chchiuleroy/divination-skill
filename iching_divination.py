# -*- coding: utf-8 -*-
"""
易經占卜系統 I Ching Divination System
三硬幣法生成卦象，解讀本卦、動爻、之卦
"""

import sys
import random
import re
from pathlib import Path

# Windows 終端 UTF-8 輸出
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ICHING_DIR = Path(__file__).parent / "iching"

# ─────────────────────────────────────────────
# 八卦定義 Trigram Definitions
# 二進制表示：bit0=初爻, bit1=二爻, bit2=三爻 (1=陽, 0=陰)
# ─────────────────────────────────────────────
TRIGRAMS = {
    7: {"name": "Qian", "chinese": "乾", "symbol": "☰", "nature": "Heaven 天"},
    0: {"name": "Kun",  "chinese": "坤", "symbol": "☷", "nature": "Earth 地"},
    1: {"name": "Zhen", "chinese": "震", "symbol": "☳", "nature": "Thunder 雷"},
    2: {"name": "Kan",  "chinese": "坎", "symbol": "☵", "nature": "Water 水"},
    4: {"name": "Gen",  "chinese": "艮", "symbol": "☶", "nature": "Mountain 山"},
    6: {"name": "Xun",  "chinese": "巽", "symbol": "☴", "nature": "Wind 風"},
    5: {"name": "Li",   "chinese": "離", "symbol": "☲", "nature": "Fire 火"},
    3: {"name": "Dui",  "chinese": "兌", "symbol": "☱", "nature": "Lake 澤"},
}

# ─────────────────────────────────────────────
# 六十四卦查詢表 (King Wen sequence)
# 行=上卦, 列=下卦
# 順序: 乾(7) 坤(0) 震(1) 坎(2) 艮(4) 巽(6) 離(5) 兌(3)
# ─────────────────────────────────────────────
TRIGRAM_ORDER = [7, 0, 1, 2, 4, 6, 5, 3]

HEXAGRAM_TABLE = [
    #       Qian Kun  Zhen Kan  Gen  Xun  Li   Dui
    #        (7)  (0)  (1)  (2)  (4)  (6)  (5)  (3)
    [ 1,  12,  25,   6,  33,  44,  13,  10],  # 上乾 Qian
    [11,   2,  24,   7,  15,  20,  36,  19],  # 上坤 Kun
    [34,  16,  51,  40,  62,  32,  55,  54],  # 上震 Zhen
    [ 5,   8,   3,  29,  39,  48,  63,  60],  # 上坎 Kan
    [26,  23,  27,   4,  52,  18,  22,  41],  # 上艮 Gen
    [ 9,  20,  42,  59,  53,  57,  37,  61],  # 上巽 Xun
    [14,  35,  21,  64,  56,  50,  30,  38],  # 上離 Li
    [43,  45,  17,  47,  31,  28,  49,  58],  # 上兌 Dui
]

# 爻位名稱
LINE_POSITIONS = {1: "初", 2: "二", 3: "三", 4: "四", 5: "五", 6: "上"}
LINE_POS_EN = {1: "beginning", 2: "second place", 3: "third place",
               4: "fourth place", 5: "fifth place", 6: "top"}


def get_hexagram_number(upper_trig: int, lower_trig: int) -> int:
    """由上下卦查詢卦號"""
    upper_idx = TRIGRAM_ORDER.index(upper_trig)
    lower_idx = TRIGRAM_ORDER.index(lower_trig)
    return HEXAGRAM_TABLE[upper_idx][lower_idx]


def cast_lines() -> list[int]:
    """
    三硬幣法投擲六爻
    正面=3, 反面=2, 三枚硬幣之和:
      6 = 老陰 (動爻, 陰→陽)
      7 = 少陽 (靜爻)
      8 = 少陰 (靜爻)
      9 = 老陽 (動爻, 陽→陰)
    返回 [初爻, 二爻, 三爻, 四爻, 五爻, 上爻]
    """
    return [sum(random.choice([2, 3]) for _ in range(3)) for _ in range(6)]


LINE_DISPLAY = {
    6: ("─── × ───", False, True,  "老陰 Changing Yin"),
    7: ("─────────", True,  False, "少陽 Young Yang"),
    8: ("────  ────", False, False, "少陰 Young Yin"),
    9: ("─── ○ ───", True,  True,  "老陽 Changing Yang"),
}


def lines_to_trigram(lines3: list[int]) -> int:
    """三爻值轉八卦二進制值"""
    result = 0
    for i, v in enumerate(lines3):
        if LINE_DISPLAY[v][1]:  # is_yang
            result |= (1 << i)
    return result


def get_changed_line_value(v: int) -> int:
    """動爻變化：老陽→少陰, 老陰→少陽"""
    if v == 9:
        return 8
    if v == 6:
        return 7
    return v


def find_hexagram_file(number: int) -> Path | None:
    """找對應卦號的 md 檔"""
    matches = list(ICHING_DIR.glob(f"{number:02d}_*.md"))
    return matches[0] if matches else None


def read_hexagram(number: int) -> str:
    """讀取卦辭 md 檔"""
    fp = find_hexagram_file(number)
    if fp:
        return fp.read_text(encoding="utf-8")
    return ""


def extract_title(content: str) -> str:
    """提取標題"""
    match = re.search(r"^##\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_section(content: str, section: str) -> str:
    """提取 THE JUDGMENT / THE IMAGE 段落"""
    pattern = rf"THE {section}\s*\n+(.*?)(?=\nTHE [A-Z]+|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        text = match.group(1).strip()
        return text
    return ""


def extract_line_text(content: str, line_num: int, is_yang: bool) -> str:
    """提取特定爻辭"""
    yang_or_yin = "Nine|Six"
    pos = LINE_POS_EN[line_num]
    if line_num == 1:
        pattern = rf"(?:Nine|Six) at the beginning means:\s*\n+(.*?)(?=\n(?:Nine|Six) (?:at|in)|When all|\Z)"
    elif line_num == 6:
        pattern = rf"(?:Nine|Six) at the top means:\s*\n+(.*?)(?=\nWhen all|\Z)"
    else:
        pattern = rf"(?:Nine|Six) in the {pos} means:\s*\n+(.*?)(?=\n(?:Nine|Six) (?:at|in)|When all|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def pos_name(i):
    return ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"][i]


def print_hexagram_visual(lines: list[int], label: str):
    """列印卦象"""
    print(f"\n  ╔══ {label}")
    for i in range(5, -1, -1):
        sym, is_yang, is_changing, desc = LINE_DISPLAY[lines[i]]
        change_mark = " ←變" if is_changing else ""
        print(f"  ║  {pos_name(i)}  {sym}{change_mark}")
    print("  ╚══════════════════")


def interpret_changing_lines_rule(n_changing: int) -> str:
    """根據動爻數量說明解讀重點"""
    rules = {
        0: "無動爻：專注本卦之卦辭與象辭",
        1: "一爻動：重點在本卦卦辭＋動爻爻辭",
        2: "二爻動：本卦卦辭＋兩動爻爻辭（以上位爻為主）",
        3: "三爻動：本卦與之卦卦辭並重",
        4: "四爻動：以之卦為主，讀之卦兩靜爻爻辭",
        5: "五爻動：以之卦為主，讀之卦一靜爻爻辭",
        6: "六爻全動：專注之卦卦辭（或六龍/六牛特別卦辭）",
    }
    return rules.get(n_changing, "")


def divine(question: str):
    """主占卜函數"""
    print("\n" + "═" * 55)
    print("  易經占卜  I Ching Divination")
    print("═" * 55)
    print(f"  問題：{question}")
    print("═" * 55)

    # 投擲六爻
    lines = cast_lines()

    # 本卦 Primary hexagram
    lower_trig = lines_to_trigram(lines[0:3])
    upper_trig = lines_to_trigram(lines[3:6])
    primary_num = get_hexagram_number(upper_trig, lower_trig)

    # 動爻
    changing = [i + 1 for i, v in enumerate(lines) if LINE_DISPLAY[v][2]]

    # 之卦 Changed hexagram
    changed_lines = [get_changed_line_value(v) for v in lines]
    c_lower = lines_to_trigram(changed_lines[0:3])
    c_upper = lines_to_trigram(changed_lines[3:6])
    changed_num = get_hexagram_number(c_upper, c_lower) if changing else None

    # ── 顯示卦象 ──────────────────────────────
    print_hexagram_visual(lines, f"本卦 Primary  #{primary_num:02d}")

    up = TRIGRAMS[upper_trig]
    lo = TRIGRAMS[lower_trig]
    print(f"\n  上卦 Upper: {up['symbol']} {up['chinese']} ({up['nature']})")
    print(f"  下卦 Lower: {lo['symbol']} {lo['chinese']} ({lo['nature']})")

    if changing:
        print(f"\n  動爻 Changing Lines: {', '.join(f'第{l}爻' for l in changing)}")
        print_hexagram_visual(changed_lines, f"之卦 Changed  #{changed_num:02d}")
        cu = TRIGRAMS[c_upper]
        cl = TRIGRAMS[c_lower]
        print(f"\n  上卦 Upper: {cu['symbol']} {cu['chinese']} ({cu['nature']})")
        print(f"  下卦 Lower: {cl['symbol']} {cl['chinese']} ({cl['nature']})")

    print(f"\n  解讀原則：{interpret_changing_lines_rule(len(changing))}")

    # ── 本卦解讀 ──────────────────────────────
    print("\n" + "─" * 55)
    primary_content = read_hexagram(primary_num)
    title = extract_title(primary_content)
    print(f"  本卦 PRIMARY HEXAGRAM")
    print(f"  {title}")
    print("─" * 55)

    judgment = extract_section(primary_content, "JUDGMENT")
    if judgment:
        # 只取卦辭正文（前幾行）+ 首段解釋
        lines_j = judgment.split("\n")
        # 找到第一個空行分隔卦辭正文與解釋
        short_text = []
        blank_count = 0
        for ln in lines_j:
            if ln.strip() == "":
                blank_count += 1
                if blank_count >= 2:
                    break
            short_text.append(ln)
        print("\n  THE JUDGMENT:")
        print("  " + "\n  ".join(short_text[:20]))

    image = extract_section(primary_content, "IMAGE")
    if image:
        lines_i = image.split("\n")[:10]
        print("\n  THE IMAGE:")
        print("  " + "\n  ".join(lines_i))

    # ── 動爻爻辭 ──────────────────────────────
    if changing:
        print("\n" + "─" * 55)
        print("  動爻爻辭 CHANGING LINES")
        print("─" * 55)
        for ln_num in changing:
            is_yang = LINE_DISPLAY[lines[ln_num - 1]][1]
            text = extract_line_text(primary_content, ln_num, is_yang)
            if text:
                # 只取前兩段
                paras = [p.strip() for p in text.split("\n\n") if p.strip()]
                short = "\n\n".join(paras[:2])
                print(f"\n  第{ln_num}爻 (Line {ln_num} / {pos_name(ln_num-1)}):")
                print("  " + short.replace("\n", "\n  "))

    # ── 之卦解讀 ──────────────────────────────
    if changed_num and changed_num != primary_num:
        print("\n" + "─" * 55)
        changed_content = read_hexagram(changed_num)
        changed_title = extract_title(changed_content)
        print(f"  之卦 CHANGED HEXAGRAM")
        print(f"  {changed_title}")
        print("─" * 55)

        c_judgment = extract_section(changed_content, "JUDGMENT")
        if c_judgment:
            lines_cj = c_judgment.split("\n")
            short_cj = []
            blank_count = 0
            for ln in lines_cj:
                if ln.strip() == "":
                    blank_count += 1
                    if blank_count >= 2:
                        break
                short_cj.append(ln)
            print("\n  THE JUDGMENT:")
            print("  " + "\n  ".join(short_cj[:20]))

        c_image = extract_section(changed_content, "IMAGE")
        if c_image:
            lines_ci = c_image.split("\n")[:10]
            print("\n  THE IMAGE:")
            print("  " + "\n  ".join(lines_ci))

    print("\n" + "═" * 55)
    return primary_num, changed_num, changing


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        try:
            question = input("請輸入您的問題 Enter your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            question = "今日運勢如何？"
    if not question:
        question = "今日運勢如何？"
    divine(question)
