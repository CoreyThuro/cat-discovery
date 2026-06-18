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

instance I_valid = literal : S {
  generators
    S1 S2 : Struct
    C1 C2 : Carrier
    H1 H2 : Hom
    F1 F2 : Fun
  equations
    carrier(S1) = C1
    carrier(S2) = C2
    cname(C1) = "carrier-of-S1"
    cname(C2) = "carrier-of-S2"
    src(H1) = S1
    tgt(H1) = S2
    fun(H1) = F1
    src(H2) = S1
    tgt(H2) = S1
    fun(H2) = F2
    dom(F1) = C1
    cod(F1) = C2
    dom(F2) = C1
    cod(F2) = C1
}

instance I_violating = literal : S {
  generators
    S1 S2 : Struct
    C1 C2 : Carrier
    H1 H2 H3 : Hom
    F1 F2 F3 : Fun
  equations
    carrier(S1) = C1
    carrier(S2) = C2
    cname(C1) = "carrier-of-S1"
    cname(C2) = "carrier-of-S2"
    src(H1) = S1
    tgt(H1) = S2
    fun(H1) = F1
    src(H2) = S1
    tgt(H2) = S1
    fun(H2) = F2
    src(H3) = S1
    tgt(H3) = S2
    fun(H3) = F3
    dom(F1) = C1
    cod(F1) = C2
    dom(F2) = C1
    cod(F2) = C1
    dom(F3) = C2
    cod(F3) = C2
}

schema S_new = literal : Ty {
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
    hkind : Hom -> String
}

mapping F = literal : S -> S_new {
  entity Struct -> Struct
  foreign_keys
    carrier -> carrier
  entity Carrier -> Carrier
  attributes
    cname -> cname
  entity Hom -> Hom
  foreign_keys
    src -> src
    tgt -> tgt
    fun -> fun
  entity Fun -> Fun
  foreign_keys
    dom -> dom
    cod -> cod
}

instance I_new = literal : S_new {
  generators
    S1 S2 : Struct
    C1 C2 : Carrier
    H1 H2 : Hom
    F1 F2 : Fun
  equations
    carrier(S1) = C1
    carrier(S2) = C2
    cname(C1) = "carrier-of-S1"
    cname(C2) = "carrier-of-S2"
    src(H1) = S1
    tgt(H1) = S2
    fun(H1) = F1
    hkind(H1) = "iso"
    src(H2) = S1
    tgt(H2) = S1
    fun(H2) = F2
    hkind(H2) = "endo"
    dom(F1) = C1
    cod(F1) = C2
    dom(F2) = C1
    cod(F2) = C1
}

instance I_back = delta F I_new
