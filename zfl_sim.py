"""Simulation der Stapelzahl L bei Zufallsfolgen (Zähleinheit: Zufallsfolgen) und die vorgerechneten Messungen aus data/zfl_sim.json.

Live gezogen wird nur mit dem SplitMix64 aus zfl_rng.py (ganzzahlig, auf jeder Plattform bitgleich). Größere Messreihen (große n, Modell V) sind vorgerechnet
(`tools/zfl_make_sim.py`, mit `--check`) und in der App als „vorgerechnet“ gekennzeichnet."""

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import zfl_lis as L
from zfl_rng import SplitMix64
from zfl_scenario import folge_modell_u

DATEI = Path(__file__).resolve().parent / "data" / "zfl_sim.json"


@dataclass(frozen=True)
class Messung:
    """Stapelzahlen einer Messreihe: `haeufigkeit[k]` = Zahl der Zufallsfolgen mit genau k Stapeln."""
    mischungen: int
    haeufigkeit: dict
    mittel: float
    streuung: float
    fehler: float          # Standardfehler des Mittels

    def anteil_hoechstens(self, m: int) -> float:
        return sum(c for k, c in self.haeufigkeit.items() if k <= m) / self.mischungen

    def kleinstes_m(self, q: float) -> int:
        if not 0.0 < q < 1.0:
            raise ValueError("Die Sicherheit q muss zwischen 0 und 1 liegen.")
        for m in sorted(self.haeufigkeit):
            if self.anteil_hoechstens(m) >= q:
                return m
        return max(self.haeufigkeit)


def messung_aus_haeufigkeit(haeufigkeit: dict) -> Messung:
    h = {int(k): int(c) for k, c in haeufigkeit.items()}
    t = sum(h.values())
    if t < 1:
        raise ValueError("Die Zahl der Mischungen muss mindestens 1 sein.")
    mittel = sum(k * c for k, c in h.items()) / t
    var = sum((k - mittel) ** 2 * c for k, c in h.items()) / t
    sd = math.sqrt(var)
    return Messung(t, dict(sorted(h.items())), mittel, sd, sd / math.sqrt(t))


def simuliere(n: int, mischungen: int, seed: int) -> Messung:
    """`mischungen` gleichverteilte Folgen der Länge n (ein Strom des Zufalls-Seeds, nacheinander), Häufigkeit der Stapelzahl."""
    if mischungen < 1:
        raise ValueError("Die Zahl der Mischungen muss mindestens 1 sein.")
    rng = SplitMix64(seed)
    h: dict[int, int] = {}
    for _ in range(mischungen):
        k = L.lis_laenge(folge_modell_u(n, rng))
        h[k] = h.get(k, 0) + 1
    return messung_aus_haeufigkeit(h)


@lru_cache(maxsize=1)
def _daten() -> dict:
    return json.loads(DATEI.read_text(encoding="utf-8"))


def grosse_n() -> dict[int, tuple[Messung, int]]:
    """Vorgerechnete Simulation Modell U für große n: n -> (Messung, Zufalls-Seed)."""
    return {int(n): (messung_aus_haeufigkeit(e["haeufigkeit"]), int(e["seed"])) for n, e in _daten()["u_gross"].items()}


def modell_v(n: int, d: float) -> Messung:
    """Vorgerechnete Messung Modell V: n in V_N_WERTE, D aus V_D_WERTE."""
    return messung_aus_haeufigkeit(_daten()["v"][str(n)]["d"][_d_text(d)])


def modell_u_gemessen(n: int) -> Messung:
    """Zu Modell V gehörende Messung Modell U (gleiches n, eigener Zufallsstrom, vorgerechnet)."""
    return messung_aus_haeufigkeit(_daten()["v"][str(n)]["u"])


def sofort_gegen_verzoegert() -> dict:
    """n = 10, Modell V: je D der Anteil der Folgen, die ein Stapel sofort sortiert, und die Stapelzahl beim verzögerten Einlagern (vorgerechnet)."""
    ergebnis = {}
    for d, e in _daten()["sofort"]["d"].items():
        ergebnis[d] = {"sortiert": e["sortiert"] / e["mischungen"], "mischungen": e["mischungen"], "verzoegert": messung_aus_haeufigkeit(e["haeufigkeit"])}
    return ergebnis


def d_text(d) -> str:
    return _d_text(d)


def _d_text(d) -> str:
    return str(int(d)) if float(d).is_integer() else str(d)
