# Week 5 Lab · Link Analysis

**Theory** — 5-1 PageRank, dead ends, spider traps (§5.1) · 5-2 efficient PageRank, topic-sensitive, link spam (§5.2 – §5.4)
**Submit to** — `w05-pagerank/out/`

A number that says how important a page is, computed from nothing but who points
at whom. This week: build it, watch the two structures that break it, measure
what convergence actually costs, and then make it run on a graph whose matrix
would not fit.

```bash
cd w05-pagerank
```

| | Task | You build |
|---|---|---|
| 1 | PageRank, and the two ways it breaks | the working version and the broken one |
| 2 | What convergence costs | an iteration curve across beta, size and tolerance |
| 3 | A graph that will not fit as a matrix | the sparse version, to 1e-9 of the dense answer |
| 4 | **optional** · until one machine is not enough | PageRank on Spark, and why it loses at small scale |

Details and requirements are in **`task1.md`**, **`task2.md`**, **`task3.md`**.
Task 4 is **optional and not graded** — see **`task4.md`**.

## Running everything

```bash
python3 task1_pagerank.py --verify
python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
python3 bench.py --yours
python3 test_tasks.py

python3 task4_spark.py --nodes 50000 --spark   # optional, needs Java 17 + PySpark
```

## What to submit

| File | From |
|---|---|
| `task1_pagerank.py` | your PageRank, working and broken |
| `out/convergence.json` · `out/convergence.md` | the iteration curve |
| `task3_sparse.py` · `out/bench.txt` | your sparse version and its numbers |
| `out/observation.md` | 2–3 lines per task |

```bash
python3 ../check.py w05
```

## No download needed

The graph is generated with a fixed seed — power-law out-degrees, a few dead
ends, one small trap. Task 4 generates its own, larger.
