# Task 4 · PageRank Until One Machine Is Not Enough — **optional**

**File** — `task4_spark.py`
**Theory** — §5.2, and §2.3 for the MapReduce shape of an iterative job
**Status** — **optional.** Not part of the assignment, not graded. Effort is noted.

---

## What this is for

Task 3 made PageRank sparse, and sparse is enough for a very long time. This task
finds where "a very long time" ends **on your machine**, and asks whether the tool
that was slower at small scale is still running when yours has stopped.

```bash
python3 task4_spark.py --nodes 50000
python3 task4_spark.py --nodes 50000  --spark
python3 task4_spark.py --nodes 500000 --spark
python3 task4_spark.py --nodes 2000000 --spark      # if you dare
```

## Requirements

| # | Requirement |
|---|---|
| A1 | `local_pagerank` reuses your task 3 implementation, adapted to an edge list |
| A2 | Both give the same top-ranked node at a size where both finish |
| A3 | Raise `--nodes` until the single-process version **stops being usable**. Record that size and what gave out — time or memory |
| A4 | At the same size, does Spark finish? Report both |
| A5 | At **small** sizes Spark is much slower. Report the ratio and explain it |
| A6 | Plot or tabulate peak memory against node count for the single-process version. Spark's does not grow the same way — say why |
| A7 | **The Spark version's ranks do not sum to 1.** Find out why, using what you built in task 1. Do not fix the function — explain it |

**A5 is not a trap, it is the point.** Expect Spark to lose badly at 50,000 nodes.
The week 2 optional task measured 369× on a word count; here it will be less
extreme but still a loss. If your report only contains the size where Spark wins,
you have measured half of it.

**A3 is the other half.** A `dict` holding hundreds of millions of entries does
not exist. The thing that was slower is still running when the `dict` is gone,
and that sentence is the entire argument for distributed processing.

**A7 is the one to do carefully.** The `spark_pagerank` function is given to you
and it is *not* the algorithm from task 1 — one thing you handled there is
missing here, and the output tells you so:

```
  single process       1.70s   peak     25.2 MB   top=147
  spark                5.65s                      top=147   sum=0.9959
```

Same top-ranked node, and a total that is not 1. Task 1 made you handle exactly
this case. Say which case it is, where the missing rank went, and what you would
add to the Spark version — in one sentence each. This is the most useful question
in the task, because production code gets this wrong regularly.

## A warning

Raising `--nodes` past a million will generate a large edge list before anything
starts. Watch your memory and stop it rather than freezing your laptop. **Stopping
early and recording where is the correct outcome.**

## If Spark will not start

The script catches it. Do A1 – A3 and A6 without Spark — those are about your
machine and they are the more interesting half anyway. Record what stopped you.

## What to write in `observation.md`

- The node count where single-process stopped being usable, and what gave out
- A5: the ratio at 50,000 nodes, and where that time goes
- A7: why the Spark ranks do not sum to 1, and what is missing
- A6: the two memory curves, and why Spark's is shaped differently
- One sentence: when would you actually reach for Spark in real work?
