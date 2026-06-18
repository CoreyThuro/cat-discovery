# categorical-discovery

A small, self-contained prototype for making **categorical mathematical structure** usable alongside **embedding-based retrieval**. The point is not to rediscover the familiar slogan that categories preserve structure and embeddings are approximate. The point is to make that distinction operational: put both methods on the same mathematical correspondences, find the right categorical representation for each kind of structure, and test what each method can actually do.

**Design thesis:** embeddings are good candidate generators; categorical structure is the layer that can certify, transport, and preserve meaning once a candidate correspondence is on the table. The prototype implements that bridge pattern in two settings:

- algebraic theories, where the right categorical language is **Lawvere theories / interpretations**;
- relational mathematical knowledge schemas, where the right categorical language is **ologs / CQL / functorial data migration**.

The main lesson is tool-correctness. An early plan tried to force Boolean algebra into CQL; an independent critic caught that this was the wrong categorical tool, because CQL schemas have unary arrows while Boolean operations are binary. The final prototype turns that correction into the architecture: use Lawvere theories for algebra, and use ologs/CQL for relational knowledge.

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

## What this contributes — and what it doesn't

- **Bridge pattern:** use embeddings to retrieve or rank plausible mathematical correspondences; use categorical maps to certify what structure is actually preserved and to transport data/theorems/instances along that correspondence.
- **Tool-correct categorical modeling:** Lawvere theories handle algebraic operations; ologs/CQL handle relational schemas and integrity constraints. The repo documents the failed design path as well as the corrected one.
- **A measured contrast, not a slogan:** the embedding baseline partially recovers the BA↔BR relationship, but lexical overlap accounts for much of the apparent success. On disjoint vocabulary it is unreliable at exact matching; the categorical map is exact because it encodes the structure, not because it is "more semantic search."
- **A working CQL integrity example:** the relational schema is not just drawn as a diagram; CQL rejects a bad instance by chase contradiction and validates a schema migration.
- **Does not show:** that embeddings fail in general, or that category theory solves mathematical discovery. The set is small and hand-curated, the encoder is one general-purpose model, and the examples are known classical correspondences. This is a prototype of an integration pattern, not a real-task benchmark or a novel-discovery result.

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
