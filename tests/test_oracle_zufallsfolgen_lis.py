"""Orakel-Tests (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §5 und §6): die Kernrechnungen gegen andere Rechenwege.

(a) Verteilung der Stapelzahl: Aufzählung aller n! Folgen mit **eigener** Doppelschleife (nicht zfl_lis) gegen die Plancherel-Summe (live) gegen die eingefrorene Gessel-Tabelle
    (ganze Zahl / n!, bitgleich) und gegen die Gessel-Rekursion des Werkzeugs, neu gerechnet (n bis 40, k bis 20). n = 9 mit eingeschlossen.
(b) Stapelregel gegen die Aufzählung aller Mengenpartitionen (n bis 6, n = 7 an einer Stichprobe): Mindestzahl fallender Teilfolgen, die alle Positionen überdecken, ist die LIS.
(c) Simulation (SplitMix64) gegen das exakte Mittel und die exakte Streuung: Zufalls-Seeds fest, vier Standardfehler.
(d) Tracy-Widom: eigene Fredholm-Rechnung (scipy) gegen die eingefrorene Kurve und gegen die Konstanten der Quellen.
(e) Markow-Schranke für den abgeschnittenen Rest der Tabelle.
Die Gegenprobe gegen die Tabelle der Skat-Mischungen von Aldous/Diaconis steht nicht im Repo (Weitergabe-Vermerk der Quelle)."""

import importlib.util
import math
import random
from itertools import permutations
from pathlib import Path

import pytest

import zfl_constants as C
import zfl_exact as E
import zfl_lis as L
import zfl_sim as S
import zfl_tw as TW
from zfl_rng import SplitMix64
from zfl_scenario import folge_modell_u

WURZEL = Path(__file__).resolve().parent.parent


def _werkzeug(name):
    spec = importlib.util.spec_from_file_location(name, WURZEL / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lis_dp(a):
    best = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best)


def aufzaehlung_dp(n):
    c = [0] * (n + 1)
    for p in permutations(range(1, n + 1)):
        c[lis_dp(p)] += 1
    return tuple(c)


# --- (a) drei Wege für die Verteilung ------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("n", range(1, 9))
def test_aufzaehlung_plancherel_und_tabelle_geben_dieselben_ganzen_zahlen(n):
    c = aufzaehlung_dp(n)
    assert c == E.plancherel(n) == E.aufzaehlung(n)
    fak = math.factorial(n)
    assert tuple(x / fak for x in c) == E.verteilung_eingefroren(n)[: n + 1]    # ganze Zahl / n!: bitgleich auf jeder Plattform


def test_n9_aufzaehlung_gegen_plancherel_und_tabelle():
    c = aufzaehlung_dp(9)
    assert c[1:] == (1, 4861, 89497, 167449, 83029, 16465, 1513, 64, 1)
    assert c == E.plancherel(9)
    assert tuple(x / math.factorial(9) for x in c) == E.verteilung_eingefroren(9)[:10]


def test_plancherel_live_gleich_eingefrorener_tabelle_bis_n30():
    for n in range(1, E.LIVE_PLANCHEREL_MAX + 1):
        fak = math.factorial(n)
        live = tuple(x / fak for x in E.plancherel(n))
        assert live == E.verteilung_eingefroren(n)[: n + 1], n
        assert all(x == 0.0 for x in E.verteilung_eingefroren(n)[n + 1:]), n


def test_gessel_rekursion_neu_gerechnet_gleich_plancherel_und_tabelle():
    """Gessel-Rekursion in Brüchen (Werkzeug) für n <= 40 und k <= 20: ganzzahlig gleich der Plancherel-Summe (n <= 30) und gleich der eingefrorenen Tabelle (n <= 40)."""
    g = _werkzeug("zfl_make_exakt")
    u = g.gessel_u(40, 20)
    for n in range(1, 31):
        c = E.plancherel(n)
        summe = 0
        for k in range(1, 21):
            summe += c[k] if k <= n else 0
            assert u[k][n] == summe, (n, k)
    for n in range(1, 41):
        fak = math.factorial(n)
        zeile = [0.0] + [(u[k][n] - (u[k - 1][n] if k > 1 else 0)) / fak for k in range(1, 21)]
        assert tuple(zeile) == E.verteilung_eingefroren(n)[:21], n


def test_gessel_spezialfaelle_k1_k2_k3():
    """u_1 = 1, u_2(n) = Catalan(n), u_3 = 1, 1, 2, 6, 23, 103, 513, 2761, 15767 (n = 0 bis 8)."""
    g = _werkzeug("zfl_make_exakt")
    u = g.gessel_u(8, 3)
    assert u[1] == [1] * 9
    assert u[2] == [math.comb(2 * n, n) // (n + 1) for n in range(9)]
    assert u[3] == [1, 1, 2, 6, 23, 103, 513, 2761, 15767]


@pytest.mark.slow
def test_gessel_tabelle_vollstaendig_neu_gerechnet():
    g = _werkzeug("zfl_make_exakt")
    assert g.main(["--check"]) == 0


def test_markow_schranke_fuer_den_abgeschnittenen_rest():
    """P(L >= k) <= C(n, k) / k! (Erwartungswert der Zahl wachsender Teilfolgen der Länge k): die Reste der Tabelle (k > 50) liegen darunter."""
    kmax = E.tabelle_k_max()
    for n in range(51, E.exakt_n_max() + 1):
        schranke = math.comb(n, kmax + 1) / math.factorial(kmax + 1)
        assert E.verteilung(n).rest <= schranke, n
    for n in range(2, 9):
        c = E.aufzaehlung(n)
        for k in range(1, n + 1):
            assert sum(c[k:]) / math.factorial(n) <= math.comb(n, k) / math.factorial(k) + 1e-15


# --- (b) Stapelregel gegen alle Mengenpartitionen -------------------------------------------------------------------------------------------------------

def mengenpartitionen(n):
    """Alle Zerlegungen der Positionen 0..n-1 in Blöcke (Restricted-Growth-Strings)."""
    def rek(i, bloecke):
        if i == n:
            yield [list(b) for b in bloecke]
            return
        for b in bloecke:
            b.append(i)
            yield from rek(i + 1, bloecke)
            b.pop()
        bloecke.append([i])
        yield from rek(i + 1, bloecke)
        bloecke.pop()
    yield from rek(0, [])


def mindestzahl_fallender_bloecke(p):
    best = len(p)
    for zerlegung in mengenpartitionen(len(p)):
        if len(zerlegung) < best and all(all(p[b[i]] > p[b[i + 1]] for i in range(len(b) - 1)) for b in zerlegung):
            best = len(zerlegung)
    return best


def test_stapelzahl_gleich_mindestzahl_aller_zerlegungen_n_bis_6():
    for n in range(1, 7):
        for p in permutations(range(1, n + 1)):
            assert len(L.stapel_legen(p)) == L.lis_laenge(p) == mindestzahl_fallender_bloecke(p), p


def test_stapelzahl_gleich_mindestzahl_aller_zerlegungen_n7_stichprobe():
    rng = random.Random(4)
    for _ in range(40):
        p = rng.sample(range(1, 8), 7)
        assert len(L.stapel_legen(p)) == L.lis_laenge(p) == mindestzahl_fallender_bloecke(p), p


# --- (c) Simulation gegen das exakte Mittel und die exakte Streuung --------------------------------------------------------------------------------------

@pytest.mark.parametrize("n,t,seed", [(20, 4000, 1820), (52, 3000, 1852), (100, 1500, 1900)])
def test_simulation_innerhalb_von_vier_standardfehlern_des_exakten_mittels(n, t, seed):
    mes = S.simuliere(n, t, seed)
    mittel, var, _ = E.kennzahlen(E.verteilung(n).wahrscheinlichkeit)
    assert abs(mes.mittel - mittel) < 4 * mes.fehler, (n, mes.mittel, mittel, mes.fehler)
    assert abs(mes.streuung - math.sqrt(var)) < 0.15 * math.sqrt(var), (n, mes.streuung)


def test_simulation_verteilung_gegen_exakte_wahrscheinlichkeiten_n52():
    """Je Stapelzahl k liegt der simulierte Anteil innerhalb von vier Standardfehlern des exakten Anteils (Zufallsfolgen gegen Folgen)."""
    n, t = 52, 4000
    mes = S.simuliere(n, t, 5252)
    p = E.verteilung(n).wahrscheinlichkeit
    for k in range(len(p)):
        erwartet = p[k]
        beobachtet = mes.haeufigkeit.get(k, 0) / t
        se = math.sqrt(max(erwartet * (1 - erwartet), 1e-12) / t)
        assert abs(beobachtet - erwartet) <= 4 * se + 1.0 / t, (k, beobachtet, erwartet)


# --- (d) Tracy-Widom -------------------------------------------------------------------------------------------------------------------------------------

def test_tracy_widom_eigene_fredholm_rechnung_gegen_die_eingefrorene_kurve():
    pytest.importorskip("scipy")
    w = _werkzeug("zfl_make_tw")
    for s in (-5.0, -3.0, -1.5, 0.0, 1.0, 2.5):
        assert float(TW.f2(s)) == pytest.approx(w.f2(s), abs=1e-6), s


def test_tracy_widom_konstanten_der_quellen_auf_drei_stellen_nachgerechnet():
    pytest.importorskip("scipy")
    import numpy as np

    w = _werkzeug("zfl_make_tw")
    gitter = np.arange(-9.0, 7.0 + 1e-9, 0.04)
    werte = np.array([w.f2(float(s)) for s in gitter])
    mittel, var, _ = w.momente(gitter, werte)
    assert mittel == pytest.approx(C.TW_MITTEL, abs=2e-3)
    assert var == pytest.approx(C.TW_VARIANZ, abs=2e-3)
    m0, v0, s0 = TW.kennwerte_aus_kurve()
    assert (m0, v0, s0) == pytest.approx((C.TW_MITTEL, C.TW_VARIANZ, C.TW_SCHIEFE), abs=2e-3)
    assert C.TW_STREUUNG == pytest.approx(0.9018, abs=5e-5)
