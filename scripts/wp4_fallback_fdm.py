#!/usr/bin/env python3
"""
WP4-FALLBACK — Piece B olog / functorial data migration, finite-set engine.

THIS IS THE FALLBACK. It demonstrates the finite-set migration MECHANISM:
  - a genuine olog (objects + UNARY generators + non-vacuous path equations),
  - integrity checking that REJECTS a seeded violating row,
  - Δ (delta / reindexing) functorial data migration across a schema evolution,
    shown to preserve the path-equation integrity by construction,
  - a naive (non-functorial) transfer that breaks integrity, caught.

It does NOT provide CQL/AQL's theorem-prover-backed compile-time integrity / chase
behaviour — that is the intended FULL-STRENGTH backend (Direction D / Q3), prepared as
first-class artifacts in scripts/wp4_cql/ and to be RUN where a JDK + CQL engine exist.
Σ/Π (the left/right adjoints / Kan extensions) are likewise the CQL-backed operations;
here we implement Δ, the canonical always-defined migration, to show integrity preservation.

The seeded violating row appears in BOTH this fallback and the CQL artifacts.
"""

# ------------------------------------------------------------------ schema (an olog)
# objects + unary generators (foreign keys) g: src_obj -> tgt_obj
GENERATORS = {
    "carrier": ("Struct", "Carrier"),
    "src":     ("Hom", "Struct"),
    "tgt":     ("Hom", "Struct"),
    "fun":     ("Hom", "Fun"),
    "dom":     ("Fun", "Carrier"),
    "cod":     ("Fun", "Carrier"),
}
# non-vacuous path equations: two independently-sourced paths Hom -> Carrier that can disagree
PATH_EQUATIONS = [
    ("Hom", ["src", "carrier"], ["fun", "dom"]),   # a hom's source carrier = its function's domain
    ("Hom", ["tgt", "carrier"], ["fun", "cod"]),   # a hom's target carrier = its function's codomain
]


def eval_path(inst, path, e):
    """Follow a path of generators starting at element e."""
    for g in path:
        e = inst[g][e]
    return e


def check_integrity(inst, equations=PATH_EQUATIONS):
    """Return list of (object, element, equation) violations. Empty list = consistent."""
    violations = []
    for (obj, p, q) in equations:
        for e in inst["_obj"][obj]:
            if eval_path(inst, p, e) != eval_path(inst, q, e):
                violations.append((obj, e, f"{'.'.join(p)} != {'.'.join(q)}  "
                                              f"({eval_path(inst,p,e)} vs {eval_path(inst,q,e)})"))
    return violations


# ------------------------------------------------------------------ instances
# Carriers are ATTRIBUTE-DISTINGUISHED (distinct names) so a mismatch is a genuine
# inconsistency, never a silent merge (mirrors the CQL chase-rejection requirement).
CARRIER_NAME = {"C1": "carrier-of-S1", "C2": "carrier-of-S2"}

VALID = {
    "_obj": {"Struct": ["S1", "S2"], "Carrier": ["C1", "C2"],
             "Hom": ["H1", "H2"], "Fun": ["F1", "F2"]},
    "carrier": {"S1": "C1", "S2": "C2"},
    "src": {"H1": "S1", "H2": "S1"},
    "tgt": {"H1": "S2", "H2": "S1"},
    "fun": {"H1": "F1", "H2": "F2"},
    "dom": {"F1": "C1", "F2": "C1"},
    "cod": {"F1": "C2", "F2": "C1"},
}

# the SEEDED VIOLATING ROW: H3's function F3 has dom=C2 but src(H3)=S1 has carrier C1 (C1 != C2)
VIOLATING = {
    "_obj": {"Struct": ["S1", "S2"], "Carrier": ["C1", "C2"],
             "Hom": ["H1", "H2", "H3"], "Fun": ["F1", "F2", "F3"]},
    "carrier": {"S1": "C1", "S2": "C2"},
    "src": {"H1": "S1", "H2": "S1", "H3": "S1"},
    "tgt": {"H1": "S2", "H2": "S1", "H3": "S2"},
    "fun": {"H1": "F1", "H2": "F2", "H3": "F3"},
    "dom": {"F1": "C1", "F2": "C1", "F3": "C2"},        # <-- F3.dom = C2  (should be C1)
    "cod": {"F1": "C2", "F2": "C1", "F3": "C2"},
}


# ------------------------------------------------------------------ Δ migration (schema evolution)
def delta_forget(inst, drop_generators=(), drop_objects=()):
    """
    Δ along the inclusion F : S_old ↪ S_new (S_new = S_old + new attribute/entity).
    Δ_F reindexes an S_new-instance to an S_old-instance by precomposition — i.e. it
    simply forgets the new generators/objects. Path equations on the shared part are
    preserved BY CONSTRUCTION (Δ does not touch the retained generators).
    """
    out = {"_obj": {o: list(es) for o, es in inst["_obj"].items() if o not in drop_objects}}
    for g, table in inst.items():
        if g == "_obj" or g in drop_generators:
            continue
        sobj, tobj = GENERATORS.get(g, (None, None))
        if sobj in drop_objects or tobj in drop_objects:
            continue
        out[g] = dict(table)
    return out


def main():
    print("=" * 72)
    print("WP4-FALLBACK  Piece B — olog + finite-set functorial data migration")
    print("  (mechanism demo; full-strength prover/chase integrity = CQL, see scripts/wp4_cql/)")
    print("=" * 72)

    print("\n[schema] objects: Struct, Carrier, Hom, Fun")
    print("  unary generators:", ", ".join(f"{g}:{s}->{t}" for g, (s, t) in GENERATORS.items()))
    print("  path equations (non-vacuous — independently-sourced Hom->Carrier paths):")
    for obj, p, q in PATH_EQUATIONS:
        print(f"    on {obj}:  {'.'.join(p)}  ==  {'.'.join(q)}")
    print("  carriers attribute-distinguished:", CARRIER_NAME)

    print("\n[integrity] VALID instance:")
    v = check_integrity(VALID)
    print(f"  violations: {len(v)}  ->  {'CONSISTENT (accepted)' if not v else v}")

    print("\n[integrity] VIOLATING instance (seeded bad row H3: fun.dom=C2 but src.carrier=C1):")
    v = check_integrity(VIOLATING)
    print(f"  violations: {len(v)}  ->  {'REJECTED' if v else 'accepted'}")
    for obj, e, msg in v:
        print(f"    {obj} {e}: {msg}")

    print("\n[Δ migration] schema evolution: add attribute  label: Hom -> Str  (S_old ↪ S_new)")
    # S_new instance = VALID + a label table; Δ forgets it, must stay consistent by construction
    inst_new = {k: (dict(v) if k != "_obj" else {o: list(es) for o, es in v.items()})
                for k, v in VALID.items()}
    inst_new["label"] = {"H1": "iso", "H2": "endo"}        # the new attribute's data
    migrated = delta_forget(inst_new, drop_generators=("label",))
    v = check_integrity(migrated)
    print(f"  Δ-migrated S_new -> S_old; 'label' forgotten; violations: {len(v)} "
          f"-> {'integrity preserved by construction' if not v else v}")

    print("\n[broken transfer] a NAIVE (non-functorial) migration rewires H1.fun to F3-like dom=C2:")
    broken = {k: (dict(v) if k != "_obj" else {o: list(es) for o, es in v.items()})
              for k, v in VALID.items()}
    broken["dom"] = dict(broken["dom"]); broken["dom"]["F1"] = "C2"   # now F1.dom=C2 != src(H1).carrier=C1
    v = check_integrity(broken)
    print(f"  violations: {len(v)}  ->  {'CAUGHT (rejected)' if v else 'undetected!'}")
    for obj, e, msg in v:
        print(f"    {obj} {e}: {msg}")

    print("\n" + "=" * 72)
    print("WP4-FALLBACK demonstrates: non-vacuous olog path equations; seeded violation")
    print("rejected; Δ migration preserves integrity; naive transfer caught. Prover/chase-")
    print("backed integrity (Direction D / Q3) is the CQL backend — see scripts/wp4_cql/.")
    print("=" * 72)


if __name__ == "__main__":
    main()
