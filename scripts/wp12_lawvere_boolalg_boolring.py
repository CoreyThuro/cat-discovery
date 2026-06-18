#!/usr/bin/env python3
"""
WP1+WP2 — Piece A centerpiece (Lawvere theories & the idempotents interpretation).

This is an EXECUTABLE WITNESS SUITE over finite cases, not a mechanization of the
general proofs. The Lawvere-theory isomorphism BoolAlg <-> BoolRing and essential
surjectivity (idem(B)=B for *every* Boolean algebra B) are classical mathematical
facts; here we *exhibit and sanity-check* them on specific small models, and *prove*
the finite witnesses (object collapse, non-full, non-faithful) outright:

  A.1  BoolAlg <-> BoolRing term-equivalence (char-2: + = -), round-trip on a model.
  A.2  E : Mod(CommRing) -> Mod(BoolAlg),  R |-> idem(R) = ({a : a*a=a}, meet=a*b,
       join=a+b-a*b, neg=1-a, bot=0, top=1), shown to be a genuine functor that is:
         - essentially surjective   (idem(B) = B for a Boolean ring B)
         - NOT essentially injective (Z/6, Z/10, Z/15 -> the same 4-element BA)
         - NOT faithful             (F2[e]/(e^2): e|->0 and e|->e collapse under E)
         - NOT full                 (one ring hom Z/6->F2, two BA homs 4->2)
       plus functoriality E(g o f) = E(g) o E(f), E(id)=id on named witnesses.

No dependencies beyond the standard library. Run: python3 scripts/wp12_lawvere_boolalg_boolring.py
"""
from itertools import product


# ---------------------------------------------------------------- finite commutative rings
class Ring:
    """A finite commutative unital ring given by its element list and +,* operations."""
    def __init__(self, name, elements, add, mul, zero, one):
        self.name = name
        self.elements = list(elements)
        self.add = add          # (a,b) -> a+b
        self.mul = mul          # (a,b) -> a*b
        self.zero = zero
        self.one = one


def Zmod(n):
    return Ring(f"Z/{n}", range(n),
                lambda a, b: (a + b) % n, lambda a, b: (a * b) % n, 0, 1)


def dual_numbers_F2():
    """F2[e]/(e^2): elements (a,b) ~ a + b*e over F2; e=(0,1)."""
    els = list(product((0, 1), repeat=2))
    add = lambda x, y: ((x[0] + y[0]) % 2, (x[1] + y[1]) % 2)
    # (a+be)(c+de) = ac + (ad+bc)e   (e^2 = 0), mod 2
    mul = lambda x, y: ((x[0] * y[0]) % 2, (x[0] * y[1] + x[1] * y[0]) % 2)
    return Ring("F2[e]/(e^2)", els, add, mul, (0, 0), (1, 0))


def product_ring(R, S):
    els = [(r, s) for r in R.elements for s in S.elements]
    add = lambda x, y: (R.add(x[0], y[0]), S.add(x[1], y[1]))
    mul = lambda x, y: (R.mul(x[0], y[0]), S.mul(x[1], y[1]))
    return Ring(f"{R.name} x {S.name}", els, add, mul, (R.zero, S.zero), (R.one, S.one))


# ---------------------------------------------------------------- the functor E and BA structure
def idempotents(R):
    return [a for a in R.elements if R.mul(a, a) == a]


def boolean_algebra_on_idem(R):
    """Return (carrier, meet, join, neg, bot, top) = E(R)."""
    sub = lambda a, b: R.add(a, R.mul(b, R.elements[0] and R.zero or R.zero))  # placeholder, unused
    carrier = idempotents(R)
    # a - b  ==  a + (-b);  -b is the additive inverse of b
    def neg_add(b):
        return next(x for x in R.elements if R.add(b, x) == R.zero)
    meet = lambda a, b: R.mul(a, b)
    join = lambda a, b: R.add(R.add(a, b), neg_add(R.mul(a, b)))   # a + b - a*b
    compl = lambda a: R.add(R.one, neg_add(a))                     # 1 - a
    return carrier, meet, join, compl, R.zero, R.one


# ---------------------------------------------------------------- Boolean-algebra axiom check
def verify_BA_axioms(carrier, meet, join, compl, bot, top):
    ok = True
    C = carrier
    def chk(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print(f"      FAIL: {msg}")
    # closure
    chk(all(meet(a, b) in C and join(a, b) in C for a in C for b in C), "closure of meet/join")
    chk(all(compl(a) in C for a in C), "closure of complement")
    # commutativity, associativity, idempotence
    chk(all(meet(a, b) == meet(b, a) and join(a, b) == join(b, a) for a in C for b in C), "commutativity")
    chk(all(meet(a, meet(b, c)) == meet(meet(a, b), c) for a in C for b in C for c in C), "assoc meet")
    chk(all(join(a, join(b, c)) == join(join(a, b), c) for a in C for b in C for c in C), "assoc join")
    # absorption
    chk(all(meet(a, join(a, b)) == a and join(a, meet(a, b)) == a for a in C for b in C), "absorption")
    # distributivity
    chk(all(meet(a, join(b, c)) == join(meet(a, b), meet(a, c)) for a in C for b in C for c in C), "distributivity")
    # identities and complement laws
    chk(all(join(a, bot) == a and meet(a, top) == a for a in C), "bot/top identities")
    chk(all(meet(a, compl(a)) == bot and join(a, compl(a)) == top for a in C), "complement laws")
    return ok


# ---------------------------------------------------------------- ring/BA homomorphism enumeration
def unital_ring_homs(R, S):
    """Brute-force all functions R->S preserving +,*,0,1 (feasible for tiny rings)."""
    homs = []
    Rel, Sel = R.elements, S.elements
    for assignment in product(Sel, repeat=len(Rel)):
        f = dict(zip(Rel, assignment))
        if f[R.one] != S.one:
            continue
        if all(f[R.add(a, b)] == S.add(f[a], f[b]) and
               f[R.mul(a, b)] == S.mul(f[a], f[b]) for a in Rel for b in Rel):
            homs.append(f)
    return homs


def ba_homs(srcBA, dstBA):
    """All functions preserving meet, join, compl, bot, top between two BAs given as tuples."""
    (Cs, ms, js, ns, bs, ts) = srcBA
    (Cd, md, jd, nd, bd, td) = dstBA
    homs = []
    for assignment in product(Cd, repeat=len(Cs)):
        f = dict(zip(Cs, assignment))
        if f[bs] != bd or f[ts] != td:
            continue
        if all(f[ms(a, b)] == md(f[a], f[b]) and f[js(a, b)] == jd(f[a], f[b]) for a in Cs for b in Cs) \
           and all(f[ns(a)] == nd(f[a]) for a in Cs):
            homs.append(f)
    return homs


def E_on_hom(f, R, S):
    """E(f): idem(R) -> idem(S) is the restriction of the ring hom f (sends idempotents to idempotents)."""
    return {a: f[a] for a in idempotents(R)}


# ---------------------------------------------------------------- the report
def line(s=""):
    print(s)


def main():
    line("=" * 72)
    line("WP1+WP2  Piece A — Lawvere theories & the idempotents interpretation E")
    line("=" * 72)

    # ---- A.1: term-equivalence round-trip on a Boolean ring model (F2 x F2) ----
    line("\n[A.1] BoolAlg <-> BoolRing term-equivalence (char-2: + = -)")
    B = product_ring(Zmod(2), Zmod(2))            # F2 x F2, a 4-element Boolean ring
    # char-2 check: 1+1 = 0  => a+b-a*b == a+b+a*b
    char2 = all(B.add(x, x) == B.zero for x in B.elements)
    line(f"  model {B.name}: char-2 (x+x=0 for all x)? {char2}  ->  '+' coincides with '-'")
    ba = boolean_algebra_on_idem(B)
    line(f"  idem({B.name}) has {len(ba[0])} elements; BA axioms hold? {verify_BA_axioms(*ba)}")
    # round-trip: BR -> BA (meet=*, join=+ - *, neg=1-) -> BR (a*b=meet, a+b = (a/\¬b) \/ (¬a/\b))
    Cs, meet, join, compl, bot, top = ba
    mul_back = lambda a, b: meet(a, b)
    add_back = lambda a, b: join(meet(a, compl(b)), meet(compl(a), b))   # symmetric difference
    rt_ok = all(mul_back(a, b) == B.mul(a, b) and add_back(a, b) == B.add(a, b)
                for a in Cs for b in Cs)
    line(f"  round-trip BR->BA->BR recovers (+, *) exactly? {rt_ok}")

    # ---- A.2: E is essentially surjective (idem(B) = B for a Boolean ring) ----
    line("\n[A.2] E : Mod(CommRing) -> Mod(BoolAlg),  R |-> idem(R)")
    ess_surj = (set(idempotents(B)) == set(B.elements))
    line(f"  essentially surjective: idem(B) = B for Boolean ring B={B.name}? {ess_surj}")

    # ---- A.2: NOT essentially injective (object collapse) ----
    sizes = {}
    for n in (6, 10, 15):
        R = Zmod(n)
        idem = idempotents(R)
        bisok = verify_BA_axioms(*boolean_algebra_on_idem(R))
        sizes[n] = (len(idem), bisok, sorted(idem))
        line(f"  idem(Z/{n}) = {sorted(idem)}  (|.|={len(idem)}, is-BA={bisok})")
    collapse = len({sizes[n][0] for n in sizes}) == 1 and all(sizes[n][1] for n in sizes)
    line(f"  -> Z/6, Z/10, Z/15 all give the {sizes[6][0]}-element BA (the unique one of that size)")
    line(f"     => E NOT essentially injective (object collapse): {collapse}")
    for n in (2, 3, 5):
        line(f"  idem(Z/{n}) = {sorted(idempotents(Zmod(n)))}   (every field -> 2-element BA)")

    # ---- A.2: NOT faithful (F2[e]/(e^2)) ----
    line("\n  not faithful:")
    D = dual_numbers_F2()
    idemD = idempotents(D)
    line(f"    idem({D.name}) = {idemD}  (only {{0,1}})")
    # the two endomorphisms e|->0 and e|->e (identity), both unital ring homs
    def endo_e_to(target_e):
        # a + b*e  |->  a + b*target_e   ; on F2 elements this is a ring hom
        return {(a, b): D.add((a, 0), D.mul((b, 0), target_e)) for (a, b) in D.elements}
    f_id = endo_e_to((0, 1))     # e |-> e   (identity)
    f_0 = endo_e_to((0, 0))      # e |-> 0
    is_hom = lambda f: f[D.one] == D.one and all(
        f[D.add(x, y)] == D.add(f[x], f[y]) and f[D.mul(x, y)] == D.mul(f[x], f[y])
        for x in D.elements for y in D.elements)
    line(f"    e|->e and e|->0 are both unital ring endos? {is_hom(f_id) and is_hom(f_0)}; distinct? {f_id != f_0}")
    line(f"    E(e|->e) = {E_on_hom(f_id, D, D)},  E(e|->0) = {E_on_hom(f_0, D, D)}")
    line(f"    => E(f)=E(g) on distinct f,g  => NOT faithful: {E_on_hom(f_id, D, D) == E_on_hom(f_0, D, D)}")

    # ---- A.2: NOT full (Z/6 -> F2) ----
    line("\n  not full:")
    R6, F2 = Zmod(6), Zmod(2)
    rhoms = unital_ring_homs(R6, F2)
    baR6 = boolean_algebra_on_idem(R6)
    baF2 = boolean_algebra_on_idem(F2)
    bhoms = ba_homs(baR6, baF2)
    line(f"    unital ring homs Z/6 -> F2: {len(rhoms)}  (reduction mod 2)")
    line(f"    BA homs idem(Z/6)(4 elts) -> idem(F2)(2 elts): {len(bhoms)}")
    realized = {tuple(sorted(E_on_hom(f, R6, F2).items())) for f in rhoms}
    all_ba = {tuple(sorted(h.items())) for h in bhoms}
    unrealized = all_ba - realized
    line(f"    => more BA homs than ring homs  => NOT full: {len(bhoms) > len(rhoms)}")
    for h in unrealized:
        line(f"    unrealized BA hom (no ring-hom source): {dict(h)}")

    # ---- A.2: functoriality on named witnesses ----
    line("\n  functoriality  E(g o f) = E(g) o E(f),  E(id) = id:")
    A = Zmod(2)
    AA = product_ring(Zmod(2), Zmod(2))
    diag = {a: (a, a) for a in A.elements}                  # f: Z/2 -> Z/2 x Z/2
    proj = {(x, y): x for (x, y) in AA.elements}            # g: Z/2 x Z/2 -> Z/2
    assert diag in unital_ring_homs(A, AA) and proj in unital_ring_homs(AA, A), "witness homs not valid"
    Ef = E_on_hom(diag, A, AA)
    Eg = E_on_hom(proj, AA, A)
    comp = {a: proj[diag[a]] for a in A.elements}           # g o f  (= id on Z/2)
    Ecomp = E_on_hom(comp, A, A)
    EgEf = {a: Eg[Ef[a]] for a in idempotents(A)}
    idE = {a: a for a in idempotents(A)}
    line(f"    g o f = id_(Z/2)? {comp == {a: a for a in A.elements}}")
    line(f"    E(g o f) = E(g) o E(f)? {Ecomp == EgEf}    E(id) = id? {E_on_hom({a:a for a in A.elements}, A, A) == idE}")

    line("\n" + "=" * 72)
    line("Piece A finite witnesses checked: object-collapse, non-faithful, non-full are")
    line("PROVEN here; term-equivalence / ess-surjectivity are sanity-checked on these")
    line("models (general proofs are classical, cited in the plan/review). (WP1+WP2 core.)")
    line("=" * 72)


if __name__ == "__main__":
    main()
