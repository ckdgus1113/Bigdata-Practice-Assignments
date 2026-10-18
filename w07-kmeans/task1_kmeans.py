#!/usr/bin/env python3
"""Week 7 · Task 1 — k-means, and the thing that decides the answer.

Textbook §7.1 (clustering, the curse of dimensionality), §7.3 (k-means).

k-means is four lines: pick centroids, assign every point to the nearest one,
move each centroid to the mean of its points, repeat. It always converges.

It converges to a **local** optimum, and which one depends entirely on where you
started. That is not a footnote - it is the difference between a clustering that
means something and one that does not, and you can watch it happen on nine points.

    python3 task1_kmeans.py --verify
"""
import argparse, math, random

# Three obvious blobs of three points each. Any sensible clustering finds them.
BLOBS = [(0.0, 0.0), (0.2, 0.1), (0.1, 0.2),
         (8.0, 8.0), (8.2, 8.1), (8.1, 8.2),
         (0.0, 8.0), (0.2, 8.1), (0.1, 8.2)]


def euclidean(a, b):
    """Distance between two points of any dimension."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def assign(points, centroids):
    """Nearest centroid for each point. Return a list of centroid indices.

    Ties go to the lower index, so that everybody's answer is the same.
    """
    labels = []
    for p in points:
        best, bi = None, 0
        for j, c in enumerate(centroids):
            d = _sq(p, c)
            if best is None or d < best:      # strict <, so the lower index wins a tie
                best, bi = d, j
        labels.append(bi)
    return labels


def update(points, labels, k):
    """Move each centroid to the mean of its points.

    An empty cluster has no mean. Decide what you do - and say so, because the
    choice changes the result and there is more than one defensible answer.

    My choice (R3): an empty cluster **keeps its old centroid**. It is the
    cheapest rule and it never makes SSE worse. The alternative, moving the
    centroid onto the point furthest from its own centroid, would cut SSE more
    but costs an extra pass and can change which local optimum is reached.
    """
    sums = [None] * k
    counts = [0] * k
    for p, l in zip(points, labels):
        if sums[l] is None:
            sums[l] = list(p)
        else:
            s = sums[l]
            for i, v in enumerate(p):
                s[i] += v
        counts[l] += 1
    return [tuple(v / counts[j] for v in sums[j]) if counts[j] else None
            for j in range(k)]


def kmeans(points, k, init="random", seed=246, max_iter=100):
    """Run to convergence. Return (labels, centroids, sse).

    `sse` is the sum over points of the squared distance to their own centroid.
    It is what k-means minimises, and it is how you compare two runs.

    `init` is either:
        "random"   pick k points at random as the starting centroids
        "++"       k-means++ (§7.3.2): pick the first at random, then pick each
                   next one with probability proportional to the squared distance
                   to the nearest centroid already chosen

    Set `kmeans.iterations` to how many passes you used.
    """
    rng = random.Random(seed)
    if init == "++":
        centroids = _plusplus(points, k, rng)
    elif init == "random":
        centroids = [tuple(p) for p in rng.sample(points, k)]
    else:
        raise ValueError(f"unknown init {init!r}")

    labels = None
    for kmeans.iterations in range(1, max_iter + 1):
        new_labels = assign(points, centroids)
        if new_labels == labels:                # nothing moved: converged
            break
        labels = new_labels
        means = update(points, labels, k)
        centroids = [m if m is not None else old       # R3: empty keeps old centroid
                     for m, old in zip(means, centroids)]
    return labels, centroids, sse_of(points, labels, centroids)


def _sq(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _plusplus(points, k, rng):
    """k-means++: next centroid chosen with probability proportional to D(x)^2."""
    centroids = [tuple(rng.choice(points))]
    d2 = [_sq(p, centroids[0]) for p in points]
    while len(centroids) < k:
        total = sum(d2)
        if total == 0:                          # every point already sits on a centroid
            idx = rng.randrange(len(points))
        else:
            r, acc, idx = rng.random() * total, 0.0, len(points) - 1
            for i, w in enumerate(d2):
                acc += w
                if acc >= r:
                    idx = i
                    break
        c = tuple(points[idx])
        centroids.append(c)
        d2 = [min(w, _sq(p, c)) for w, p in zip(d2, points)]
    return centroids


def sse_of(points, labels, centroids):
    """Sum of squared distances from each point to its assigned centroid."""
    return sum(_sq(p, centroids[l]) for p, l in zip(points, labels))


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<50} {detail}")
        fails += not ok

    try:
        check("distance in 2d", abs(euclidean((0, 0), (3, 4)) - 5) < 1e-9)
        check("distance in 5d",
              abs(euclidean((0,) * 5, (1,) * 5) - math.sqrt(5)) < 1e-9)
    except NotImplementedError:
        print("  euclidean is still a stub"); return 1

    try:
        labels, cents, sse = kmeans(BLOBS, 3, init="++", seed=1)
    except NotImplementedError:
        print("  kmeans is still a stub"); return 1

    groups = {}
    for p, l in zip(BLOBS, labels):
        groups.setdefault(l, []).append(p)
    check("three clusters of three", sorted(len(g) for g in groups.values()) == [3, 3, 3],
          sorted(len(g) for g in groups.values()))
    check("the three blobs were recovered",
          all(max(q[0] for q in g) - min(q[0] for q in g) < 1 and
              max(q[1] for q in g) - min(q[1] for q in g) < 1
              for g in groups.values()))
    check("sse is small when clusters are right", sse < 1.0, f"sse {sse:.4f}")

    # Bad luck with random starts should sometimes be visibly worse.
    randoms = [kmeans(BLOBS, 3, init="random", seed=s)[2] for s in range(40)]
    plusplus = [kmeans(BLOBS, 3, init="++", seed=s)[2] for s in range(40)]
    check("random init sometimes lands badly", max(randoms) > min(randoms) * 5,
          f"sse from {min(randoms):.3f} to {max(randoms):.3f}")
    check("k-means++ is more reliable than random",
          sum(plusplus) / len(plusplus) <= sum(randoms) / len(randoms),
          f"mean sse: ++ {sum(plusplus) / len(plusplus):.3f} vs "
          f"random {sum(randoms) / len(randoms):.3f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
