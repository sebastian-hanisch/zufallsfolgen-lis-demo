"""Tracy-Widom-Verteilung F₂ (GUE), die Grenzverteilung von (L_n - 2√n) / n^(1/6) (Baik, Deift, Johansson 1999, Satz 1.1; nach Quellenbericht).

Die Kurve ist vorgerechnet (`tools/zfl_make_tw.py`: Fredholm-Determinante des Airy-Kerns) und steht in data/zfl_tw.json; die App braucht nur numpy.
Vergleichsmaß ist der Kolmogorov-Abstand **nur an den ganzen Stapelzahlen k**: max über k von |P(L ≤ k) − F₂((k + c − 2√n) / n^(1/6))| (c eine Verschiebung)."""

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

DATEI = Path(__file__).resolve().parent / "data" / "zfl_tw.json"
SHIFT_GITTER = tuple(round(-1.0 + 0.01 * i, 2) for i in range(201))     # c = -1 bis 1 in Schritten von 0,01


@lru_cache(maxsize=1)
def _daten() -> dict:
    return json.loads(DATEI.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _kurve() -> tuple[np.ndarray, np.ndarray]:
    d = _daten()
    werte = np.array(d["werte"])
    return d["start"] + d["schritt"] * np.arange(len(werte)), werte


def kennwerte_aus_kurve() -> tuple[float, float, float]:
    """Mittel, Varianz und Schiefe von F₂, aus der eingefrorenen Kurve gerechnet (eigene Rechnung, zum Vergleich mit den Konstanten der Quellen)."""
    d = _daten()
    return d["mittel"], d["varianz"], d["schiefe"]


def f2(s):
    """F₂(s) per linearer Interpolation der eingefrorenen Kurve (links vom Gitter 0, rechts 1)."""
    gitter, werte = _kurve()
    return np.interp(s, gitter, werte, left=0.0, right=1.0)


def skaliert(k, n: int, c: float = 0.0):
    """Die Stelle s = (k + c − 2√n) / n^(1/6), an der F₂ zu P(L ≤ k) verglichen wird."""
    return (np.asarray(k, dtype=float) + c - 2.0 * math.sqrt(n)) / n ** (1.0 / 6.0)


def kolmogorov_abstand(wahrscheinlichkeit, n: int, c: float = 0.0) -> float:
    """Größter Abstand |P(L ≤ k) − F₂(skaliert(k))| über die ganzen k = 0 bis k_max."""
    kum = np.cumsum(np.asarray(wahrscheinlichkeit, dtype=float))
    ks = np.arange(len(kum))
    return float(np.max(np.abs(kum - f2(skaliert(ks, n, c)))))


def beste_verschiebung(wahrscheinlichkeit, n: int) -> tuple[float, float]:
    """Verschiebung c (Gitter −1 bis 1, Schritt 0,01) mit dem kleinsten Kolmogorov-Abstand und dieser Abstand."""
    kum = np.cumsum(np.asarray(wahrscheinlichkeit, dtype=float))
    ks = np.arange(len(kum))
    abstaende = [float(np.max(np.abs(kum - f2(skaliert(ks, n, c))))) for c in SHIFT_GITTER]
    i = int(np.argmin(abstaende))
    return SHIFT_GITTER[i], abstaende[i]
