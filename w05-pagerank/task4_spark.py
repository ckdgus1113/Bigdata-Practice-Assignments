#!/usr/bin/env python3
"""Week 5 · Task 4 (optional) — PageRank until one machine is not enough.

Textbook §5.2, and §2.3 for why iterative jobs look the way they do in MapReduce.

Task 3 made PageRank sparse, and sparse is enough for a very long time. This task
finds where "a very long time" ends on your machine, and checks whether the thing
that was slower at small scale is still running when yours has stopped.

    python3 task4_spark.py --nodes 50000            # your task 3 version
    python3 task4_spark.py --nodes 50000 --spark    # and Spark, side by side
    python3 task4_spark.py --nodes 2000000 --spark  # keep going

Optional. Not part of the assignment.
"""
import argparse, random, time, tracemalloc


def build(nodes, avg_out=8, seed=246):
    """A graph as an edge list. Deliberately not a dict - Spark cannot take one."""
    rng = random.Random(seed)
    edges = []
    hot = list(range(min(nodes, 200)))
    for v in range(nodes):
        for _ in range(max(1, int(rng.gauss(avg_out, 3)))):
            edges.append((v, rng.choice(hot) if rng.random() < 0.3
                          else rng.randrange(nodes)))
    return edges


def local_pagerank(edges, nodes, beta=0.85, iterations=10):
    """Your task 3 implementation, adapted to an edge list.

    TASK 4a - reuse what you wrote in task3_sparse.py. Hold the graph however
    you like; the point of this task is to find out what that costs.

    Return {node: rank} and set local_pagerank.peak_bytes.
    """
    raise NotImplementedError("TASK 4a - reuse your sparse PageRank")


def spark_pagerank(edges, nodes, beta=0.85, iterations=10):
    """The same computation in Spark. Given, so the comparison is fair.

    Note what it never does: it never holds the whole graph in one process.
    Every step is a join between two RDDs, which is the shape §2.3 describes
    and the reason this survives graphs that a dict cannot.

    It is also not quite the algorithm you wrote in task 1. The difference is
    small, visible in the output, and task4.md asks you to find it - do not
    "fix" this function, explain it.
    """
    from pyspark.sql import SparkSession
    spark = (SparkSession.builder.master("local[*]").appName("w05")
             .config("spark.ui.enabled", "false").getOrCreate())
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    links = sc.parallelize(edges).groupByKey().mapValues(list).cache()
    ranks = links.mapValues(lambda _: 1.0 / nodes)

    for _ in range(iterations):
        contribs = links.join(ranks).flatMap(
            lambda kv: [(dst, kv[1][1] / len(kv[1][0])) for dst in kv[1][0]])
        ranks = contribs.reduceByKey(lambda a, b: a + b).mapValues(
            lambda r: beta * r + (1 - beta) / nodes)

    top = ranks.takeOrdered(10, key=lambda kv: -kv[1])
    total = ranks.map(lambda kv: kv[1]).sum()
    spark.stop()
    return dict(top), total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nodes", type=int, default=50_000)
    p.add_argument("--spark", action="store_true")
    p.add_argument("--iterations", type=int, default=10)
    a = p.parse_args()

    t0 = time.perf_counter()
    edges = build(a.nodes)
    print(f"\n  {a.nodes:,} nodes, {len(edges):,} edges, built in "
          f"{time.perf_counter() - t0:.1f}s\n")

    try:
        tracemalloc.start()
        t0 = time.perf_counter()
        ranks = local_pagerank(edges, a.nodes, iterations=a.iterations)
        t_local = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        top_local = sorted(ranks.items(), key=lambda kv: -kv[1])[:3]
        print(f"  single process   {t_local:8.2f}s   peak {peak / 1e6:8.1f} MB   "
              f"top={top_local[0][0]}")
    except NotImplementedError:
        print("  single process   TASK 4a not implemented")
        t_local = None
    except MemoryError:
        tracemalloc.stop()
        print("  single process   MemoryError - that is the finding. Record it.")
        t_local = None

    if a.spark:
        try:
            t0 = time.perf_counter()
            top, total = spark_pagerank(edges, a.nodes, iterations=a.iterations)
            t_spark = time.perf_counter() - t0
            first = sorted(top.items(), key=lambda kv: -kv[1])[0]
            print(f"  spark            {t_spark:8.2f}s   {'':16} "
                  f"top={first[0]}   sum={total:.4f}")
            if t_local:
                print(f"\n  spark is {t_spark / t_local:.1f}x the single process here")
        except Exception as e:
            print(f"  spark            did not run: {type(e).__name__}")
            print("  Record it in observation.md - this task is optional for exactly this reason.")
    print()


if __name__ == "__main__":
    main()
