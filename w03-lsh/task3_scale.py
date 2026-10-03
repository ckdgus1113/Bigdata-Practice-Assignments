#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """Your near-duplicate finder.

        __init__(threshold)
        find(docs, similarity) -> {(i, j), ...}

    `similarity(a, b)` is the only way to compare two documents, and every call
    is counted. Everything else - signatures, banding, bucketing - is free, in
    the sense that the harness does not charge you for it. That is deliberate:
    it is also roughly true at scale, where the comparison is the expensive
    part and the hashing is linear.

    Two knobs decide everything:

        the number of hashes in a signature
        how many bands you split it into

    §3.4.2 gives you the relationship between those and the probability that a
    pair at similarity s becomes a candidate. It is an S-curve, and where its
    step sits is something you choose. Choose it on purpose and be able to say
    why in observation.md - a threshold of 0.8 does not mean bands should be
    anything in particular until you have done the arithmetic.

    You may reuse your Task 1 code.
    """

    # n hashes in b bands of r = n / b rows. A pair at similarity s becomes a
    # candidate with probability 1 - (1 - s^r)^b, whose step sits near
    # (1/b)^(1/r) = (1/30)^(1/4) = 0.43. That is deliberately BELOW the 0.6
    # threshold: a missed true pair is lost for good, while an extra candidate
    # costs one comparison. At s = 0.62 (the weakest planted pair) the pair is
    # caught with probability 1 - (1 - 0.62^4)^30 = 0.991, and at s = 0.01
    # (two unrelated documents) the chance is about 30 * 0.01^4 = 3e-7.
    HASHES, BANDS = 120, 30
    PRIME = (1 << 61) - 1

    def __init__(self, threshold, seed=246):
        import random
        self.threshold = threshold
        rng = random.Random(seed)
        self.coeffs = [(rng.randrange(1, self.PRIME), rng.randrange(self.PRIME))
                       for _ in range(self.HASHES)]

    def signature(self, doc):
        p = self.PRIME
        return [min((a * x + c) % p for x in doc) for a, c in self.coeffs]

    def find(self, docs, similarity):
        from task1_minhash import lsh_candidates
        sigs = [self.signature(d) for d in docs]
        out = set()
        for i, j in lsh_candidates(sigs, self.BANDS):
            if similarity(docs[i], docs[j]) >= self.threshold:
                out.add((i, j))
        return out
