# Task 2 · How Long Does It Take to Converge, and on What?

**File** — `task2_convergence.py`
**Theory** — §5.1, §5.2
**Kind** — **measurement. Timings are about your machine; iteration counts are not.**

---

## Why this task exists

The textbook says PageRank converges. It does not say in how many iterations,
because that depends on `beta`, on the graph, and on what you call "converged".

This task turns those three knobs and writes down what happens.

## What to do

```bash
python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
python3 task2_convergence.py --nodes 20000 --betas 0.85,0.95
python3 task2_convergence.py --tol 1e-6 --betas 0.85
```

| # | Requirement |
|---|---|
| A1 | At least **five** values of beta, spanning 0.5 to 0.99 |
| A2 | Tabulate iterations against beta → `out/convergence.md` |
| A3 | Describe the shape. What happens as beta approaches 1, and **why** |
| A4 | At least two graph sizes, at least 5× apart. Does the **iteration count** change with size? Does the **time**? Those are different questions |
| A5 | Two tolerances at least 1e-4 apart. How many extra iterations does each extra digit cost? |
| A6 | Does the **top-10 ranking** change as beta changes? At which beta does it first change? |
| A7 | Your machine: CPU, RAM, what else was running |

A4 is the one worth thinking about before you run it. Predict the answer for
both halves first, then check. One of them will surprise you.

A6 is the practically important one. If the ranking is stable across beta, then
beta is a tuning detail. If it is not, then somebody chose 0.85 and that choice
is in every result.

## Pass condition

`out/convergence.json` has five or more betas with your machine recorded, and
`out/convergence.md` answers A3–A6.

```bash
python3 test_tasks.py --task 2
```

## What to write in `observation.md`

- What happens to the iteration count as beta → 1, and the reason
- A4: which of iteration count and wall time grew with graph size, and why they differ
- A6: whether the top 10 moved, and what that means for trusting a published ranking
