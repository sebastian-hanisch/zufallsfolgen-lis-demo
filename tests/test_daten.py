"""Die eingefrorenen Dateien in data/: Aufbau, Stimmigkeit und teilweises Neu-Rechnen mit den Werkzeugen (tools/zfl_make_*.py, jedes mit `--check`).

Plattform (DEMO-PLAYBOOK §5, „neu gerechnet, exakt verglichen“): Ganzzahlen (Häufigkeiten, Tabelle als ganze Zahl / n!) werden exakt verglichen; die Simulationen sind mit
SplitMix64 und `exact_log` ganzzahlig bzw. bitgleich, ihre Häufigkeiten werden darum ebenfalls exakt neu gerechnet (nur der Block n = 20 im schnellen Test, der Rest langsam).
Gleitkommazahlen (F₂-Kurve, Kennzahlen aus Wahrscheinlichkeiten) als Band."""

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pytest

import zfl_constants as C
import zfl_exact as E
import zfl_lis as L
import zfl_sim as S
import zfl_tw as TW
from zfl_rng import SplitMix64
from zfl_scenario import folge_modell_v

WURZEL = Path(__file__).resolve().parent.parent


def _werkzeug(name):
    spec = importlib.util.spec_from_file_location(name, WURZEL / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_tabelle_exakt_aufbau_und_normierung():
    t = json.loads(E.DATEI.read_text(encoding="utf-8"))
    assert (t["n_max"], t["k_max"]) == (150, 50)
    assert sorted(int(n) for n in t["wahrscheinlichkeit"]) == list(range(1, 151))
    for n in range(1, 151):
        p = t["wahrscheinlichkeit"][str(n)]
        assert len(p) == 51 and p[0] == 0.0
        assert math.fsum(p) + t["rest"][str(n)] == pytest.approx(1.0, abs=1e-12), n


def test_kennzahlen_der_tabelle_gleich_den_kennzahlen_aus_den_wahrscheinlichkeiten():
    for n in (1, 2, 5, 10, 30, 52, 100, 150):
        m, v, s = E.kennzahlen_eingefroren(n)
        m2, v2, s2 = E.kennzahlen(E.verteilung(n).wahrscheinlichkeit)
        assert m == pytest.approx(m2, rel=1e-12) and v == pytest.approx(v2, rel=1e-9, abs=1e-15) and s == pytest.approx(s2, rel=1e-9, abs=1e-12), n


def test_kennzahlen_live_gleich_eingefroren_bis_n30():
    for n in range(2, 31):
        live = E.kennzahlen(E.verteilung(n).wahrscheinlichkeit)
        gefroren = E.kennzahlen_eingefroren(n)
        assert live == pytest.approx(gefroren, rel=1e-10), n


def test_sim_aufbau_zahl_der_mischungen_und_zufalls_seeds():
    d = json.loads(S.DATEI.read_text(encoding="utf-8"))
    assert sorted(int(n) for n in d["u_gross"]) == list(C.GROSSE_N)
    for n, e in d["u_gross"].items():
        assert sum(e["haeufigkeit"].values()) == e["mischungen"] and e["seed"] > 0
        assert min(int(k) for k in e["haeufigkeit"]) >= 1 and max(int(k) for k in e["haeufigkeit"]) <= int(n)
    assert sorted(int(n) for n in d["v"]) == list(C.V_N_WERTE)
    for n, e in d["v"].items():
        assert sorted(int(x) for x in e["d"]) == sorted(C.V_D_WERTE)
        for h in list(e["d"].values()) + [e["u"]]:
            assert sum(h.values()) == e["mischungen"]
    assert list(d["sofort"]["d"]) == [str(x) for x in C.SOFORT_D] + ["unendlich"]
    for e in d["sofort"]["d"].values():
        assert sum(e["haeufigkeit"].values()) == e["mischungen"] and 0 <= e["sortiert"] <= e["mischungen"]


def test_modell_u_der_simulationen_gleich_dem_exakten_mittel_innerhalb_von_vier_standardfehlern():
    for n in (20, 100):
        mes = S.modell_u_gemessen(n)
        assert abs(mes.mittel - E.mittel(n)) < 4 * mes.fehler, n
    mes = S.modell_u_gemessen(1000)
    assert 56.0 < mes.mittel < 60.0


def test_mittel_faellt_mit_wachsender_verweilzeit_gemeinsame_zufallszahlen():
    """Gleiche Zufallszahlen für alle D: das Mittel der Stapelzahl fällt mit D (jeweils innerhalb von drei Standardfehlern der größeren D-Stufe)."""
    for n in C.V_N_WERTE:
        mittel = [S.modell_v(n, d) for d in C.V_D_WERTE]
        for a, b in zip(mittel, mittel[1:]):
            assert a.mittel >= b.mittel - 3 * b.fehler, n


def test_werkzeug_ranglogik_numpy_gleich_python_und_skalierung_gleich_direkter_ziehung():
    """Die numpy-Rangfunktion des Werkzeugs gleich der Python-Rangfunktion der App, und D·e_i ist bitgleich zu `expovariate(D)`."""
    w = _werkzeug("zfl_make_sim")
    n = 60
    basis = np.arange(1, n + 1, dtype=np.float64)
    rng_e = SplitMix64(99)
    for d in (1, 5, 100):
        for _ in range(5):
            zustand = rng_e.state
            e = np.array([rng_e.expovariate(1.0) for _ in range(n)])
            direkt = folge_modell_v(n, float(d), SplitMix64(zustand))
            assert w.raenge_numpy(basis, float(d), e) == direkt


def test_sim_block_n20_neu_gerechnet_exakt_gleich():
    w = _werkzeug("zfl_make_sim")
    assert w.main(["--check", "--teil", "v20"]) == 0


@pytest.mark.slow
def test_sim_weitere_bloecke_neu_gerechnet_exakt_gleich():
    w = _werkzeug("zfl_make_sim")
    assert w.main(["--check", "--teil", "u200", "v100", "sofort"]) == 0


def test_tw_kurve_aufbau_und_monotonie():
    gitter, werte = TW._kurve()
    assert werte[0] < 1e-10 and werte[-1] > 1 - 1e-6
    assert np.all(np.diff(werte) >= -1e-12)
    assert gitter[0] == -10.0 and gitter[-1] == pytest.approx(8.0)


def test_tw_kolmogorov_abstand_an_den_ganzen_k_n10_und_n100():
    """Eigene Rechnung: 0,139 (n = 10), 0,055 (n = 100), beste Verschiebung c = −0,15 bzw. −0,09 (Gitter 0,01)."""
    assert TW.kolmogorov_abstand(E.verteilung(10).wahrscheinlichkeit, 10) == pytest.approx(0.1388, abs=5e-4)
    assert TW.kolmogorov_abstand(E.verteilung(100).wahrscheinlichkeit, 100) == pytest.approx(0.0548, abs=5e-4)
    c10, a10 = TW.beste_verschiebung(E.verteilung(10).wahrscheinlichkeit, 10)
    c100, a100 = TW.beste_verschiebung(E.verteilung(100).wahrscheinlichkeit, 100)
    assert (c10, round(a10, 3)) == (-0.15, 0.101) and (c100, round(a100, 3)) == (-0.09, 0.046)


def test_tw_kurve_neu_gerechnet():
    pytest.importorskip("scipy")
    assert _werkzeug("zfl_make_tw").main(["--check"]) == 0
