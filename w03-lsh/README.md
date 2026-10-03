# Week 3 Lab · Finding Similar Items

**Theory** — 3-1 Jaccard, shingling, minhashing (§3.1 – §3.3) · 3-2 LSH, distance measures (§3.4 – §3.5)
**Submit to** — `w03-lsh/out/`

Comparing every pair of things is quadratic, and quadratic stops being possible
long before "big data" starts. This week is the standard way out, and the price
it charges.

```bash
cd w03-lsh
```

| | Task | You build |
|---|---|---|
| 1 | Minhash and LSH from the matrix up | signatures and banding, checked against the textbook's own example |
| 2 | Find the crossover on your machine | a timing and memory curve, and the size where it hurts |
| 3 | Find the same pairs, comparing far less | a finder scored on comparisons and recall |

Details and requirements are in **`task1.md`**, **`task2.md`**, **`task3.md`**.

## Running everything

```bash
python3 task1_minhash.py --verify
python3 task2_crossover.py --sizes 250,500,1000,2000
python3 bench.py --yours
python3 test_tasks.py
```

## What to submit

| File | From |
|---|---|
| `task1_minhash.py` | your minhash and LSH |
| `out/crossover.json` · `out/curve.md` | the timing curve and where it broke |
| `task3_scale.py` · `out/bench.txt` | your finder and its numbers |
| `out/observation.md` | 2–3 lines per task |

```bash
python3 ../check.py w03
```

## No download needed

Tasks 1 and 3 run on synthetic data with a fixed seed, so everybody's numbers
are comparable. Task 2 is about **your** machine, so its numbers are not
supposed to match anybody else's — that is the point of it.
