"""Claims-Tests: jede Zahl der Befunde B1 bis B13 der README mit ihren Voraussetzungen (DEMO-PLAYBOOK §11, §11a; die Tabelle „Zahl → Test“ der README nennt je Befund die Funktion).

Zähleinheiten: **Folgen** (exakte Zahlen: alle n! Folgen gleich wahrscheinlich, ohne Gleichstände) und **Zufallsfolgen** (Simulation: Zufalls-Seeds und Zahl der Mischungen in
`data/zfl_sim.json`, Werkzeug `tools/zfl_make_sim.py`). Plattform (Lehre 2026-11-15): Ganzzahlen und Brüche exakt; Gleitkommazahlen (Mittel, Streuung, Prozente) auf die genannten
Stellen gerundet verglichen; die Simulationszahlen stehen als Häufigkeiten in der Datei und werden von test_daten.py bitgleich neu gerechnet (n = 20 schnell, der Rest langsam).
Messungen, die nicht im Test stehen: Rechenzeit, Seitenlänge, Gegenprobe gegen die Tabelle der Skat-Mischungen (die Tabelle steht nicht im Repo)."""

import math
import re
from fractions import Fraction
from itertools import permutations
from pathlib import Path

import pytest

import zfl_constants as C
import zfl_evaluation as ev
import zfl_exact as E
import zfl_lis as L
import zfl_sim as S
from zfl_rng import SplitMix64
from zfl_scenario import folge_modell_u

WURZEL = Path(__file__).resolve().parent.parent


def _prozent(x, stellen=1):
    return round(100 * x, stellen)


# --- B1: die Handfolge ---------------------------------------------------------------------------------------------------------------------------------

def test_b1_handfolge_drei_stapel(hand):
    assert L.stapel_legen(hand) == [[1], [3, 2], [6, 5, 4]] and L.lis_laenge(hand) == 3
    assert len(L.stapel_legen(hand, L.REGEL_GROESSTE)) == 4          # Gegenregel: vier statt drei


# --- B2: alle Folgen n = 5 und n = 9 --------------------------------------------------------------------------------------------------------------------

def test_b2_n5_alle_120_folgen():
    assert E.plancherel(5)[1:] == (1, 41, 61, 16, 1) and math.factorial(5) == 120
    mittel, var, _ = E.kennzahlen(E.verteilung(5).wahrscheinlichkeit)
    assert Fraction(sum(k * c for k, c in enumerate(E.plancherel(5))), 120) == Fraction(67, 24)
    assert (round(mittel, 3), round(math.sqrt(var), 3)) == (2.792, 0.706)
    assert E.wahrscheinlichkeit_hoechstens(E.verteilung(5).wahrscheinlichkeit, 2) == pytest.approx(42 / 120)       # höchstens zwei Stapel: Catalan(5) = 42


def test_b2_n9_alle_362880_folgen():
    c = E.aufzaehlung(9)
    assert c[1:] == (1, 4861, 89497, 167449, 83029, 16465, 1513, 64, 1) and sum(c) == math.factorial(9) == 362880


# --- B3: drei Rechenwege ---------------------------------------------------------------------------------------------------------------------------------

def test_b3_aufzaehlung_plancherel_und_tabelle():
    for n in range(1, 9):
        assert E.aufzaehlung(n) == E.plancherel(n)
    for n in range(1, 31):
        assert tuple(c / math.factorial(n) for c in E.plancherel(n)) == E.verteilung_eingefroren(n)[: n + 1]
    assert max(E.verteilung(n).rest for n in range(51, 151)) <= 5.3e-28                  # größter Rest bei n = 150
    schranke = math.comb(150, 51) / math.factorial(51)                                    # Markow-Schranke für den abgeschnittenen Rest, n = 150
    assert E.verteilung(150).rest < schranke and round(schranke / 1e-26, 1) == 2.5
    anzahl = [1] + [0] * 100                                                              # Zahl der Partitionen von 100 (so viele Formen hätte die Plancherel-Summe bei n = 100)
    for teil in range(1, 101):
        for summe in range(teil, 101):
            anzahl[summe] += anzahl[summe - teil]
    assert anzahl[100] == 190569292 and sum(1 for _ in E.partitionen(10)) == anzahl[10] == 42


# --- B4: Mittel und Streuung -----------------------------------------------------------------------------------------------------------------------------

def test_b4_mittel_und_streuung_exakt():
    erwartet = {5: (2.792, 0.706), 10: (4.335, 0.894), 20: (6.615, 1.098), 52: (11.566, 1.407), 100: (16.738, 1.640), 150: (20.960, 1.794)}
    for n, (m, s) in erwartet.items():
        mittel, var, _ = E.kennzahlen(E.verteilung(n).wahrscheinlichkeit)
        assert (round(mittel, 3), round(math.sqrt(var), 3)) == (m, s), n


# --- B5: 2√n gegen exakt -----------------------------------------------------------------------------------------------------------------------------------

def test_b5_zwei_wurzel_n_liegt_darueber_exakt_bis_n150():
    erwartet = {5: 60.2, 10: 45.9, 20: 35.2, 52: 24.7, 100: 19.5, 150: 16.9}
    for n, p in erwartet.items():
        assert _prozent(ev.naeherung(n).luecke_relativ) == p, n
    assert all(ev.naeherung(n).luecke > 0 for n in range(1, 151))
    luecken = [ev.naeherung(n).luecke for n in range(1, 151)]
    assert all(b > a for a, b in zip(luecken, luecken[1:]))                   # die Lücke in Stapeln wächst mit n (n = 1 bis 150)
    assert (round(ev.naeherung(100).luecke, 2), round(ev.naeherung(150).luecke, 2)) == (3.26, 3.53)


def test_b5_zwei_wurzel_n_gegen_vorgerechnete_simulation_n200_bis_10000():
    zeilen = {z["n"]: z for z in ev.grosse_n_zeilen()}
    assert {n: _prozent(z["luecke_relativ"]) for n, z in zeilen.items()} == {200: 15.3, 300: 13.3, 500: 10.9, 1000: 8.6, 2000: 6.9, 5000: 5.0, 10000: 4.1}
    assert (zeilen[200]["mischungen"], zeilen[1000]["mischungen"], zeilen[10000]["mischungen"]) == (20000, 3000, 600)
    assert (round(zeilen[1000]["luecke"], 2), round(zeilen[10000]["luecke"], 2), round(zeilen[10000]["fehler"], 2)) == (5.01, 7.81, 0.17)
    assert all(z["luecke_relativ"] > 0 for z in zeilen.values())


# --- B6: die Korrektur und der Rest ----------------------------------------------------------------------------------------------------------------------

def test_b6_rest_zur_korrektur_und_nach_abzug_von_einhalb():
    rest = {5: 0.636, 20: 0.589, 52: 0.566, 100: 0.554, 150: 0.548}
    halb = {5: 0.136, 20: 0.089, 52: 0.066, 100: 0.054, 150: 0.048}
    for n in rest:
        a = ev.naeherung(n)
        assert (round(a.rest, 3), round(a.rest_halb, 3)) == (rest[n], halb[n]), n
    assert all(ev.naeherung(n).rest_halb > ev.naeherung(m).rest_halb > 0 for n, m in ((20, 30), (30, 52), (52, 100), (100, 150)))
    assert round(ev.rest_exponent(20, 150), 2) == 0.30
    assert (round(ev.naeherung(100).tw, 2), round(ev.naeherung(100).tw_halb, 2)) == (16.18, 16.68)


def test_b6_rest_aus_der_vorgerechneten_simulation_liegt_bei_0_4_bis_0_6():
    for z in ev.grosse_n_zeilen():
        assert 0.4 < z["rest"] < 0.6, z["n"]


# --- B7: verschiedene Werte beim Vorfaktor -------------------------------------------------------------------------------------------------------------------

def test_b7_vorfaktor_1_711_gegen_1_7711_bei_n52():
    q = ev.quellenvergleich(52)
    assert (round(q["faktor_ad"], 2), round(q["faktor_bdj"], 2), round(q["exakt"], 2)) == (11.12, 11.00, 11.57)
    assert (C.FAKTOR_ALDOUS_DIACONIS, C.FAKTOR_BDJ) == (1.711, 1.7711)


# --- B8: Streuung, Schiefe und Abstand zu Tracy-Widom ----------------------------------------------------------------------------------------------------

def test_b8_streuung_schiefe_und_kolmogorov_abstand():
    f = {n: ev.form(n) for n in (10, 20, 52, 100, 150)}
    assert (_prozent(f[100].streuung_anteil), _prozent(f[150].streuung_anteil)) == (84.4, 86.3)
    assert (round(f[100].schiefe, 3), round(f[150].schiefe, 3)) == (0.326, 0.315) and C.TW_SCHIEFE == 0.2241
    assert {n: round(x.abstand, 3) for n, x in f.items()} == {10: 0.139, 20: 0.108, 52: 0.068, 100: 0.055, 150: 0.047}
    assert {n: (x.beste_verschiebung, round(x.abstand_beste, 3)) for n, x in f.items()} == {10: (-0.15, 0.101), 20: (-0.13, 0.080), 52: (-0.10, 0.055), 100: (-0.09, 0.046), 150: (-0.07, 0.039)}
    assert all(f[a].abstand > f[b].abstand for a, b in ((10, 20), (20, 52), (52, 100), (100, 150)))
    assert all(x.schiefe > C.TW_SCHIEFE for x in f.values())


# --- B9: wie viele Stapel einplanen -----------------------------------------------------------------------------------------------------------------------

def test_b9_stapelzahl_fuer_sicherheit():
    erwartet = {10: [4, 5, 6, 7, 7], 20: [7, 8, 8, 9, 10], 52: [11, 13, 14, 15, 17], 100: [17, 19, 20, 21, 23]}
    for n, m in erwartet.items():
        p = E.verteilung(n).wahrscheinlichkeit
        assert [E.kleinstes_m(p, q) for q in (0.5, 0.9, 0.95, 0.99, 0.999)] == m, n


def test_b9_wenige_stapel_reichen_fast_nie():
    p10 = E.verteilung(10).wahrscheinlichkeit
    assert [_prozent(E.wahrscheinlichkeit_hoechstens(p10, m), 2 if m == 2 else 1) for m in (2, 3, 4)] == [0.46, 16.2, 60.4]
    assert E.wahrscheinlichkeit_hoechstens(p10, 2) == pytest.approx(E.catalan(10) / math.factorial(10), rel=1e-12)
    assert E.catalan(10) == 16796 and math.factorial(10) == 3628800
    assert E.wahrscheinlichkeit_hoechstens(E.verteilung(52).wahrscheinlichkeit, 4) == pytest.approx(1.38e-16, rel=5e-3)
    assert _prozent(E.wahrscheinlichkeit_hoechstens(E.verteilung(20).wahrscheinlichkeit, 4), 2) == 1.09


# --- B10: Modell V (Verweilzeit) ----------------------------------------------------------------------------------------------------------------------------

def test_b10_modell_v_n100_d10_und_container_je_stapel():
    m = S.modell_v(100, 10)
    assert (m.mischungen, round(m.mittel, 1), round(m.fehler, 2)) == (4000, 40.1, 0.04)
    assert round(E.mittel(100), 1) == 16.7
    assert round(100 / m.mittel, 1) == 2.5
    assert round(ev.verweilzeit(100, 10, 95.0).verhaeltnis, 1) == 2.4
    assert round(ev.verweilzeit(100, 100, 95.0).container_je_stapel, 1) == 4.8


def test_b10_bei_d_gleich_n_noch_20_bis_27_prozent_ueber_modell_u():
    assert [round(ev.verweilzeit(n, n, 95.0).verhaeltnis, 2) for n in (20, 100, 1000)] == [1.20, 1.24, 1.27]


def test_b10_erst_bei_d_gleich_10_n_unter_3_prozent():
    verhaeltnisse = [ev.verweilzeit(n, 10 * n, 95.0).verhaeltnis for n in (20, 100, 1000)]
    assert [round(v, 3) for v in verhaeltnisse] == [1.018, 1.023, 1.026] and all(v < 1.03 for v in verhaeltnisse)
    assert [round(ev.verweilzeit(n, 5 * n, 95.0).verhaeltnis, 2) for n in (20, 100, 1000)] == [1.04, 1.05, 1.05]      # D = 5n: noch 4 bis 5 % darüber


def test_b10_bei_d_gleich_1_liegt_l_durch_n_bei_0_81_bis_0_82():
    for n in C.V_N_WERTE:
        assert round(S.modell_v(n, 1).mittel / n, 2) in (0.81, 0.82), n
    assert round(S.modell_v(1000, 10).mittel / 1000, 2) == 0.39 and round(S.modell_v(400, 10).mittel / 400, 2) == 0.39
    assert [round(n / S.modell_v(n, 1).mittel, 2) for n in C.V_N_WERTE] == [1.22, 1.23, 1.23, 1.23]
    fehler = [S.modell_v(1000, d).fehler for d in C.V_D_WERTE]                            # n = 1000: 800 Zufallsfolgen je D
    assert S.modell_v(1000, 1).mischungen == 800 and (round(min(fehler), 2), round(max(fehler), 2)) == (0.09, 0.38)


# --- B11: sofort gegen verzögert ---------------------------------------------------------------------------------------------------------------------------

def test_b11_sofort_gegen_verzoegert_bei_n10():
    z = {x["d"]: x for x in ev.sofort_zeilen()}
    assert (_prozent(z["0.5"]["sortiert"]), round(z["0.5"]["verzoegert"], 1)) == (99.7, 9.4)
    assert (_prozent(z["unendlich"]["sortiert"], 2), round(z["unendlich"]["verzoegert"], 1)) == (0.42, 4.3)
    assert round(100 * E.catalan(10) / math.factorial(10), 2) == 0.46
    assert abs(z["unendlich"]["sortiert"] - E.catalan(10) / math.factorial(10)) < 4 * math.sqrt(0.00463 * (1 - 0.00463) / 20000)      # vier Standardfehler


# --- B12: die Gegenregel ----------------------------------------------------------------------------------------------------------------------------------

def test_b12_gegenregel_braucht_bei_n8_in_37_2_prozent_der_folgen_mehr_stapel():
    mehr = sum(len(L.stapel_legen(p, L.REGEL_GROESSTE)) > L.lis_laenge(p) for p in permutations(range(1, 9)))
    assert (mehr, round(100 * mehr / math.factorial(8), 1)) == (14993, 37.2)


# --- B13: der Zufallsgenerator --------------------------------------------------------------------------------------------------------------------------------

def test_b13_alle_24_anordnungen_bei_n4_chi_quadrat_24_5():
    rng = SplitMix64(C.DEFAULTS["seed"])
    zaehler = {}
    for _ in range(48000):
        a = tuple(folge_modell_u(4, rng))
        zaehler[a] = zaehler.get(a, 0) + 1
    chi = sum((v - 2000) ** 2 / 2000 for v in zaehler.values())
    assert len(zaehler) == 24 and round(chi, 1) == 24.5 and chi < 49.7


# --- README: genannte Tests und Testzahl -------------------------------------------------------------------------------------------------------------------

def test_readme_nennt_nur_vorhandene_tests_und_jeden_befund():
    readme = (WURZEL / "README.md").read_text(encoding="utf-8")
    quelle = (WURZEL / "tests" / "test_claims.py").read_text(encoding="utf-8")
    genannt = set(re.findall(r"`(test_b\d+[a-z0-9_]*)`", readme))
    vorhanden = set(re.findall(r"^def (test_b\d+[a-z0-9_]*)\(", quelle, flags=re.M))
    assert genannt and genannt <= vorhanden, sorted(genannt - vorhanden)
    for nr in range(1, 14):
        assert any(name.startswith(f"test_b{nr}_") for name in genannt), f"Befund B{nr} ohne Test in der README"
