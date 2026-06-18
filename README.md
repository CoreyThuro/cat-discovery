# categorical-discovery

A small, self-contained prototype investigating whether **categorical structure** (theory morphisms, ologs, functorial data migration) captures mathematical knowledge that **embedding-based retrieval** misses — and, where it does, *how*.

**Thesis:** embeddings retrieve by **similarity**; categorical structure **transports along well-typed, structure-preserving maps**. Embeddings *approximate* relationships; categorical maps *certify and migrate* them. The prototype uses the categorically-correct tool for each kind of structure, and measures both against a fair embedding baseline.

## The two pieces

### Piece A — theory morphisms & interpretations (Lawvere theories)
On **Boolean algebras ↔ Boolean rings** and the **idempotents** of a commutative ring:
- **A.1 — exact transport.** BoolAlg ↔ BoolRing is a *term-equivalence* = an **isomorphism of Lawvere theories** (char-2 makes `+ = −`); the BR→BA→BR round-trip recovers `(+, ·)` exactly.
- **A.2 — lossy transport (the non-degenerate case).** The idempotents functor `E : Mod(CommRing) → Mod(BoolAlg)`, `R ↦ idem(R)`, is **essentially surjective** yet **not an equivalence** — not essentially injective, not full, not faithful. A genuine structure-preserving map that *forgets* information while being *exact* about what it preserves. This is what off-the-shelf similarity embeddings have no analogue for.
- **A.3 — embedding-comparison arm.** *Measures* whether a fair similarity encoder recovers the BA↔BR correspondence (it is not assumed).
- **A.4 — soundness.** The morphism search must **fail** on a near-miss (a non-complemented distributive lattice has no Boolean complement → no interpretation).

Run: `python3 scripts/wp12_lawvere_boolalg_boolring.py` · `python3 scripts/wp3_embedding_and_soundness.py`

### Piece B — olog / functorial data migration (ologs + CQL)
A small **relational** mathlib-knowledge olog (entities + unary arrows + real commutative-diagram path equations), with **functorial data migration** under schema evolution:
- **Full-strength (CQL):** Δ/Σ/Π migration with **theorem-prover / chase-backed compile-time integrity**; a seeded constraint violation is **rejected** by the chase (not silently merged).
- **Fallback (Python):** the same finite-set migration *mechanism* without the prover layer.

Run: `python3 scripts/wp4_fallback_fdm.py` · CQL: see [`scripts/wp4_cql/`](scripts/wp4_cql/)

## Results

**Piece A (computed witnesses — `wp12`):** `E` confirmed essentially surjective (`idem(B)=B` for a Boolean ring) but non-invertible — `Z/6, Z/10, Z/15` all collapse to the same 4-element Boolean algebra; `F₂[ε]/(ε²)` gives a non-faithful witness; `Z/6→F₂` a non-full one (unrealized Boolean hom `3↦0,4↦1`). BA↔BR round-trip exact. *(Finite witness suite, not a general mechanization; the general facts are classical.)*

**Embedding arm (`wp3`, encoder `all-MiniLM-L6-v2`):**

| subset | recall@1 | recall@3 | MRR |
|---|---|---|---|
| all pairs | 0.64 | 0.86 | 0.78 |
| **disjoint-vocabulary only** | **0.38** | 0.75 | 0.61 |
| shares-a-token only | 1.00 | 1.00 | 1.00 |

The headline (0.64) is inflated by lexical overlap; on genuinely **disjoint vocabulary** the encoder drops to recall@1 0.38, and only **3/14** counterparts clear a calibrated same-meaning threshold. **Soundness:** 0 valid complements found on the 3-chain → the search correctly returns "no interpretation" (it discriminates).

**Piece B (CQL, validated):** the violation spike rejects via a chase **contradiction** (`carrier-of-S2 = carrier-of-S1`, i.e. reject-not-merge); the valid-migration file — including `I_back = delta F I_new` — loads and chases cleanly. Prover-backed compile-time integrity confirmed.

## What this shows — and what it doesn't

- **Shows (mechanism):** categorical maps transport structure *exactly* and preserve integrity *by construction*, where a fair similarity encoder only *approximates* the correspondence and is unreliable once vocabulary is disjoint.
- **Does not show:** that "embeddings suffice" is false as *real-task sufficiency* — the set is small and hand-curated, the vocabulary maximally disjoint, the encoder a single general-purpose model. This is a **mechanism demonstration on a known, classical correspondence**, not novel discovery.

## Layout

```text
scripts/
  wp12_lawvere_boolalg_boolring.py   # Piece A.1/A.2 — Lawvere/idempotents witness suite (stdlib only)
  wp3_embedding_and_soundness.py     # Piece A.3 embedding arm + A.4 soundness test
  wp4_fallback_fdm.py                # Piece B — finite-set functorial-migration mechanism (stdlib only)
  wp4_cql/                           # Piece B — full-strength CQL/AQL (validated); see its README
requirements.txt                     # deps for the embedding arm (Piece A.1/A.2 + B fallback are stdlib)
```

## Running

- **Piece A.1/A.2 and Piece B fallback:** standard library only — just `python3 scripts/<file>.py`.
- **Piece A.3 embedding arm:** `pip install -r requirements.txt`. Loads `all-MiniLM-L6-v2` from the Hugging Face cache or downloads it (needs network); skips cleanly if neither is available.
- **Piece B (full-strength CQL):** a JDK + the CQL/AQL engine ([categoricaldata.net](https://categoricaldata.net)); see [`scripts/wp4_cql/README.md`](scripts/wp4_cql/README.md).
