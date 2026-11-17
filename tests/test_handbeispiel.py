"""Handbeispiele, von Hand nachgerechnet; die Erwartungswerte stehen als Rechnung im Test, nicht als abgeschriebene Ausgabe des Codes.

1. Handfolge n = 6 (1 3 6 2 5 4): Stapel [1], [3, 2], [6, 5, 4], LIS 3.
2. n = 5: sieben Formen, f = 1, 4, 5, 6, 5, 4, 1; 1 + 16 + 25 + 36 + 25 + 16 + 1 = 120; erste Zeile k: k = 5: 1, k = 4: 16, k = 3: 25 + 36, k = 2: 25 + 16, k = 1: 1.
   Summe der Stapelzahlen 5 + 4·16 + 3·61 + 2·41 + 1 = 335, Mittel 335/120 = 67/24, E[L²] = (25 + 16·16 + 9·61 + 4·41 + 1)/120 = 995/120.
3. Die Falle: 2√5 = 4,472 liegt 60,2 % über 67/24; n = 9: 2√9 = 6 über 4,0594.
4. Quantile n = 52 aus der Tabelle: kleinste Stapelzahl für 50/90/95/99/99,9 %: 11, 13, 14, 15, 17.
5. Modell V mit gesetzten Verweilzeiten (ausgedacht): Ränge 2 1 5 3 4, verzögert 3 Stapel, sofort 1 Stapel."""

from fractions import Fraction

import pytest

import zfl_evaluation as ev
import zfl_exact as E
import zfl_lis as L
from zfl_scenario import raenge_aus_verweilzeiten


def test_1_handfolge(hand):
    assert L.stapel_legen(hand) == [[1], [3, 2], [6, 5, 4]]
    m = ev.mischung(6, 218, L.REGEL_ERSTER)                 # Zufalls-Seed 218 mischt 1..6 zur Handfolge
    assert m.folge == hand and m.lis == 3 and m.stapelzahl == 3 and m.stapel == ((1,), (3, 2), (6, 5, 4))


def test_2_n5_formen_und_verteilung():
    f = [E.anzahl_standard_tableaux(lam) for lam in E.partitionen(5)]
    assert f == [1, 4, 5, 6, 5, 4, 1] and sum(x * x for x in f) == 120 == 1 + 16 + 25 + 36 + 25 + 16 + 1
    assert E.plancherel(5)[1:] == (1, 25 + 16, 25 + 36, 16, 1) == (1, 41, 61, 16, 1)      # k = 1: (1^5); k = 2: (2,2,1) und (2,1,1,1); k = 3: (3,2) und (3,1,1); k = 4: (4,1); k = 5: (5)
    mittel = Fraction(5 * 1 + 4 * 16 + 3 * 61 + 2 * 41 + 1 * 1, 120)
    assert mittel == Fraction(335, 120) == Fraction(67, 24)
    var = Fraction(25 * 1 + 16 * 16 + 9 * 61 + 4 * 41 + 1, 120) - mittel ** 2
    assert var == Fraction(287, 576)


def test_2_n5_kennzahlen_der_verteilung_gleich_den_bruechen():
    mittel, var, _ = E.kennzahlen(E.verteilung(5).wahrscheinlichkeit)
    assert mittel == pytest.approx(67 / 24, rel=1e-12) and var == pytest.approx(287 / 576, rel=1e-12)


def test_3_die_falle_2_wurzel_n():
    assert ev.zwei_wurzel(5) == pytest.approx(4.4721, abs=5e-5)
    assert (ev.zwei_wurzel(5) - 67 / 24) / (67 / 24) == pytest.approx(0.602, abs=5e-4)
    a9 = ev.naeherung(9)
    assert a9.exakt == pytest.approx(4.0594, abs=5e-5) and a9.zwei_wurzel == 6.0 and a9.luecke_relativ == pytest.approx(0.478, abs=5e-4)
    assert all(ev.naeherung(n).zwei_wurzel > ev.naeherung(n).exakt for n in range(1, 151))


def test_4_quantile_n52():
    p = E.verteilung(52).wahrscheinlichkeit
    assert [E.kleinstes_m(p, q) for q in (0.5, 0.9, 0.95, 0.99, 0.999)] == [11, 13, 14, 15, 17]


def test_5_modell_v_beispiel():
    rang = raenge_aus_verweilzeiten([2.5, 0.5, 4.5, 0.25, 1.0])
    assert rang == [2, 1, 5, 3, 4]                         # Abfahrten 3,5 2,5 7,5 4,25 6,0
    assert L.lis_laenge(rang) == 3 and L.ein_stapel_sortiert(rang)
