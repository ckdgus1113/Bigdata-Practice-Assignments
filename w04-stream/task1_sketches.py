#!/usr/bin/env python3
"""Week 4 · Task 1 — Answer questions about a stream you cannot store.

Textbook §4.3 (sampling), §4.4 (Bloom filter), §4.5 (Flajolet-Martin).

The premise of the whole chapter: the stream is longer than your memory, it
goes past once, and you still have to answer. Every method here trades an exact
answer for a bounded amount of space, and the job is to know exactly what you
traded.

You build three, and the harness checks each against the truth it is
approximating.

    python3 task1_sketches.py --verify
"""
import argparse, hashlib, math, random


class BloomFilter:
    """Membership, with one-sided error.

    A Bloom filter never says "no" about something you inserted. It sometimes
    says "yes" about something you did not. That asymmetry is the entire design
    and it is why it is useful for "have I seen this before" and useless for
    "is this definitely in the set".

    `m` bits, `k` hash functions.
    """

    def __init__(self, m, k, seed=246):
        self.m = m
        self.k = k
        self.seed = seed
        self.bits = bytearray((m + 7) // 8)
        self._key = str(seed).encode()

    def _indexes(self, item):
        # One digest, split into two 64-bit halves, then g_i = h1 + i*h2 (mod m).
        # This gives k probe positions from a single hash call.
        d = hashlib.blake2b(str(item).encode(), digest_size=16,
                            key=self._key).digest()
        h1 = int.from_bytes(d[:8], "big")
        h2 = int.from_bytes(d[8:], "big") | 1   # odd, so the probes spread out
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item):
        # Only ever sets bits. A bit is never cleared, which is why an inserted
        # item can never be reported absent.
        for i in self._indexes(item):
            self.bits[i >> 3] |= 1 << (i & 7)

    def __contains__(self, item):
        return all(self.bits[i >> 3] >> (i & 7) & 1 for i in self._indexes(item))

    def expected_fp_rate(self, n_inserted):
        """The textbook's predicted false-positive rate after n insertions.

        §4.4.2 derives it. Return the number, do not measure it - the harness
        measures separately and compares the two.
        """
        # P(a given bit is still 0) = (1 - 1/m)^(kn) ~ e^(-kn/m)
        # A false positive needs all k probed bits to be 1.
        return (1 - math.exp(-self.k * n_inserted / self.m)) ** self.k

    def memory_bits(self):
        return len(self.bits) * 8


def flajolet_martin(stream, n_hashes=64, seed=246):
    """Estimate how many DISTINCT items went past, in almost no memory.

    §4.5. Hash each item, count trailing zeros in the hash, keep the maximum.
    A maximum of R suggests about 2^R distinct items, because seeing R trailing
    zeros is a 1-in-2^R event.

    One hash gives an estimate with enormous variance, so you use many and
    combine them. How you combine them matters a great deal:

      * averaging 2^R directly is dominated by whichever hash got lucky - the
        values are exponential, so one outlier swamps the rest
      * the median is robust but can only ever be a power of two
      * §4.5.3 suggests grouping, and combining twice

    The harness accepts anything **within a factor of two** of the truth. That is
    not a generous tolerance, it is an honest one: this method really is that
    crude, and HyperLogLog exists because of it. Getting inside a factor of two
    reliably is the requirement; getting closer than that is not expected here.

    Return your estimate as a float.
    """
    registers = fm_registers(stream, n_hashes, seed)
    return fm_combine(registers, "mean-R")


PHI = 0.77351   # Flajolet-Martin correction: E[2^R] ~ n / PHI
# The max trailing-zero count of N items has E[R] ~ log2(N) + gamma/ln2 - 1/2,
# i.e. 2^E[R] ~ 1.26 N. That is the constant for "average the exponent".
C_EXP = 2 ** (0.5772156649 / math.log(2) - 0.5)


def fm_registers(stream, n_hashes=64, seed=246):
    """One pass. Returns `n_hashes` small integers, the maximum trailing-zero
    count seen by each register.

    Instead of hashing every item `n_hashes` times, hash it once and let the low
    bits pick which register it belongs to; the remaining bits give the trailing
    zeros. That is stochastic averaging (Flajolet-Martin's PCSA): the cost per
    item is one hash, and each register sees about n / n_hashes of the items.
    Memory is `n_hashes` integers no matter how long the stream is.
    """
    key = str(seed).encode()
    shift = (n_hashes - 1).bit_length()          # bits used to pick a register
    regs = [0] * n_hashes
    for item in stream:
        h = int.from_bytes(hashlib.blake2b(str(item).encode(), digest_size=8,
                                           key=key).digest(), "big")
        j = h % n_hashes
        rest = h >> shift
        # trailing zeros of `rest`; an all-zero remainder counts as the max
        r = (rest & -rest).bit_length() if rest else 64 - shift
        if r > regs[j]:
            regs[j] = r
    return regs


def fm_combine(regs, rule="group-median"):
    """Turn the registers into one estimate. Several rules, to compare.

    Each register saw about n/m items, so a register with value R (here R is
    "trailing zeros + 1") suggests n/m ~ 2^R * PHI^-1 / 2.
    """
    m = len(regs)
    per = [2.0 ** (r - 1) / PHI for r in regs]    # per-register estimate of n/m
    if rule == "mean":                  # average 2^R directly: outlier-dominated
        return m * sum(per) / m
    if rule == "median":                # robust, but always lands on 2^R / PHI
        s = sorted(per)
        mid = m // 2
        return m * (s[mid] if m % 2 else (s[mid - 1] + s[mid]) / 2)
    if rule == "group-median":          # §4.5.3: average within groups, median of groups
        g = max(1, int(math.sqrt(m)))
        groups = [per[i:i + g] for i in range(0, m - g + 1, g)]
        avgs = sorted(sum(x) / len(x) for x in groups)
        mid = len(avgs) // 2
        med = avgs[mid] if len(avgs) % 2 else (avgs[mid - 1] + avgs[mid]) / 2
        return m * med
    if rule == "mean-R":                # average the exponent, not 2^R (PCSA)
        return m * 2.0 ** (sum(r - 1 for r in regs) / m) / C_EXP
    raise ValueError(rule)


def reservoir_sample(stream, k, seed=246):
    """Keep k items uniformly at random from a stream of unknown length.

    §4.3. Every item that went past must end up with the same probability k/n
    of being in your sample, and you only ever hold k of them.

    Return a list of k items (or fewer if the stream was shorter).
    """
    rng = random.Random(seed)
    sample = []
    for n, item in enumerate(stream, start=1):
        if n <= k:
            sample.append(item)           # the first k always go in
        else:
            # The n-th item enters with probability k/n and evicts a uniformly
            # chosen resident. n is just the running count; the total length is
            # never needed.
            j = rng.randrange(n)
            if j < k:
                sample[j] = item
    return sample


# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub"); return 1
    inserted = [f"item-{i}" for i in range(800)]
    for x in inserted:
        bf.add(x)
    check("no false negatives", all(x in bf for x in inserted))

    absent = [f"other-{i}" for i in range(20_000)]
    fp = sum(1 for x in absent if x in bf) / len(absent)
    predicted = bf.expected_fp_rate(len(inserted))
    close = abs(fp - predicted) < max(0.02, predicted * 0.5)
    check("measured false-positive rate matches theory", close,
          f"measured {fp:.3%}, predicted {predicted:.3%}")

    # --- Flajolet-Martin: a factor of two is what this method gives you
    try:
        distinct = 20_000
        stream = [f"k{rng.randrange(distinct)}" for _ in range(120_000)]
        est = flajolet_martin(stream)
    except NotImplementedError:
        print("  flajolet_martin is still a stub"); return 1
    true_distinct = len(set(stream))
    ratio = est / true_distinct
    check("distinct estimate within a factor of 2", 0.5 <= ratio <= 2.0,
          f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)")

    # --- Reservoir: uniform over many trials
    try:
        counts = [0] * 20
        trials = 4000
        for t in range(trials):
            s = reservoir_sample(range(20), 5, seed=t)
            for i in s:
                counts[i] += 1
    except NotImplementedError:
        print("  reservoir_sample is still a stub"); return 1
    expected = trials * 5 / 20
    spread = (max(counts) - min(counts)) / expected
    check("reservoir is uniform across items", spread < 0.15,
          f"spread {spread:.1%} around {expected:.0f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
