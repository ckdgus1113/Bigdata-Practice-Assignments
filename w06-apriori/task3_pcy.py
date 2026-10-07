#!/usr/bin/env python3
"""Week 6 · Task 3 — Make pass two fit.

Textbook §6.3 (PCY), §6.3.2 - §6.3.4.

`PlainApriori` does what Task 1 asked: use pass one to drop infrequent items,
then count every pair of surviving items. That is already much better than
counting all pairs. It is still not enough, because the surviving items are the
common ones, and the common ones appear together constantly.

The harness measures **the peak number of pair counters you held**, because
that is the thing that decides whether the algorithm runs at all. §6.3 is about
spending pass one's spare memory to shrink it.

    python3 bench.py
    python3 bench.py --yours

Correctness first: you must find exactly the same frequent pairs. Finding fewer
is not an optimisation.
"""
from collections import Counter
from itertools import combinations


class PlainApriori:
    """Pass one drops infrequent items. Pass two counts every surviving pair."""

    def __init__(self, support):
        self.support = support
        self.peak_counters = 0

    def run(self, baskets):
        counts = Counter()
        for basket in baskets:
            counts.update(basket)
        frequent = {i for i, c in counts.items() if c >= self.support}

        pair_counts = Counter()
        for basket in baskets:
            items = sorted(basket & frequent)
            for pair in combinations(items, 2):
                pair_counts[pair] += 1
            self.peak_counters = max(self.peak_counters, len(pair_counts))

        return {frozenset(p): c for p, c in pair_counts.items()
                if c >= self.support}


class YourAlgorithm:
    """Your frequent-pair finder.

        __init__(support)
        run(baskets) -> {frozenset({a, b}): count}
        .peak_counters -> the most pair counters you ever held at once

    Same pairs as the baseline. Fewer counters.

    Pass one only needs one integer per item, and there are not many items. The
    rest of your memory is sitting idle while you do it. §6.3 spends it: hash
    every pair you see in pass one into a fixed array of buckets, and count the
    buckets rather than the pairs.

    A bucket whose total is below the support threshold cannot contain a
    frequent pair. In pass two you skip every pair landing in such a bucket -
    and the bucket array collapses to a bitmap, one bit each, before you need
    the memory for counters.

    Two things to be careful of:

      * a bucket being frequent does not make its pairs frequent. It is a
        filter, not an answer
      * `peak_counters` is on your honour. Count the pair counters you hold at
        the same time. The bitmap is not a pair counter, but if you keep the
        full bucket counts alive into pass two, that is not free either -
        observation.md asks about it
    """

    # Fixed array of buckets. ~3.8M pair occurrences land in 1M buckets, about
    # 4 per bucket on average against a threshold of 50, so most buckets stay
    # infrequent. Fewer buckets means more collisions and a weaker filter.
    BUCKETS = 1_000_003

    def __init__(self, support, buckets=None):
        self.support = support
        self.buckets = buckets or self.BUCKETS
        self.peak_counters = 0

    def _bucket(self, a, b):
        # a < b always, so the pair is hashed in a canonical order
        return hash((a, b)) % self.buckets

    def run(self, baskets):
        support = self.support

        # pass one: count items, and hash every pair of every basket into a
        # bucket. Bucket counts are not pair counters - there are fixed many.
        item_counts = Counter()
        bucket_counts = [0] * self.buckets
        for basket in baskets:
            item_counts.update(basket)
            for a, b in combinations(sorted(basket), 2):
                bucket_counts[self._bucket(a, b)] += 1

        frequent = {i for i, c in item_counts.items() if c >= support}
        # between passes the bucket array collapses to one bit per bucket
        bitmap = [c >= support for c in bucket_counts]
        del bucket_counts

        # pass two: count only pairs of frequent items that land in a frequent
        # bucket. The bitmap is a filter - a frequent bucket proves nothing.
        pair_counts = Counter()
        for basket in baskets:
            items = sorted(basket & frequent)
            for a, b in combinations(items, 2):
                if bitmap[self._bucket(a, b)]:
                    pair_counts[(a, b)] += 1
            self.peak_counters = max(self.peak_counters, len(pair_counts))

        return {frozenset(p): c for p, c in pair_counts.items()
                if c >= support}
