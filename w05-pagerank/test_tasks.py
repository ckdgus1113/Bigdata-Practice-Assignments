#!/usr/bin/env python3
"""Week 5 · does your work pass?"""
import argparse, importlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results = []


def record(task, name, status, detail=""):
    results.append((task, name, status, detail))
    print({PASS: "  ok  ", FAIL: " FAIL ", SKIP: " skip "}[status]
          + f" [{task}] {name}" + (f"  - {detail}" if detail else ""))


def test_task1():
    try:
        m = importlib.import_module("task1_pagerank")
    except Exception as e:
        return record(1, "task1_pagerank.py imports", FAIL, repr(e))
    try:
        rc = m.verify()
    except Exception as e:
        return record(1, "verify runs", FAIL, repr(e))
    record(1, "all seven checks", PASS if rc == 0 else FAIL)


def test_task2():
    path = os.path.join(OUT, "convergence.json")
    if not os.path.exists(path):
        return record(2, "out/convergence.json exists", FAIL,
                      "run task2_convergence.py")
    data = json.load(open(path))
    betas = sorted({r["beta"] for r in data.get("runs", [])})
    record(2, "A1 five or more betas", PASS if len(betas) >= 5 else FAIL, str(betas))
    sizes = sorted({r.get("nodes") for r in data.get("runs", [])})
    record(2, "A4 two or more graph sizes", PASS if len(sizes) >= 2 else FAIL,
           str(sizes))
    tols = sorted({r.get("tol") for r in data.get("runs", [])})
    record(2, "A5 two or more tolerances", PASS if len(tols) >= 2 else FAIL, str(tols))
    record(2, "A7 machine recorded",
           PASS if data.get("machine", {}).get("platform") else FAIL)
    record(2, "out/convergence.md exists",
           PASS if os.path.exists(os.path.join(OUT, "convergence.md")) else FAIL)


def test_task3():
    try:
        bench = importlib.import_module("bench")
        mod = importlib.import_module("task3_sparse")
    except Exception as e:
        return record(3, "modules import", FAIL, repr(e))
    graph = bench.build()
    base = bench.run(mod.DenseMatrix, "baseline", graph)
    try:
        mine = bench.run(mod.YourPageRank, "yours", graph, base["ranks"])
    except NotImplementedError:
        return record(3, "YourPageRank implemented", FAIL, "still a stub")
    except Exception as e:
        return record(3, "YourPageRank runs", FAIL, repr(e))
    record(3, "R3 ranks within 1e-9", PASS if mine["worst"] <= 1e-9 else FAIL,
           f"worst {mine['worst']:.2e}")
    mem = base["floats"] / max(mine["floats"], 1)
    record(3, "R4 less memory", PASS if mem > 2 else FAIL, f"{mem:.0f}x")
    record(3, "R5 teleport argument in observation.md", SKIP, "graded by a human")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=int, choices=[1, 2, 3])
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for n, fn in [(1, test_task1), (2, test_task2), (3, test_task3)]:
        if a.task in (None, n):
            print(f"\n=== Task {n}")
            fn()
    print()
    failed = sum(1 for *_, s, _ in results if s == FAIL)
    skipped = sum(1 for *_, s, _ in results if s == SKIP)
    print(f"  {len(results) - failed - skipped} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
