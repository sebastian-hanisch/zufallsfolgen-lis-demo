"""Konstanten: Regler-Grenzen, feste Annahmen, Quellenkonstanten, Farben und Schnellstart-Szenarien (Presets)."""

import math

import zfl_lis as L

# --- Regler-Grenzen (jeder Regler gehört zu einem Experiment) ------------------------------------------------------------------------------------
N1_MIN, N1_MAX = 4, 150            # Experiment 1: eine Mischung legen (exakte Vergleichsverteilung nur bis n = 150)
N2_MIN, N2_MAX = 2, 100            # Experiment 2: exakte Verteilung gegen Simulation
T_MIN, T_MAX, T_SCHRITT = 100, 10000, 100       # Zahl der Mischungen; n * T <= 1 Million (etwa 1 Sekunde Rechenzeit)
N3_MIN, N3_MAX = 5, 150            # Experiment 3: wie gut ist 2 sqrt(n)? (größere n nur als vorgerechnete Simulation in der Tabelle)
N4_MIN, N4_MAX = 5, 150            # Experiment 4: Streuung und Form gegen Tracy-Widom
SHIFT_MIN, SHIFT_MAX, SHIFT_SCHRITT = -1.0, 1.0, 0.05
N5_MIN, N5_MAX = 10, 150           # Experiment 5: wie viele Stapel einplanen
Q_MIN, Q_MAX, Q_SCHRITT = 50.0, 99.9, 0.1       # Sicherheit in Prozent
V_N_WERTE = (20, 100, 400, 1000)   # Modell V: vorgerechnet für diese n
V_D_WERTE = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 100000)   # Verweilzeiten D in Ankunftsabständen (vorgerechnet)
GROSSE_N = (200, 300, 500, 1000, 2000, 5000, 10000)     # Modell U: vorgerechnete Simulation
SOFORT_N, SOFORT_D = 10, (0.5, 1, 2, 4, 8, 16)           # „sofort“ gegen „verzögert“ bei n = 10 (Modell V, vorgerechnet)
SEED_MAX = 999999999
LIVE_PRODUKT_MAX = 1_000_000       # n * Zahl der Mischungen, live in etwa einer Sekunde
HANDFOLGE = (1, 3, 6, 2, 5, 4)     # die Handfolge n = 6
HANDFOLGE_SEED = None              # wird unten gesetzt (Zufalls-Seed, dessen Mischung die Handfolge ist)

# --- Konstanten der Quellen ---------------------------------------------------------------------------------------------------------------------
TW_MITTEL = -1.771086807411        # Mittel der Tracy-Widom-Verteilung F2 (Baik/Deift/Johansson 1999, Bornemann 2023; eigene Fredholm-Rechnung: -1,77109)
TW_VARIANZ = 0.8131947928329       # Varianz von F2 (Quellen: 0,8132; eigene Rechnung: 0,81323)
TW_STREUUNG = math.sqrt(TW_VARIANZ)    # 0,9018
TW_SCHIEFE = 0.2241                # Schiefe von F2 (eigene Rechnung: 0,2241)
FAKTOR_ALDOUS_DIACONIS = 1.711     # Vorfaktor so bei Aldous/Diaconis 1999 (nach Quellenbericht, nicht im Original geprüft); die beiden anderen Quellen nennen 1,7711
FAKTOR_BDJ = 1.7711                # Vorfaktor bei Baik/Deift/Johansson und Bornemann (verbindlich)

COLOR_STAPEL = "#4c78a8"
COLOR_LIS = "#d9822b"
COLOR_EXAKT = "#2F6B65"
COLOR_SIM = "#d9822b"
COLOR_KURVE = "#4c78a8"
COLOR_GRAU = "rgba(150,150,150,0.55)"

# --- Schnellstart-Szenarien (Presets) ----------------------------------------------------------------------------------------------------------------
DEFAULTS = {
    "n1": 52, "seed": 20261117, "regel": L.REGEL_ERSTER,
    "n2": 52, "t": 2000,
    "n3": 52, "n4": 52, "shift": 0.0,
    "n5": 52, "q": 95.0, "nv": 100, "dv": 100,
}


def _preset(**aenderung) -> dict:
    p = dict(DEFAULTS)
    p.update(aenderung)
    return p


def _hand_seed() -> int:
    """Kleinster Zufalls-Seed, dessen Mischung von 1..6 die Handfolge 1 3 6 2 5 4 ist (Suche über die 720 möglichen Mischungen)."""
    from zfl_rng import SplitMix64

    for seed in range(1, 100000):
        a = [1, 2, 3, 4, 5, 6]
        SplitMix64(seed).shuffle(a)
        if tuple(a) == HANDFOLGE:
            return seed
    raise RuntimeError("kein Zufalls-Seed gefunden")


HANDFOLGE_SEED = _hand_seed()

PRESETS = {
    "Skat-Blatt n = 52 (Voreinstellung)": _preset(),
    "Handfolge n = 6": _preset(n1=6, seed=HANDFOLGE_SEED, n2=6),
    "Handbeispiel n = 5, alle 120": _preset(n1=5, n2=5, t=2000, n3=5, n4=5, n5=10),
    "Bucht n = 100": _preset(n1=100, n2=100, t=1000, n3=100, n4=100, n5=100, q=95.0),
    "Näherung bei n = 100": _preset(n3=100, n4=100),
    "Verweilzeit D = 10, n = 100": _preset(nv=100, dv=10),
}
PRESET_HELP = {
    "Skat-Blatt n = 52 (Voreinstellung)": "So viele Container wie ein Skat-Blatt Karten hat (n = 52, Modell, kein Betrieb): eine Mischung legen, die exakte Verteilung der Stapelzahl und die Formel 2√n daneben.",
    "Handfolge n = 6": "Die Handfolge 1 3 6 2 5 4 (ein Zufalls-Seed erzeugt sie): drei Stapel, Stapel [1], [3, 2], [6, 5, 4]. Zum Nachzählen von Hand.",
    "Handbeispiel n = 5, alle 120": "n = 5: alle 120 Folgen aufgezählt, 1, 41, 61, 16 und 1 Folgen mit 1 bis 5 Stapeln; Aufzählung und Plancherel-Summe geben dieselben Zahlen.",
    "Bucht n = 100": "100 Container in einer Bucht: die Verteilung der Stapelzahl exakt, die Simulation daneben und wie viele Stapel für 95 % der Folgen reichen.",
    "Näherung bei n = 100": "n = 100: die Formel 2√n liegt 19,5 % über dem exakten Mittel; die Korrektur mit n^(1/6) schließt die Lücke nicht ganz; die Form gegen Tracy-Widom.",
    "Verweilzeit D = 10, n = 100": "Wagen bleiben im Mittel nur 10 Ankunftsabstände (Modell mit Verweilzeit, ausgedacht): die Folge ist fast sortiert und braucht viel mehr Stapel.",
}
