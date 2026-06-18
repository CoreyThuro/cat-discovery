# WP4 (full-strength) — Piece B in CQL/AQL

**Status: FULLY CQL-VALIDATED.** Both files ran in the CQL IDE: the violation spike rejects via a
chase contradiction, and the valid-migration file (including `I_back = delta F I_new`) loads and
chases cleanly. The full-strength backend (Direction D / Q3 — prover/chase-backed compile-time
integrity, which the Python fallback cannot provide) is confirmed, not merely prepared.

## Confirmed result (the chase-rejection spike)
Loading the seeded violating instance produced a chase **contradiction** (rejection):
```
Error in instance I_violating: java.lang.RuntimeException: Contradictions:
carrier-of-S2 = carrier-of-S1
```
Why: the bad row `H3` (`fun(H3)=F3`, `dom(F3)=C2`) forces, via `Hom.src.carrier = Hom.fun.dom`,
that `C1 = C2`; because `C1`/`C2` are attribute-distinguished by `cname`, the chase cannot merge
them and rejects. This is exactly the reject-not-merge behaviour the attribute distinction was
designed to force.

## Files
- [`piece_b_valid_migration.cql`](piece_b_valid_migration.cql) — `S`, `I_valid`, `S_new`, mapping `F`,
  `I_new`, `I_back = delta F I_new`. **Ran cleanly** (no parser/typechecker/chase errors; wall-clock ~0.1s)
  → validates `I_valid`, `S_new`, `F`, `I_new`, and the delta migration `I_back`. Kept separate from the
  violating instance, whose contradiction halts execution.
- [`piece_b_violation_spike.cql`](piece_b_violation_spike.cql) — `S` + `I_violating`; **fails by design**
  with the chase contradiction above (this IS the confirmed reject-not-merge result).
- [`archive/`](archive/) — exploratory iterations + the original `.aql` draft (scratch/superseded; the
  combined working file `piece_b_bare_ordered.cql` these were split from lives there too).

Both runs were performed in the CQL IDE (the violation spike's contradiction and the clean valid-migration
run are recorded above). For full reproducibility, record the exact CQL/AQL engine build + JDK version used.

## Syntax fixes that made it load (from the working `piece_b_bare_ordered.cql`)
- `path_equations` must come **before** `attributes` in a schema.
- typeside needs `imports sql`; declaring `String` manually makes string literals ill-sorted.
- attribute renamed `label` → `hkind`.
- mapping uses repeated `entity X -> Y` declarations + grouped `foreign_keys` / `attributes`;
  dotted names like `Struct.carrier -> carrier` are rejected.

Confirmed working types/syntax: attribute type is `String` (from `imports sql`); the mapping
interleaves `entity X -> Y` with its own `foreign_keys`/`attributes` per entity.

## Remaining
None. WP4 is fully CQL-validated. (Optional future work: a larger relational slice / more
schema-evolution steps — not required for the prototype.)
