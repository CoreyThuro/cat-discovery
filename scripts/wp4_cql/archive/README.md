# Archive — exploratory CQL/AQL iterations (scratch / superseded)

Debugging trace from getting Piece B to load in the CQL IDE. **Not canonical** — the polished,
confirmed-working artifacts are one level up:
- `../piece_b_valid_migration.cql` (S, I_valid, S_new, mapping F, I_new, I_back = delta F I_new)
- `../piece_b_violation_spike.cql` (S + I_violating; fails by design with the chase contradiction)

Contents here:
- `piece_b_bare_ordered.cql` — the combined working file these two were split from (last working iteration).
- `piece_b_bare.cql`, `piece_b_bare_equations.cql` — earlier iterations while fixing syntax.
- `piece_b.aql` — the original draft (rejected by the IDE); annotated with the fixes that were applied.

Kept only as a record of the syntax-debugging path; see `../README.md` for the fixes that mattered.
