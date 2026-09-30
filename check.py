#!/usr/bin/env python3
"""Submission format check.

This does not grade your answers. It tells you what is missing.

    python3 check.py w03
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

SPEC = {
    "w02": ("w02-mapreduce", [
        ("task4.txt",      "optional task 4 output", False),
        ("observation.md", "what you found - optional", False),
    ]),
    "w03": ("w03-lsh", [
        ("crossover.json", "timings from task2_crossover.py", True),
        ("curve.md",       "the curve and where it broke", True),
        ("bench.txt",      "python3 bench.py --yours", True),
        ("observation.md", "2-3 lines per task", True),
    ]),
    "w04": ("w04-stream", [
        ("limits.json",    "timings from task2_limits.py", True),
        ("limits.md",      "the memory curve and where it broke", True),
        ("bench.txt",      "python3 bench.py --yours", True),
        ("observation.md", "2-3 lines per task", True),
    ]),
    "w05": ("w05-pagerank", [
        ("convergence.json", "runs from task2_convergence.py", True),
        ("convergence.md",   "the iteration curve", True),
        ("bench.txt",        "python3 bench.py --yours", True),
        ("observation.md",   "2-3 lines per task", True),
        ("task4.txt",        "optional task 4 output", False),
    ]),
    "w06": ("w06-apriori", [
        ("explosion.json", "runs from task2_explosion.py", True),
        ("explosion.md",   "the explosion curve", True),
        ("bench.txt",      "python3 bench.py --yours", True),
        ("observation.md", "2-3 lines per task", True),
        ("task4.txt",      "optional task 4 output", False),
    ]),
    "w07": ("w07-kmeans", [
        ("curse.json",     "runs from task2_curse.py", True),
        ("curse.md",       "the contrast curve", True),
        ("bench.txt",      "python3 bench.py --yours", True),
        ("observation.md", "2-3 lines per task", True),
    ]),
}


def check(week):
    if week not in SPEC:
        print(f"Unknown week: {week}")
        print("Try one of: " + " ".join(sorted(SPEC)))
        return 2

    folder, items = SPEC[week]
    out = os.path.join(HERE, folder, "out")
    print(f"== {folder}/out/ ==\n")

    if not os.path.isdir(out):
        print("  No out/ folder. Create it and put your results there:")
        print(f"      mkdir -p {folder}/out")
        return 1

    missing, weak = [], []
    for name, desc, required in items:
        path = os.path.join(out, name)
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size == 0:
                print(f"  [empty]   {name:20s} {desc}")
                missing.append(name)
            else:
                print(f"  [ok]      {name:20s} {desc}  ({size:,} bytes)")
        elif required:
            print(f"  [missing] {name:20s} {desc}")
            missing.append(name)
        else:
            print(f"  [optional]{name:20s} {desc}")

    obs = os.path.join(out, "observation.md")
    if os.path.exists(obs):
        text = open(obs, encoding="utf-8").read().strip()
        lines = [l for l in text.splitlines() if l.strip()]
        if len(text) < 120:
            weak.append("observation.md is very short - 2-3 lines per task, please")
        elif len(lines) < 3:
            weak.append("observation.md has fewer lines than there are tasks")

    print()
    for w in weak:
        print(f"  ! {w}")
    if missing:
        print(f"\n  {len(missing)} missing: {', '.join(missing)}")
        return 1
    if weak:
        print("\n  Format is fine. See the notes above.")
        return 0
    print("  Format check passed. Whether it is right is up to you.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    arg = sys.argv[1].lower()
    if not arg.startswith("w"):
        arg = "w" + arg.zfill(2)
    sys.exit(check(arg))
