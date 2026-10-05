#!/usr/bin/env python3
"""Week 4 · Task 3 — Same memory, fewer mistakes.

Textbook §4.4 (Bloom filters), §4.5 (counting distinct).

`NaiveFilter` is a membership filter in a fixed number of bits. It works. It
also makes far more mistakes than it has to with the memory it was given, and
it does so for a reason you can find by reading §4.4.2 and doing one derivative.

You get **exactly the same number of bits**. Make fewer mistakes.

    python3 bench.py
    python3 bench.py --yours

The rule that makes this interesting: a false negative is not allowed. Ever.
The whole point of this structure is that "no" means no. A filter that gets a
better score by occasionally forgetting something it was given has not improved
anything, it has broken the contract.
"""
import hashlib, math


class NaiveFilter:
    """One hash function, and the bits it was given."""

    def __init__(self, n_bits, seed=246):
        self.n_bits = n_bits
        self.seed = seed
        self.bits = bytearray(n_bits)

    def _index(self, item):
        d = hashlib.blake2b(str(item).encode(), digest_size=8,
                            key=str(self.seed).encode()).digest()
        return int.from_bytes(d, "big") % self.n_bits

    def add(self, item):
        self.bits[self._index(item)] = 1

    def __contains__(self, item):
        return bool(self.bits[self._index(item)])

    def memory_bits(self):
        return self.n_bits


class YourFilter:
    """Your filter.

        __init__(n_bits, seed=246)
        add(item)
        item in filter  ->  bool
        memory_bits()   ->  how many bits you are using

    `memory_bits()` must not exceed the `n_bits` you were given. The harness
    checks. Counting only some of your memory is not an optimisation.

    §4.4.2 gives the false-positive rate of a filter with m bits, k hashes and
    n items inserted. There is a k that minimises it, and it depends on m/n.
    The harness tells you n before you start, so you have no excuse for guessing.

    Then there is a second question, which is worth more: the harness inserts
    a **known** number of items, but a real stream does not tell you n in
    advance. What would you do then? You do not have to implement it - but
    observation.md asks.
    """

    # The harness inserts N_INSERT items into N_BITS bits. A filter built for a
    # stream of unknown length cannot know this, so it is stated here, once.
    EXPECTED_ITEMS = 8_000

    def __init__(self, n_bits, seed=246, expected_items=None):
        n = expected_items or self.EXPECTED_ITEMS
        self.n_bits = n_bits
        self.seed = seed
        # §4.4.2: FP = (1 - e^(-kn/m))^k is minimised at k = (m/n) ln 2.
        # Here m/n = 10, so k = 6.93; the integer neighbours are 6 and 7 and
        # the rate is nearly flat between them, so take whichever is lower.
        k_real = n_bits / n * math.log(2)
        self.k = min((max(1, math.floor(k_real)), max(1, math.ceil(k_real))),
                     key=lambda k: (1 - math.exp(-k * n / n_bits)) ** k)
        self.bits = bytearray((n_bits + 7) // 8)    # packed: 8 bits per byte
        self._key = str(seed).encode()

    def _indexes(self, item):
        # One digest gives all k positions: g_i = h1 + i * h2 (mod m).
        d = hashlib.blake2b(str(item).encode(), digest_size=16,
                            key=self._key).digest()
        h1 = int.from_bytes(d[:8], "big")
        h2 = int.from_bytes(d[8:], "big") | 1
        return [(h1 + i * h2) % self.n_bits for i in range(self.k)]

    def add(self, item):
        for i in self._indexes(item):
            self.bits[i >> 3] |= 1 << (i & 7)

    def __contains__(self, item):
        return all(self.bits[i >> 3] >> (i & 7) & 1 for i in self._indexes(item))

    def memory_bits(self):
        # Everything held: the packed bit array. k, seed and the key are a few
        # bytes of constants and do not scale with the data.
        return len(self.bits) * 8
