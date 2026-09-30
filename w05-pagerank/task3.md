# Task 3 · PageRank on a Graph That Will Not Fit as a Matrix

**Files** — `task3_sparse.py` · harness `bench.py` (**do not edit the harness**)
**Theory** — §5.2 efficient PageRank
**Kind** — improvement · runs anywhere

---

## What you are given

`DenseMatrix` is PageRank written the way the equations are written: build M,
multiply. Correct, readable, and it stores n² numbers for a graph that has
almost no edges.

```bash
python3 bench.py
python3 bench.py --yours
```

```
  1,200 nodes  ·  5,877 edges  ·  density 0.4081%
```

**Where the baseline lands:**

```
  baseline      0.32s   floats held    1,440,000   sum 1.000000
```

1.44 million numbers for 5,877 edges. The web's matrix is about 99.9999% zeros,
and storing them is the entire problem §5.2 is about.

## Requirements

| # | Requirement |
|---|---|
| R1 | `YourPageRank(beta, tol, max_iter)` with `run(graph)` and `memory_floats()` |
| R2 | `bench.py` unmodified |
| R3 | **Every rank within 1e-9 of the dense answer.** The harness checks all of them |
| R4 | Fewer floats held, and faster |
| R5 | In `observation.md`: the teleport term touches every node. Explain why it does **not** need a dense operation |

R3 is not a formality. A fast PageRank that ranks pages differently is a
different algorithm, not a faster one.

## Grading

| | Requirement |
|---|---|
| pass | R1–R4, more than 2× less memory |
| good | ≥ **20×** less memory and ≥ 2× faster |
| **strong** | ≥ **100×** less memory and ≥ 5× faster |

"Strong" is comfortably reachable — a straightforward adjacency-list version gets
about 600× the memory and 40× the speed. If you are nowhere near, you are
probably still materialising something you do not need.

Notice what `graph` already is: an adjacency list, which **is** the sparse
representation. The dense version throws that structure away and then pays to
rebuild it.

## R5 · the part that looks like it needs a dense operation

Every node receives `(1 - beta)/n` from teleporting, every iteration. That is an
operation over all n nodes, so it looks dense. It is not — and neither is the
dead-end redistribution, which has the same shape. §5.2.3 explains both.
Say in your own words why.

## What to write in `observation.md`

- What you store instead of M, and how many floats that is in terms of n and the edge count
- R5, in your own words
- Your worst per-node difference from the dense answer. If it is not zero, say
  where the difference comes from — it is not a bug
