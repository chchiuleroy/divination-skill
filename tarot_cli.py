#!/usr/bin/env python3
"""
tarot_cli.py — 塔羅牌抽牌 CLI
用法：
  python tarot_cli.py --spread single --question "今天適合行動嗎"
  python tarot_cli.py --spread three_card --variant 0
  python tarot_cli.py --spread celtic_cross
  python tarot_cli.py --list-spreads
  python tarot_cli.py --yes-no --question "這件事會成功嗎"
"""
import json
import random
import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).parent
CARDS_PATH = BASE / "tarot_cards.json"
SPREADS_PATH = BASE / "spreads.json"


def load_data():
    with open(CARDS_PATH, encoding="utf-8") as f:
        cards = json.load(f)["cards"]
    with open(SPREADS_PATH, encoding="utf-8") as f:
        spreads = {s["id"]: s for s in json.load(f)["spreads"]}
    return cards, spreads


def draw_cards(cards, n, allow_reversed=True):
    drawn = random.sample(cards, n)
    result = []
    for card in drawn:
        reversed_ = allow_reversed and (random.random() < 0.5)
        result.append({
            "id": card["id"],
            "name": card["name"],
            "name_en": card["name_en"],
            "arcana": card["arcana"],
            "suit": card["suit"],
            "element": card["element"],
            "astrology": card["astrology"],
            "reversed": reversed_,
            "keywords": card["keywords_reversed"] if reversed_ else card["keywords_upright"],
            "yes_no": card["yes_no"],
            "themes": card["themes"],
        })
    return result


def do_spread(cards, spreads, spread_id, variant_index=0, allow_reversed=True):
    spread = spreads.get(spread_id)
    if not spread:
        raise ValueError(f"找不到牌陣 '{spread_id}'，可用：{list(spreads.keys())}")

    positions = spread.get("positions")
    if not positions and "variants" in spread:
        variants = spread["variants"]
        if variant_index >= len(variants):
            variant_index = 0
        positions = variants[variant_index]["positions"]
        variant_name = variants[variant_index]["name"]
    else:
        variant_name = None

    drawn = draw_cards(cards, len(positions), allow_reversed)

    output = {
        "spread_id": spread_id,
        "spread_name": spread["name"],
        "variant": variant_name,
        "description": spread["description"],
        "positions": [],
    }
    for pos, card in zip(positions, drawn):
        output["positions"].append({
            "index": pos["index"],
            "position_name": pos["name"],
            "position_desc": pos["description"],
            "card": card,
        })
    return output


def do_yes_no(cards, question=""):
    card = draw_cards(cards, 1, allow_reversed=True)[0]
    answer_map = {"yes": "是 ✓", "no": "否 ✗", "neutral": "中性 ～"}
    return {
        "mode": "yes_no",
        "question": question,
        "card": card,
        "answer": answer_map.get(card["yes_no"], "中性 ～"),
    }


def list_spreads(spreads):
    rows = []
    for s in spreads.values():
        variants = ""
        if "variants" in s:
            vnames = " / ".join(v["name"] for v in s["variants"])
            variants = f"  變體：{vnames}"
        rows.append(f"  {s['id']:<15} {s['name']}（{s['card_count']} 張）{variants}")
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description="塔羅牌抽牌 CLI")
    parser.add_argument("--spread", default="three_card",
                        help="牌陣 ID（single/three_card/celtic_cross/horseshoe/relationship/year_ahead）")
    parser.add_argument("--variant", type=int, default=0,
                        help="三張牌陣的變體索引（0=過去現在未來, 1=狀況行動結果, 2=心身靈, 3=選項AB）")
    parser.add_argument("--question", default="", help="問題（可選）")
    parser.add_argument("--no-reversed", action="store_true", help="不使用逆位")
    parser.add_argument("--yes-no", action="store_true", help="是非題模式（單張）")
    parser.add_argument("--list-spreads", action="store_true", help="列出所有牌陣")
    parser.add_argument("--seed", type=int, default=None, help="隨機種子（可重現）")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    cards, spreads = load_data()

    if args.list_spreads:
        print("可用牌陣：")
        print(list_spreads(spreads))
        return

    allow_reversed = not args.no_reversed

    if args.yes_no:
        result = do_yes_no(cards, args.question)
    else:
        result = do_spread(cards, spreads, args.spread, args.variant, allow_reversed)

    if args.question:
        result["question"] = args.question

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
