# Task 1 · PageRank, and the Two Ways It Breaks

**File** — `task1_pagerank.py`
**Theory** — §5.1 PageRank, §5.1.3 dead ends, §5.1.4 spider traps
**Kind** — implementation · runs anywhere

---

## What you are building

A random surfer follows links forever; a page's rank is how often the surfer is
there. As linear algebra that is `r = M r`, and **as written it does not work on
the real web.**

Two structures break it, and one line fixes both. You build the broken version
too, so that you watch each failure rather than take it on trust.

| Structure | What goes wrong |
|---|---|
| **dead end** — a page with no out-links | rank drains out of the graph until everything is 0 |
| **spider trap** — pages that only link to each other | they absorb all the rank |

## Requirements

| # | Requirement |
|---|---|
| R1 | `pagerank(graph, beta, iterations, tol)` returns ranks summing to 1 |
| R2 | Dead ends handled: total rank is conserved |
| R3 | Spider traps handled: nodes outside the trap keep some rank |
| R4 | Stops early when the L1 change drops below `tol` |
| R5 | Sets `pagerank.iterations` to the number actually used — Task 2 reads it |
| R6 | `pagerank_no_teleport` implements the broken version, and really does fail |

R6 is not busywork. The harness checks that your broken version **drains to
near-zero** on the dead-end graph and that the trap **takes over 95%** on the
other. If your "broken" version quietly works, you have hidden the fix somewhere
and you will not understand what it was for.

## Pass condition

```bash
python3 task1_pagerank.py --verify
```

Seven checks, including both failures and both repairs.

```
  ok    without the fix, a dead end drains the graph     total rank 0.0000
  ok    with the fix, rank is conserved                  1.000000
  ok    without the fix, a spider trap takes everything  C+D = 1.0000
```

## What to write in `observation.md`

- Where does a dead end's rank go in the broken version, and where do you send it
  instead? Name the choice you made — there is more than one defensible answer
- The same fix repairs both problems. Say in one sentence why the same thing
  works for two failures that look different
- What does `beta` mean physically? What is the surfer doing with probability
  `1 - beta`?
