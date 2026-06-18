(*
  WP4 (full-strength) — Piece B, VIOLATION SPIKE file.
  EXPECTED TO FAIL: loading I_violating triggers a CQL chase CONTRADICTION (rejection, not
  silent merge). This is the chase-rejection reservation from the v4 plan — CONFIRMED by an
  actual CQL IDE run:

      Error in instance I_violating: java.lang.RuntimeException: Contradictions:
      carrier-of-S2 = carrier-of-S1

  Why: the seeded bad row H3 (fun(H3)=F3, dom(F3)=C2) forces, via path_equation
  Hom.src.carrier = Hom.fun.dom, that C1 = C2. Because C1/C2 are attribute-distinguished by
  cname ("carrier-of-S1" != "carrier-of-S2"), the chase cannot merge them and rejects.

  Kept SEPARATE from the valid/migration file because the contradiction halts execution.
  Syntax matches the confirmed-working piece_b_bare_ordered.cql (path_equations before
  attributes; imports sql; no manual String).
*)

typeside Ty = literal {
  imports
    sql
}

schema S = literal : Ty {
  entities
    Struct Carrier Hom Fun
  foreign_keys
    carrier : Struct -> Carrier
    src     : Hom -> Struct
    tgt     : Hom -> Struct
    fun     : Hom -> Fun
    dom     : Fun -> Carrier
    cod     : Fun -> Carrier
  path_equations
    Hom.src.carrier = Hom.fun.dom
    Hom.tgt.carrier = Hom.fun.cod
  attributes
    cname : Carrier -> String
}

(* seeded violation: dom(F3) = C2 but src(H3).carrier = C1  ->  forces C1 = C2  ->  contradiction *)
instance I_violating = literal : S {
  generators
    S1 S2 : Struct
    C1 C2 : Carrier
    H1 H2 H3 : Hom
    F1 F2 F3 : Fun
  equations
    carrier(S1) = C1   carrier(S2) = C2
    cname(C1) = "carrier-of-S1"   cname(C2) = "carrier-of-S2"
    src(H1) = S1   tgt(H1) = S2   fun(H1) = F1
    src(H2) = S1   tgt(H2) = S1   fun(H2) = F2
    src(H3) = S1   tgt(H3) = S2   fun(H3) = F3
    dom(F1) = C1   cod(F1) = C2
    dom(F2) = C1   cod(F2) = C1
    dom(F3) = C2   cod(F3) = C2
}
