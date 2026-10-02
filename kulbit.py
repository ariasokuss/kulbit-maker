"""Kulbit Maker — генератор смешных названий для команды."""

import argparse
import json
import random
import sys
from difflib import SequenceMatcher
from pathlib import Path

WORDS_FILE = Path(__file__).with_name("words.json")

# Вероятности шаблонов
P_PREPOSITION = 0.45  # «абманка для абамки»
P_ADJECTIVE = 0.15  # «майнкрафтовая абамка»
# остальное — просто два слова: «майнкрафт кульбит»
P_SOUNDALIKE = 0.25  # пара созвучных слов: «абманка для абамки»
P_SEQUEL = 0.05  # редкая приписка: «сквиш против доты 2»

VOWELS = "аеёиоуыэюя"


def load(path=WORDS_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def similarity(a, b):
    return SequenceMatcher(None, a["nom"], b["nom"]).ratio()


def pick_pair(words, rng):
    """Два разных слова; иногда специально подбираем созвучные."""
    first = rng.choice(words)
    others = [w for w in words if w is not first]
    if rng.random() < P_SOUNDALIKE:
        best = max(others, key=lambda w: similarity(first, w))
        if similarity(first, best) >= 0.6:
            return first, best
    return first, rng.choice(others)


def fix_preposition(prep, next_word):
    """о → об перед гласной, с → со перед «с»/«з»/«ш» + согласная."""
    first = next_word[0]
    if prep == "о" and first in VOWELS:
        return "об"
    if prep == "с" and first in "сзш" and len(next_word) > 1 and next_word[1] not in VOWELS:
        return "со"
    return prep


def make_name(data, rng=random):
    words = data["words"]
    a, b = pick_pair(words, rng)
    roll = rng.random()

    if roll < P_PREPOSITION:
        prep = rng.choice(data["prepositions"])
        tail = b[prep["case"]]
        name = f"{a['nom']} {fix_preposition(prep['word'], tail)} {tail}"
    elif roll < P_PREPOSITION + P_ADJECTIVE and any("adj" in w for w in words):
        adj_word = rng.choice([w for w in words if "adj" in w])
        noun = rng.choice([w for w in words if w is not adj_word])
        name = f"{adj_word['adj'][noun['gender']]} {noun['nom']}"
    else:
        name = f"{a['nom']} {b['nom']}"

    if rng.random() < P_SEQUEL:
        suffix = rng.choice(data["sequels"])
        name += suffix if suffix[0] in ":+ " else f" {suffix}"
    return name


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Генератор смешных названий команды")
    parser.add_argument("-n", type=int, default=1, help="сколько названий выдать")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter — следующее название, q — выход")
    parser.add_argument("--seed", type=int, help="сид для воспроизводимости")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    data = load()

    if args.interactive:
        print("Enter — ещё, q — выход")
        while True:
            print(f"  >> {make_name(data, rng)}")
            if input().strip().lower() in ("q", "й", "exit"):
                break
        return

    seen = set()
    attempts = 0
    while len(seen) < args.n and attempts < args.n * 50:
        attempts += 1
        name = make_name(data, rng)
        if name not in seen:
            seen.add(name)
            print(name)


if __name__ == "__main__":
    main()
