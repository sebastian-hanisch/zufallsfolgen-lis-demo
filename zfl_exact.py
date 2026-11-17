"""Exakte Verteilung der Stapelzahl L (= LIS) einer Zufallsfolge: alle n! Folgen gleich wahrscheinlich (Modell U, ohne Gleichstände).

Drei Wege liefern dieselben ganzen Zahlen (Zähleinheit: Folgen):
  * Aufzählung aller n! Folgen (live bis n = 8, hier `aufzaehlung`),
  * Plancherel-Summe über alle Formen (Partitionen von n): Zahl der Folgen mit L = k ist die Summe der f² über alle Formen mit erster Zeile k,
    f nach der Hakenformel (live bis n = 30, hier `plancherel`),
  * die Gessel-Rekursion in exakten Brüchen (nur im Werkzeug tools/zfl_make_exakt.py; Ergebnis eingefroren in data/zfl_exakt.json für n = 1 bis 150).
Die eingefrorene Tabelle enthält die Wahrscheinlichkeiten P(L = k) als `ganze Zahl / n!` (Python rundet diese Division korrekt, die Zahlen sind auf jeder
Plattform dieselben Bits)."""

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations
from pathlib import Path

import zfl_lis as L

DATEI = Path(__file__).resolve().parent / "data" / "zfl_exakt.json"
LIVE_AUFZAEHLUNG_MAX = 8
LIVE_PLANCHEREL_MAX = 30


def partitionen(n: int, groesster_teil: int | None = None):
    """Alle Partitionen von n als absteigende Tupel (die Formen der Tableaux)."""
    if groesster_teil is None:
        groesster_teil = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, groesster_teil), 0, -1):
        for rest in partitionen(n - k, k):
            yield (k,) + rest


def hakenprodukt(form: tuple[int, ...]) -> int:
    """Produkt aller Hakenlängen der Form (Zeilenlängen absteigend)."""
    spaltenhoehe = [sum(1 for zeile in form if zeile > j) for j in range(form[0])]
    produkt = 1
    for i, zeile in enumerate(form):
        for j in range(zeile):
            produkt *= (zeile - j - 1) + (spaltenhoehe[j] - i - 1) + 1
    return produkt


def anzahl_standard_tableaux(form: tuple[int, ...]) -> int:
    """f_λ: Zahl der Standard-Young-Tableaux der Form λ nach der Hakenformel."""
    return math.factorial(sum(form)) // hakenprodukt(form)


@lru_cache(maxsize=None)
def plancherel(n: int) -> tuple[int, ...]:
    """Häufigkeiten c[k] (k = 0..n): Zahl der Folgen der Länge n mit genau k Stapeln, als Summe der f² über alle Formen mit erster Zeile k."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein.")
    c = [0] * (n + 1)
    for form in partitionen(n):
        f = anzahl_standard_tableaux(form)
        c[form[0]] += f * f
    return tuple(c)


@lru_cache(maxsize=None)
def aufzaehlung(n: int) -> tuple[int, ...]:
    """Häufigkeiten c[k] (k = 0..n) durch Aufzählen aller n! Folgen (nur für kleine n; ab n = 9 mehrere Sekunden)."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein.")
    c = [0] * (n + 1)
    for p in permutations(range(1, n + 1)):
        c[L.lis_laenge(p)] += 1
    return tuple(c)


@lru_cache(maxsize=1)
def _tabelle() -> dict:
    return json.loads(DATEI.read_text(encoding="utf-8"))


def exakt_n_max() -> int:
    return int(_tabelle()["n_max"])


def tabelle_k_max() -> int:
    return int(_tabelle()["k_max"])


@dataclass(frozen=True)
class Verteilung:
    n: int
    wahrscheinlichkeit: tuple[float, ...]   # Index k: P(L = k), k = 0..k_max (bei n <= 30 bis n)
    haeufigkeiten: tuple[int, ...] | None   # Index k: Zahl der Folgen mit L = k, nur wo live gerechnet (n <= 30)
    quelle: str
    rest: float                             # P(L > k_max) der eingefrorenen Tabelle (0 bei live gerechneten)


def verteilung(n: int) -> Verteilung:
    """Verteilung von L für n = 1 bis 150: bis n = 30 live aus der Plancherel-Summe, darüber aus der eingefrorenen Gessel-Tabelle."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein.")
    if n > exakt_n_max():
        raise ValueError(f"Für n > {exakt_n_max()} gibt es keine exakte Verteilung in dieser Demo (nur Simulation).")
    if n <= LIVE_PLANCHEREL_MAX:
        c = plancherel(n)
        fak = math.factorial(n)
        quelle = "Aufzählung und Plancherel-Summe" if n <= LIVE_AUFZAEHLUNG_MAX else "Plancherel-Summe (live)"
        return Verteilung(n, tuple(x / fak for x in c), c, quelle, 0.0)
    t = _tabelle()
    return Verteilung(n, tuple(t["wahrscheinlichkeit"][str(n)]), None, "Gessel-Rekursion, vorgerechnet", float(t["rest"][str(n)]))


def verteilung_eingefroren(n: int) -> tuple[float, ...]:
    """Die eingefrorene Zeile der Tabelle (für Tests: gleiche Bits wie ganze Zahl / n!)."""
    return tuple(_tabelle()["wahrscheinlichkeit"][str(n)])


def kennzahlen_eingefroren(n: int) -> tuple[float, float, float]:
    """Mittel, Varianz, Schiefe der eingefrorenen Tabelle (aus exakten Brüchen gerechnet, n = 1 bis 150)."""
    t = _tabelle()
    return float(t["mittel"][str(n)]), float(t["varianz"][str(n)]), float(t["schiefe"][str(n)])


def kennzahlen(wahrscheinlichkeit) -> tuple[float, float, float]:
    """Mittel, Varianz und Schiefe aus den Wahrscheinlichkeiten P(L = k) (Index k)."""
    p = list(wahrscheinlichkeit)
    mittel = math.fsum(k * x for k, x in enumerate(p))
    var = math.fsum((k - mittel) ** 2 * x for k, x in enumerate(p))
    schiefe = math.fsum((k - mittel) ** 3 * x for k, x in enumerate(p)) / var ** 1.5 if var > 0 else 0.0
    return mittel, var, schiefe


def mittel(n: int) -> float:
    return kennzahlen(verteilung(n).wahrscheinlichkeit)[0]


def streuung(n: int) -> float:
    return math.sqrt(kennzahlen(verteilung(n).wahrscheinlichkeit)[1])


def wahrscheinlichkeit_hoechstens(wahrscheinlichkeit, m: int) -> float:
    """P(L <= m)."""
    if m < 0:
        return 0.0
    return min(1.0, math.fsum(wahrscheinlichkeit[: m + 1]))


def kleinstes_m(wahrscheinlichkeit, q: float) -> int:
    """Kleinste Stapelzahl m mit P(L <= m) >= q (0 < q < 1)."""
    if not 0.0 < q < 1.0:
        raise ValueError("Die Sicherheit q muss zwischen 0 und 1 liegen (100 % ist mit endlich vielen Stapeln nur bei m = n erreichbar).")
    for m in range(len(wahrscheinlichkeit)):
        if wahrscheinlichkeit_hoechstens(wahrscheinlichkeit, m) >= q:
            return m
    return len(wahrscheinlichkeit) - 1


def catalan(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)
