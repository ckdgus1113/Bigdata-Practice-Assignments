#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        """Elkan's algorithm: triangle-inequality pruning, no approximation.

        Stored per point (k + 2 numbers, n * (k + 1) floats plus n labels):
            u[i]     upper bound on d(x_i, its centroid)
            l[i][j]  lower bound on d(x_i, centroid j)
        Stored per iteration (k * k): the centroid-to-centroid distances.

        Two tests skip work, both from d(x,c') >= d(c,c') - d(x,c):
            1. u[i] <= s[c]   (s[c] = half the distance from c to its nearest
               other centroid): nothing can be closer, skip the point entirely.
            2. u[i] <= l[i][j] or u[i] <= d(c,c_j) / 2: centroid j cannot beat
               the current one, skip that single distance.
        Bounds are loosened by how far each centroid moved (k distance calls per
        iteration, not n * k), and tightened only when a test fails.
        """
        k, n = self.k, len(points)
        centroids = list(initial_centroids)
        labels = [0] * n
        u = [0.0] * n
        lower = [None] * n
        self.calls_by_iteration = []

        for self.iterations in range(1, self.max_iter + 1):
            before = getattr(distance, "calls", 0)
            changed = False

            if self.iterations == 1:
                # Nothing is known yet: measure everything once, keep it as bounds.
                for i, p in enumerate(points):
                    row = [distance(p, c) for c in centroids]
                    best, bi = row[0], 0
                    for j in range(1, k):
                        if row[j] < best - 1e-12:
                            best, bi = row[j], j
                    lower[i], u[i], labels[i] = row, best, bi
                changed = True
            else:
                cc = [[0.0] * k for _ in range(k)]
                for a in range(k):
                    for b in range(a + 1, k):
                        cc[a][b] = cc[b][a] = distance(centroids[a], centroids[b])
                half = [[v / 2 for v in row] for row in cc]
                s = [min(cc[a][b] for b in range(k) if b != a) / 2 for a in range(k)]

                for i, p in enumerate(points):
                    ci = labels[i]
                    ui = u[i]
                    if ui <= s[ci]:
                        continue                       # test 1: cannot have changed
                    li, hc = lower[i], half[ci]
                    tight = False
                    for j in range(k):
                        if j == ci or ui <= li[j] or ui <= hc[j]:
                            continue                   # test 2: j cannot be closer
                        if not tight:                  # make u exact, once
                            ui = li[ci] = distance(p, centroids[ci])
                            tight = True
                            if ui <= li[j] or ui <= hc[j]:
                                continue
                        dj = li[j] = distance(p, centroids[j])
                        if dj < ui - 1e-12:
                            ci, ui, hc = j, dj, half[j]
                            changed = True
                    labels[i], u[i] = ci, ui

            self.calls_by_iteration.append(getattr(distance, "calls", 0) - before)
            new = _means(points, labels, k, centroids)
            if not changed:
                centroids = new
                break

            move = [distance(o, c) for o, c in zip(centroids, new)]
            for i in range(n):
                u[i] += move[labels[i]]
                li = lower[i]
                for j in range(k):
                    v = li[j] - move[j]
                    li[j] = v if v > 0.0 else 0.0
            centroids = new
        return labels, centroids
