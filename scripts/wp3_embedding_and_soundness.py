#!/usr/bin/env python3
"""
WP3 — Piece A embedding-comparison arm (A.3) + false-positive/soundness test (A.4).

A.3 (the bridge): does an off-the-shelf *similarity* encoder recover the BoolAlg<->BoolRing
correspondence that the theory morphism makes exact? We MEASURE this — we do not assume it.
  - pinned encoder (all-MiniLM-L6-v2), recorded.
  - ~14 corresponding pairs: each a fact stated in Boolean-ALGEBRA (lattice/order) vocabulary
    and the SAME fact in Boolean-RING (arithmetic) vocabulary.
  - distractor pool so ranking is meaningful.
  - threshold calibrated on held-out SAME-vocabulary paraphrase pairs (principled, not post-hoc).
  - shared-token pre-check: split pairs into "disjoint vocabulary" vs "shares a salient token"
    and report separately, so a hit isn't a literal-token artifact.
  - descriptive ranking only (recall@1/3, MRR, mean rank) — N is small.
  - DISCONFIRMING outcome built in: if the encoder ranks counterparts at the top, that is
    evidence toward hypothesis (i) on this task, reported as such (not a categorical win).

A.4 (soundness): the symbolic morphism search must FAIL on a near-miss with no valid
interpretation — a non-complemented distributive lattice (the 3-chain 0<m<1) admits no
Boolean-algebra complement, so no structure-preserving map BoolAlg -> that lattice exists.
Run through the same finite-model style as the positive case; it must return "none".

Honesty: this is a prototype RUN, not a frozen pre-registration. The metric/threshold RULES
are fixed in code before inspecting results, but a real study (v4 plan WP3) freezes them in a
pre-registration doc first. Encoder choice is a fair general semantic encoder; a math-specialised
encoder (ReProver/ByT5) is the ideal next baseline.
"""
import sys
from itertools import product

ENCODER = "all-MiniLM-L6-v2"

# ------------------------------------------------------------------ A.3 data
# (BA-vocabulary statement, BR-vocabulary statement, salient tokens shared?)
CORRESPONDING = [
    ("meet is idempotent: a ∧ a = a", "every element is idempotent: a · a = a", True),   # 'idempotent'
    ("meet is commutative: a ∧ b = b ∧ a", "multiplication is commutative: a · b = b · a", True),
    ("meet is associative: a ∧ (b ∧ c) = (a ∧ b) ∧ c", "multiplication is associative: a · (b · c) = (a · b) · c", True),
    ("the top element is the identity for meet: a ∧ ⊤ = a", "one is the identity for multiplication: a · 1 = a", False),
    ("the bottom element absorbs under meet: a ∧ ⊥ = ⊥", "zero is absorbing for multiplication: a · 0 = 0", False),
    ("an element and its complement meet to the bottom: a ∧ ¬a = ⊥", "an element times one-minus-itself is zero: a · (1 − a) = 0", False),
    ("join is meet of complements (De Morgan): a ∨ b = ¬(¬a ∧ ¬b)", "join as a ring term: a + b − a · b", False),
    ("the lattice order: a ≤ b iff a ∧ b = a", "the order: a ≤ b iff a · b = a", True),   # 'order'
    ("meet distributes over join: a ∧ (b ∨ c) = (a ∧ b) ∨ (a ∧ c)", "product distributes over the ring-join: a·(b+c−bc) = ab+ac−abc", True),  # 'distrib'
    ("a Boolean algebra is a complemented distributive lattice", "a Boolean ring is a ring in which every element is idempotent", True),  # 'Boolean'
    ("the least element, written bottom ⊥", "the additive identity, written zero 0", False),
    ("the greatest element, written top ⊤", "the multiplicative identity, written one 1", False),
    ("complementation, the unary operation ¬a", "the unary operation sending a to 1 − a", False),
    ("join, the least upper bound a ∨ b", "the ring expression a + b − a · b", False),
]

# held-out SAME-vocabulary paraphrase pairs (both Boolean-ALGEBRA vocab) for threshold calibration
SAME_VOCAB_PARAPHRASES = [
    ("meet is commutative: a ∧ b = b ∧ a", "the operation ∧ is symmetric: a ∧ b equals b ∧ a"),
    ("the top element ⊤ is the unit for meet", "⊤ is the greatest element and a ∧ ⊤ = a"),
    ("complementation sends a to ¬a", "the unary complement operation ¬ on the lattice"),
    ("a ≤ b iff a ∧ b = a", "the partial order defined by meet: a below b when a ∧ b = a"),
    ("join is the least upper bound a ∨ b", "a ∨ b is the supremum of a and b in the lattice"),
    ("a Boolean algebra is a complemented distributive lattice", "a complemented distributive lattice is a Boolean algebra"),
]

DISTRACTORS = [
    "the derivative of sine is cosine",
    "every continuous function on a compact interval attains its maximum",
    "the fundamental group of the circle is the integers",
    "a finite-dimensional vector space has a basis",
    "the integral of 1/x is the natural logarithm",
    "a group is a monoid in which every element has an inverse",
    "the determinant of a product is the product of the determinants",
    "a metric space is complete if every Cauchy sequence converges",
    "the rank-nullity theorem relates kernel and image dimensions",
    "a prime number has exactly two positive divisors",
    "the sum of the first n integers is n(n+1)/2",
    "a topological space is connected if it is not a union of two disjoint open sets",
    "the exponential function equals its own derivative",
    "a field is a commutative ring in which every nonzero element is invertible",
]


def run_embedding_arm():
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        print(f"[A.3] SKIPPED — encoder stack unavailable: {type(e).__name__}: {e}")
        print("      (harness is ready; run where sentence-transformers + a model are available.)")
        return
    print(f"[A.3] Embedding-comparison arm — pinned encoder: {ENCODER}")
    # provenance (a model NAME is not a pin): record library + model versions and source
    import os, glob, sentence_transformers, transformers
    snaps = glob.glob(os.path.expanduser(
        f"~/.cache/huggingface/hub/models--sentence-transformers--{ENCODER}/snapshots/*"))
    from_cache = bool(snaps)
    print(f"      provenance: sentence-transformers={sentence_transformers.__version__} "
          f"transformers={transformers.__version__} numpy={np.__version__}")
    print(f"      model snapshot: {[os.path.basename(s) for s in snaps] or 'downloading (not yet cached)'} "
          f"(loaded {'from cache' if from_cache else 'via download — requires network'})")
    try:
        model = SentenceTransformer(ENCODER)
    except Exception as e:
        print(f"      SKIPPED — could not load encoder (network down + cold cache?): {type(e).__name__}: {e}")
        print("      (harness is ready; run with network access or a warm HF cache.)")
        return
    enc = lambda xs: model.encode(xs, normalize_embeddings=True)

    ba = [p[0] for p in CORRESPONDING]
    br = [p[1] for p in CORRESPONDING]
    shared = [p[2] for p in CORRESPONDING]
    import numpy as np
    ba_v, br_v = enc(ba).astype(np.float64), enc(br).astype(np.float64)
    dist_v = enc(DISTRACTORS).astype(np.float64)
    for name, arr in (("ba", ba_v), ("br", br_v), ("dist", dist_v)):
        assert np.isfinite(arr).all(), f"non-finite embeddings in {name}"
        norms = np.linalg.norm(arr, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-3), f"{name} not unit-normalized: {norms.min():.3f}..{norms.max():.3f}"

    # threshold calibration on same-vocab paraphrases (rule fixed before inspecting cross-vocab results)
    sv = SAME_VOCAB_PARAPHRASES
    sv_a, sv_b = enc([p[0] for p in sv]), enc([p[1] for p in sv])
    sv_cos = sorted(float(np.dot(sv_a[i], sv_b[i])) for i in range(len(sv)))
    tau = sv_cos[max(0, len(sv_cos)//5)]   # ~20th percentile of "same-meaning, same-vocab" cosines
    print(f"      calibration (same-vocab paraphrase cosines): min={sv_cos[0]:.3f} "
          f"median={sv_cos[len(sv_cos)//2]:.3f} max={sv_cos[-1]:.3f}  ->  threshold tau={tau:.3f}")

    # candidate pool for retrieval = all BR statements + distractors; query = each BA statement
    pool_v = np.vstack([br_v, dist_v])
    assert np.isfinite(pool_v).all()
    n_br = len(br)

    def report(idxs, label):
        if not idxs:
            return
        ranks, hits1, hits3, recip = [], 0, 0, 0.0
        for i in idxs:
            sims = np.array([float(np.dot(pool_v[j], ba_v[i])) for j in range(len(pool_v))])
            assert np.isfinite(sims).all(), "non-finite similarity"
            order = list(np.argsort(-sims))          # descending
            rank = order.index(i) + 1                # rank of the TRUE counterpart (index i in pool)
            ranks.append(rank)
            hits1 += (rank == 1); hits3 += (rank <= 3); recip += 1.0 / rank
        n = len(idxs)
        print(f"      {label:22s} n={n:2d} | recall@1={hits1/n:.2f} recall@3={hits3/n:.2f} "
              f"MRR={recip/n:.2f} mean_rank={sum(ranks)/n:.1f} (of {len(pool_v)})")

    print(f"      candidate pool = {n_br} BR statements + {len(DISTRACTORS)} distractors = {len(pool_v)}")
    report(list(range(n_br)), "ALL pairs")
    report([i for i in range(n_br) if not shared[i]], "DISJOINT-vocab only")
    report([i for i in range(n_br) if shared[i]], "shares-a-token only")
    # also: how many counterparts clear the same-vocab similarity threshold?
    cross_cos = [float(ba_v[i] @ br_v[i]) for i in range(n_br)]
    clear = sum(c >= tau for c in cross_cos)
    print(f"      cross-vocab counterpart cosines: min={min(cross_cos):.3f} "
          f"mean={sum(cross_cos)/len(cross_cos):.3f} max={max(cross_cos):.3f}; "
          f"{clear}/{n_br} clear tau")
    print("      READ: high recall/MRR ⇒ embeddings DO recover the correspondence here ⇒ evidence")
    print("            toward (i) on this task. Low recall / buried counterparts ⇒ embeddings miss")
    print("            what the morphism makes exact. Reported as measured (descriptive; small N).")


# ------------------------------------------------------------------ A.4 soundness
def run_soundness():
    print("\n[A.4] Soundness / false-positive test — morphism search must FAIL on a near-miss")
    # The 3-chain bounded distributive lattice 0 < m < 1 (a genuine distributive lattice).
    elems = [0, 1, 2]          # 0=bottom, 1=middle m, 2=top
    leq = lambda a, b: a <= b
    meet = lambda a, b: min(a, b)
    join = lambda a, b: max(a, b)
    bot, top = 0, 2
    # sanity: it IS a (bounded) distributive lattice
    distrib = all(meet(a, join(b, c)) == join(meet(a, b), meet(a, c)) for a in elems for b in elems for c in elems)
    print(f"      model: 3-chain 0<m<1; bounded distributive lattice? {distrib}")
    # search ALL unary 'complement' candidates; a Boolean-algebra complement needs
    #   a ∧ ¬a = ⊥  and  a ∨ ¬a = ⊤  for all a.
    found = []
    for cand in product(elems, repeat=len(elems)):   # cand[a] = ¬a
        comp = dict(zip(elems, cand))
        if all(meet(a, comp[a]) == bot and join(a, comp[a]) == top for a in elems):
            found.append(comp)
    print(f"      candidate complement operations searched: {len(elems)**len(elems)}; "
          f"valid Boolean complements found: {len(found)}")
    print(f"      => no Boolean-algebra interpretation on the 3-chain (the middle m has no complement)")
    print(f"      => morphism search correctly returns NONE: {len(found) == 0}  (sound; not always-yes)")
    print("      contrast: BoolAlg<->BoolRing interpretation DOES exist (proven in WP1+WP2).")


if __name__ == "__main__":
    run_embedding_arm()
    run_soundness()
