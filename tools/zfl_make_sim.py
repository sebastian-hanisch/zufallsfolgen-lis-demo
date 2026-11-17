"""Werkzeug: vorgerechnete Simulationen für `data/zfl_sim.json` (Zähleinheit: Zufallsfolgen; Zufallsquelle: SplitMix64 aus zfl_rng.py, auf jeder Plattform bitgleich).

Drei Blöcke:
  u_gross   Modell U (gleichverteilt) für große n (200 bis 10 000): Häufigkeit der Stapelzahl, Zahl der Mischungen und Zufalls-Seed je n.
  v         Modell V (Verweilzeit D, ausgedacht) für n = 20, 100, 400, 1000 und 14 Verweilzeiten D von 1 bis 100 000 Ankunftsabständen, dazu Modell U gemessen.
            Für jede Folge werden die Exp(1)-Zahlen e_i einmal gezogen und für alle D mit D·e_i skaliert (gleiche Zufallszahlen für alle D), das gibt glatte Kurven.
            D·e_i ist bitgleich zur direkten Ziehung `expovariate(D)` (die Vorzeichen heben sich auf).
  sofort    n = 10, Modell V mit D = 0,5 bis 16 und Modell U: Anteil der Folgen, die ein Stapel „sofort“ sortiert, und Stapelzahl beim verzögerten Einlagern.

Aufruf (Python des Test-venv, aus dem Repo-Ordner; Gesamtlaufzeit einige Minuten):
    tools/zfl_make_sim.py                    schreibt data/zfl_sim.json
    tools/zfl_make_sim.py --check            rechnet alles neu und vergleicht mit der Datei (Exit 1 bei Abweichung)
    tools/zfl_make_sim.py --check --teil v20   nur einen Block: u<n>, v<n> oder sofort (mehrere durch Leerzeichen)"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

import zfl_constants as C  # noqa: E402
import zfl_lis as L  # noqa: E402
from zfl_rng import SplitMix64  # noqa: E402
from zfl_scenario import folge_modell_u  # noqa: E402

DATEI = WURZEL / "data" / "zfl_sim.json"

# n -> (Zahl der Mischungen, Zufalls-Seed)
U_GROSS = {200: (20000, 90200), 300: (10000, 90300), 500: (6000, 90500), 1000: (3000, 91000), 2000: (2000, 92000), 5000: (1000, 95000), 10000: (600, 99000)}
V_PLAN = {20: (6000, 72020), 100: (4000, 72100), 400: (2000, 72400), 1000: (800, 73000)}     # n -> (Mischungen, Zufalls-Seed der e_i)
U_REF = {20: 82020, 100: 82100, 400: 82400, 1000: 83000}                                         # Zufalls-Seed der Modell-U-Referenz je n (gleiche Mischungszahl wie V)
SOFORT = {"n": C.SOFORT_N, "mischungen": 20000, "seed": 61010, "seed_u": 61011}


def _hist(werte) -> dict:
    h: dict[int, int] = {}
    for k in werte:
        h[int(k)] = h.get(int(k), 0) + 1
    return {str(k): h[k] for k in sorted(h)}


def raenge_numpy(basis: np.ndarray, d: float, e: np.ndarray) -> list[int]:
    """Rang-Folge zu den Abfahrtszeiten basis + d*e (stabile Sortierung: gleiche Zeiten nach Ankunftsnummer, wie zfl_scenario.raenge_aus_verweilzeiten)."""
    reihenfolge = np.argsort(basis + d * e, kind="stable")
    raenge = np.empty(len(e), dtype=np.int64)
    raenge[reihenfolge] = np.arange(1, len(e) + 1)
    return raenge.tolist()


def block_u(n: int) -> dict:
    t, seed = U_GROSS[n]
    rng = SplitMix64(seed)
    return {"mischungen": t, "seed": seed, "haeufigkeit": _hist(L.lis_laenge(folge_modell_u(n, rng)) for _ in range(t))}


def block_v(n: int) -> dict:
    t, seed = V_PLAN[n]
    rng = SplitMix64(seed)
    basis = np.arange(1, n + 1, dtype=np.float64)
    ergebnisse = {C_d: [] for C_d in C.V_D_WERTE}
    for _ in range(t):
        e = np.array([rng.expovariate(1.0) for _ in range(n)])
        for d in C.V_D_WERTE:
            ergebnisse[d].append(L.lis_laenge(raenge_numpy(basis, float(d), e)))
    rng_u = SplitMix64(U_REF[n])
    u = [L.lis_laenge(folge_modell_u(n, rng_u)) for _ in range(t)]
    return {"mischungen": t, "seed": seed, "seed_u": U_REF[n], "u": _hist(u), "d": {str(d): _hist(v) for d, v in ergebnisse.items()}}


def block_sofort() -> dict:
    n, t = SOFORT["n"], SOFORT["mischungen"]
    rng = SplitMix64(SOFORT["seed"])
    basis = np.arange(1, n + 1, dtype=np.float64)
    ergebnis = {}
    folgen = []
    for _ in range(t):
        folgen.append(np.array([rng.expovariate(1.0) for _ in range(n)]))
    for d in C.SOFORT_D:
        ls, sortiert = [], 0
        for e in folgen:
            f = raenge_numpy(basis, float(d), e)
            ls.append(L.lis_laenge(f))
            sortiert += L.ein_stapel_sortiert(f)
        ergebnis[str(d)] = {"mischungen": t, "sortiert": sortiert, "haeufigkeit": _hist(ls)}
    rng_u = SplitMix64(SOFORT["seed_u"])
    ls, sortiert = [], 0
    for _ in range(t):
        f = folge_modell_u(n, rng_u)
        ls.append(L.lis_laenge(f))
        sortiert += L.ein_stapel_sortiert(f)
    ergebnis["unendlich"] = {"mischungen": t, "sortiert": sortiert, "haeufigkeit": _hist(ls)}
    return {"n": n, "seed": SOFORT["seed"], "seed_u": SOFORT["seed_u"], "d": ergebnis}


def alle_namen() -> list[str]:
    return [f"u{n}" for n in U_GROSS] + [f"v{n}" for n in V_PLAN] + ["sofort"]


def rechne_block(name: str):
    if name == "sofort":
        return block_sofort()
    if name.startswith("u"):
        return block_u(int(name[1:]))
    if name.startswith("v"):
        return block_v(int(name[1:]))
    raise SystemExit(f"unbekannter Block: {name}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--teil", nargs="*", help="nur diese Blöcke (u<n>, v<n>, sofort); nur mit --check")
    args = ap.parse_args(argv)
    namen = args.teil if args.teil else alle_namen()
    neu = {name: rechne_block(name) for name in namen}
    if args.check:
        alt = json.loads(DATEI.read_text(encoding="utf-8"))
        fehler = []
        for name, wert in neu.items():
            wert = json.loads(json.dumps(wert))
            gespeichert = alt["sofort"] if name == "sofort" else alt["u_gross"][name[1:]] if name.startswith("u") else alt["v"][name[1:]]
            if gespeichert != wert:
                fehler.append(name)
        print(f"zfl_sim.json: {'ABWEICHUNG in ' + ', '.join(fehler) if fehler else 'ok'} ({', '.join(namen)})")
        return 1 if fehler else 0
    if args.teil:
        print("Schreiben nur ohne --teil.")
        return 2
    daten = {"quelle": "tools/zfl_make_sim.py: SplitMix64 (zfl_rng.py); Zähleinheit Zufallsfolgen; Modell V ausgedacht",
             "u_gross": {name[1:]: neu[name] for name in neu if name.startswith("u")},
             "v": {name[1:]: neu[name] for name in neu if name.startswith("v")},
             "sofort": neu["sofort"]}
    zeilen = ["{", f'"quelle": {json.dumps(daten["quelle"], ensure_ascii=False)},']
    for schluessel in ("u_gross", "v"):
        zeilen.append(f'"{schluessel}": {{')
        zeilen.append(",\n".join(f'"{n}": {json.dumps(e)}' for n, e in daten[schluessel].items()))
        zeilen.append("},")
    zeilen.append(f'"sofort": {json.dumps(daten["sofort"])}')
    zeilen.append("}")
    DATEI.parent.mkdir(parents=True, exist_ok=True)
    DATEI.write_text("\n".join(zeilen) + "\n", encoding="utf-8", newline="\n")
    print(f"geschrieben: {DATEI}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
