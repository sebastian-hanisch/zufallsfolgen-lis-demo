"""Kern gegen Handrechnung und unabhängige Gegenproben (DEMO-PLAYBOOK §1b und §12): Stapelregel, LIS, Plancherel-Summe, Ankunftsmodelle.

Die Gegenproben benutzen nichts aus zfl_lis: LIS per Doppelschleife (O(n²)), Stapel per eigener Schleife, Aufzählung aller Folgen."""

import math
import random
from fractions import Fraction
from itertools import permutations

import pytest

import zfl_exact as E
import zfl_lis as L
from zfl_rng import SplitMix64
from zfl_scenario import folge_aus_zufalls_seed, folge_modell_u, folge_modell_v, raenge_aus_verweilzeiten


def lis_doppelschleife(a):
    best = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best)


def test_handfolge_von_hand(hand):
    assert L.stapel_legen(hand) == [[1], [3, 2], [6, 5, 4]]
    assert L.lis_laenge(hand) == 3 == lis_doppelschleife(hand)
    assert L.lds_laenge(hand) == 3
    pos = L.lis_positionen(hand)
    werte = [hand[p] for p in pos]
    assert len(pos) == 3 and werte == sorted(werte) and pos == sorted(pos)


def test_zweite_handfolge_n5():
    assert L.stapel_legen((3, 1, 5, 2, 4)) == [[3, 1], [5, 2], [4]]
    assert L.lis_laenge((3, 1, 5, 2, 4)) == 3


def test_gegenregel_braucht_bei_der_handfolge_vier_stapel(hand):
    """Größte passende Spitze: 1 neu, 3 neu, 6 neu, 2 auf die 6 (größte Spitze unter 3 und 6), 5 neu (kein Stapel mit Spitze > 5), 4 auf die 5: [1], [3], [6, 2], [5, 4]."""
    assert L.stapel_legen(hand, L.REGEL_GROESSTE) == [[1], [3], [6, 2], [5, 4]]


def test_lis_gleich_doppelschleife_auf_300_zufallsfolgen():
    rng = random.Random(11)
    for _ in range(300):
        n = rng.randint(1, 40)
        a = rng.sample(range(1, 200), n)
        assert L.lis_laenge(a) == lis_doppelschleife(a)
        pos = L.lis_positionen(a)
        w = [a[p] for p in pos]
        assert len(pos) == L.lis_laenge(a) and w == sorted(w) and pos == sorted(pos) and len(set(w)) == len(w)


def test_erste_regel_legt_so_viele_stapel_wie_die_lis_und_jeder_stapel_faellt():
    for p in permutations(range(1, 9)):
        stapel = L.stapel_legen(p)
        assert len(stapel) == lis_doppelschleife(p)
        for s in stapel:
            assert all(s[i] > s[i + 1] for i in range(len(s) - 1))
        assert sorted(x for s in stapel for x in s) == list(range(1, 9))


def test_erste_regel_legt_so_viele_stapel_wie_die_lis_alle_362880_folgen_n9():
    assert all(len(L.stapel_legen(p)) == lis_doppelschleife(p) for p in permutations(range(1, 10)))


def test_gegenregel_legt_nie_weniger_als_die_lis_und_manchmal_mehr():
    mehr = 0
    for p in permutations(range(1, 7)):
        k = len(L.stapel_legen(p, L.REGEL_GROESSTE))
        assert k >= lis_doppelschleife(p)
        mehr += k > lis_doppelschleife(p)
    assert mehr > 0


def test_ein_stapel_sofort_gegen_mustersuche():
    def enthaelt_231(p):
        n = len(p)
        return any(p[k] < p[i] < p[j] for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))

    for n in range(1, 8):
        for p in permutations(range(1, n + 1)):
            assert L.ein_stapel_sortiert(p) == (not enthaelt_231(p))


def test_hakenformel_n5_und_summe_der_quadrate():
    formen = list(E.partitionen(5))
    assert len(formen) == 7
    assert [E.anzahl_standard_tableaux(f) for f in formen] == [1, 4, 5, 6, 5, 4, 1]
    assert sum(E.anzahl_standard_tableaux(f) ** 2 for f in formen) == 120


@pytest.mark.parametrize("n", range(1, 11))
def test_summe_der_quadrate_gleich_fakultaet(n):
    assert sum(E.anzahl_standard_tableaux(f) ** 2 for f in E.partitionen(n)) == math.factorial(n)


def test_n5_verteilung_von_hand():
    """1, 41, 61, 16, 1 Folgen mit 1 bis 5 Stapeln; Summe der Stapelzahlen 335, Mittel 67/24, Varianz 287/576."""
    c = E.plancherel(5)
    assert c == (0, 1, 41, 61, 16, 1) == E.aufzaehlung(5)
    summe = sum(k * v for k, v in enumerate(c))
    assert summe == 5 + 4 * 16 + 3 * 61 + 2 * 41 + 1 == 335
    mittel = Fraction(summe, 120)
    assert mittel == Fraction(67, 24)
    assert Fraction(sum(k * k * v for k, v in enumerate(c)), 120) - mittel ** 2 == Fraction(287, 576)


def test_n3_verteilung_von_hand():
    assert E.plancherel(3) == (0, 1, 4, 1) == E.aufzaehlung(3)


def test_verteilung_ist_normiert_und_hat_die_richtigen_quellen():
    for n, quelle in ((5, "Aufzählung und Plancherel-Summe"), (20, "Plancherel-Summe (live)"), (60, "Gessel-Rekursion, vorgerechnet")):
        v = E.verteilung(n)
        assert v.quelle == quelle
        assert math.fsum(v.wahrscheinlichkeit) + v.rest == pytest.approx(1.0, abs=1e-12)


def test_kleinstes_m_und_wahrscheinlichkeit_hoechstens_n5():
    p = E.verteilung(5).wahrscheinlichkeit
    assert E.wahrscheinlichkeit_hoechstens(p, 2) == pytest.approx(42 / 120)
    assert E.kleinstes_m(p, 0.5) == 3 and E.kleinstes_m(p, 0.9) == 4 and E.kleinstes_m(p, 0.99) == 4 and E.kleinstes_m(p, 0.995) == 5   # P(L <= 4) = 119/120


def test_mischung_ist_eine_folge_und_der_zufalls_seed_bestimmt_sie():
    a = folge_aus_zufalls_seed(30, 5)
    assert sorted(a) == list(range(1, 31)) and a == folge_aus_zufalls_seed(30, 5) and a != folge_aus_zufalls_seed(30, 6)


def test_modell_v_von_hand():
    """Gesetzte Verweilzeiten 2,5 / 0,5 / 4,5 / 0,25 / 1,0: Abfahrten 3,5 / 2,5 / 7,5 / 4,25 / 6,0, Ränge 2 1 5 3 4."""
    assert raenge_aus_verweilzeiten([2.5, 0.5, 4.5, 0.25, 1.0]) == [2, 1, 5, 3, 4]
    assert L.lis_laenge([2, 1, 5, 3, 4]) == 3 and L.ein_stapel_sortiert([2, 1, 5, 3, 4])


def test_modell_v_ist_eine_folge_und_wird_mit_kleiner_verweilzeit_fast_sortiert():
    rng = SplitMix64(3)
    a = folge_modell_v(200, 0.01, rng)
    assert sorted(a) == list(range(1, 201))
    assert a == list(range(1, 201))                      # Verweilzeit weit unter dem Ankunftsabstand: die Reihenfolge der Ankunft bleibt
    assert L.lis_laenge(folge_modell_v(200, 1000.0, SplitMix64(3))) < 60


def test_modell_u_gleichverteilung_n4_chi_quadrat():
    """48 000 Mischungen von 4 Containern: alle 24 Anordnungen kommen vor, Chi-Quadrat unter 49,7 (p = 0,001 bei 23 Freiheitsgraden)."""
    rng = SplitMix64(20261117)
    zaehler = {}
    for _ in range(48000):
        a = tuple(folge_modell_u(4, rng))
        zaehler[a] = zaehler.get(a, 0) + 1
    assert len(zaehler) == 24
    chi = sum((v - 2000) ** 2 / 2000 for v in zaehler.values())
    assert chi < 49.7
