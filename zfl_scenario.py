"""Ankunftsmodelle (ausgedacht, keine reale Ankunftsfolge): Modell U (alle n! Folgen gleich wahrscheinlich) und Modell V (Verweilzeit).

Modell U: Die Folge der Abholränge 1 bis n ist eine gleichverteilte Zufallsfolge (Fisher-Yates mit SplitMix64).
Modell V: Wagen i kommt zur Zeit i (Ankunftsabstand 1) und bleibt Exp(Mittel D) Zeit; die Abfahrtszeit ist i plus Verweilzeit, der Abholrang ist der Rang der
Abfahrtszeit. D steuert von fast sortiert (D klein) bis Modell U (D sehr groß). Es zählt nur die Rangfolge der Abfahrten, nicht ihre Abstände.
Gleiche Abfahrtszeiten (praktisch nicht vorkommend) werden nach der Ankunftsnummer geordnet."""

from zfl_rng import SplitMix64


def folge_modell_u(n: int, rng: SplitMix64) -> list[int]:
    """Gleichverteilte Folge der Ränge 1..n."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein.")
    a = list(range(1, n + 1))
    rng.shuffle(a)
    return a


def raenge_aus_verweilzeiten(verweilzeiten) -> list[int]:
    """Rang-Folge in Ankunftsreihenfolge: Wagen i (i = 1, 2, ...) kommt zur Zeit i, die Abfahrt ist i + Verweilzeit, der Rang ist die Platznummer der Abfahrt."""
    abfahrt = [i + 1 + d for i, d in enumerate(verweilzeiten)]
    if not abfahrt:
        raise ValueError("n muss mindestens 1 sein.")
    reihenfolge = sorted(range(len(abfahrt)), key=lambda i: (abfahrt[i], i))
    raenge = [0] * len(abfahrt)
    for platz, i in enumerate(reihenfolge, start=1):
        raenge[i] = platz
    return raenge


def folge_modell_v(n: int, mittlere_verweilzeit: float, rng: SplitMix64) -> list[int]:
    """Modell V mit Exp(Mittel D)-Verweilzeiten, D in Ankunftsabständen (D > 0)."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein.")
    if not mittlere_verweilzeit > 0:
        raise ValueError("Die mittlere Verweilzeit D muss größer als 0 sein.")
    return raenge_aus_verweilzeiten([rng.expovariate(mittlere_verweilzeit) for _ in range(n)])


def folge_aus_zufalls_seed(n: int, seed: int) -> list[int]:
    """Die Mischung (Modell U) zu einem Zufalls-Seed: gleicher Zufalls-Seed, gleiche Folge."""
    return folge_modell_u(n, SplitMix64(seed))
