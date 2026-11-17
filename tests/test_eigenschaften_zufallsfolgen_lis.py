"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): Aussagen, die für die Stapelzahl gelten müssen, ohne dass man das Ergebnis kennt. Je Eigenschaft 20 bis 50 Zufallsinstanzen
mit festem Zufalls-Seed, plus Randfälle."""

import math
import random
from itertools import permutations

import pytest

import zfl_constants as C
import zfl_exact as E
import zfl_lis as L
import zfl_sim as S
from zfl_rng import SplitMix64
from zfl_scenario import folge_aus_zufalls_seed, folge_modell_v, raenge_aus_verweilzeiten


def _folgen(anzahl=40, n_max=40, seed=2026):
    rng = random.Random(seed)
    return [rng.sample(range(1, n_max + 1), rng.randint(1, n_max)) for _ in range(anzahl)]


def _standardisiert(a):
    rang = {x: i + 1 for i, x in enumerate(sorted(a))}
    return [rang[x] for x in a]


def test_lis_der_inversen_permutation_ist_gleich():
    rng = random.Random(1)
    for _ in range(40):
        n = rng.randint(1, 40)
        p = rng.sample(range(1, n + 1), n)
        inv = [0] * n
        for i, x in enumerate(p):
            inv[x - 1] = i + 1
        assert L.lis_laenge(p) == L.lis_laenge(inv)


def test_lis_der_umkehrfolge_ist_die_lds_und_beide_haben_dieselbe_verteilung():
    for p in _folgen():
        assert L.lis_laenge(p[::-1]) == L.lds_laenge(p)
    for n in range(1, 7):
        lis = sorted(L.lis_laenge(p) for p in permutations(range(1, n + 1)))
        lds = sorted(L.lds_laenge(p) for p in permutations(range(1, n + 1)))
        assert lis == lds


def test_weglassen_des_letzten_elements_aendert_die_stapelzahl_um_null_oder_eins():
    for p in _folgen(50):
        if len(p) < 2:
            continue
        k_ganz = L.lis_laenge(p)
        k_kurz = L.lis_laenge(_standardisiert(p[:-1]))
        assert k_ganz - k_kurz in (0, 1)


def test_mittel_waechst_mit_n_um_hoechstens_eins_je_schritt():
    for n in range(1, E.exakt_n_max()):
        d = E.kennzahlen_eingefroren(n + 1)[0] - E.kennzahlen_eingefroren(n)[0]
        assert 0 < d <= 1, n


def test_u_k_n_durch_n_fakultaet_waechst_in_k_und_faellt_in_n():
    """P(L_n <= k) wächst in k und fällt in n (mehr Container, mehr Stapel nötig); für n bis 150 und k bis 50 aus der Tabelle."""
    kum = {n: [0.0] * 51 for n in range(1, 151)}
    for n in range(1, 151):
        laufend = 0.0
        for k, x in enumerate(E.verteilung_eingefroren(n)):
            laufend += x
            kum[n][k] = laufend
    for n in range(1, 151):
        assert all(kum[n][k + 1] >= kum[n][k] - 1e-15 for k in range(50)), n
    for k in range(1, 51):
        assert all(kum[n + 1][k] <= kum[n][k] + 1e-12 for n in range(1, 150)), k


def test_wahrscheinlichkeiten_summieren_sich_zu_eins():
    for n in (1, 2, 7, 25, 30, 31, 80, 150):
        v = E.verteilung(n)
        assert math.fsum(v.wahrscheinlichkeit) + v.rest == pytest.approx(1.0, abs=1e-12)


def test_hoechstens_zwei_stapel_sind_die_catalan_zahl_durch_n_fakultaet():
    for n in range(1, 31):
        p = E.verteilung(n).wahrscheinlichkeit
        assert E.wahrscheinlichkeit_hoechstens(p, 2) == pytest.approx(E.catalan(n) / math.factorial(n), rel=1e-12), n


def test_gleicher_zufalls_seed_gleiche_folge_und_andere_gleiche_verteilung():
    for seed in range(1, 21):
        assert folge_aus_zufalls_seed(25, seed) == folge_aus_zufalls_seed(25, seed)
    assert len({tuple(folge_aus_zufalls_seed(12, s)) for s in range(1, 21)}) > 15


def test_modell_v_gibt_eine_permutation_der_raenge_1_bis_n():
    rng = SplitMix64(31)
    for _ in range(30):
        n = rng.below(60) + 1
        d = [0.3, 1.0, 5.0, 40.0][rng.below(4)]
        assert sorted(folge_modell_v(n, d, rng)) == list(range(1, n + 1))


def test_verschieben_aller_ankunftszeiten_aendert_die_rangfolge_nicht():
    """Die Ankunftszeit i wird um eine Konstante verschoben (hier über die Verweilzeiten ausgedrückt: gleiche Abfahrtsreihenfolge bei i + c)."""
    rng = SplitMix64(5)
    for _ in range(30):
        n = rng.below(40) + 2
        verweil = [rng.expovariate(3.0) for _ in range(n)]
        r1 = raenge_aus_verweilzeiten(verweil)
        abfahrt = [i + 1 + d for i, d in enumerate(verweil)]
        r2 = _raenge([a + 1000.0 for a in abfahrt])
        assert r1 == r2


def _raenge(zeiten):
    reihenfolge = sorted(range(len(zeiten)), key=lambda i: (zeiten[i], i))
    r = [0] * len(zeiten)
    for platz, i in enumerate(reihenfolge, start=1):
        r[i] = platz
    return r


def test_modell_v_naehert_sich_modell_u_mit_wachsendem_d():
    """Das Mittel der Stapelzahl fällt mit D und liegt bei D = 100 000 innerhalb von vier Standardfehlern des Modells U (n = 20 und n = 100, vorgerechnet)."""
    for n in (20, 100):
        mittel = [S.modell_v(n, d).mittel for d in C.V_D_WERTE]
        assert mittel[0] > mittel[len(mittel) // 2] > mittel[-1]
        mes = S.modell_v(n, 100000)
        ref = E.mittel(n)
        assert abs(mes.mittel - ref) < 4 * mes.fehler


def test_stapelzahl_haengt_nicht_an_den_werten_nur_an_der_reihenfolge():
    """Streng monotone Umrechnung der Ränge (z. B. Quadrieren) ändert weder die Stapelzahl noch die Zahl der Stapel der ersten Regel."""
    for p in _folgen(30, 30):
        q = [x * x + 3 for x in p]
        assert L.lis_laenge(q) == L.lis_laenge(p) and len(L.stapel_legen(q)) == len(L.stapel_legen(p))


def test_simulation_gleicher_zufalls_seed_gleiche_haeufigkeit():
    a = S.simuliere(15, 300, 77)
    b = S.simuliere(15, 300, 77)
    assert a.haeufigkeit == b.haeufigkeit
    assert S.simuliere(15, 300, 78).haeufigkeit != a.haeufigkeit
