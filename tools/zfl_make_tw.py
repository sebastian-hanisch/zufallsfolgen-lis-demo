"""Werkzeug: Tracy-Widom-Verteilung F₂ (GUE) als eingefrorene Kurve `data/zfl_tw.json`.

F₂(s) ist die Fredholm-Determinante det(I - K) des Airy-Kerns auf (s, ∞). Hier numerisch mit Gauß-Legendre-Knoten (110 Knoten auf (s, 14)) und scipy (Airy-Funktion),
auf dem Gitter s = -10 bis 8 in Schritten von 0,01. Mittel, Varianz und Schiefe werden aus der Kurve gerechnet und stehen zum Vergleich mit den Konstanten der Quellen
(Baik, Deift, Johansson 1999; Bornemann, arXiv 2301.02022) in der Datei. Die App braucht nur die Datei (numpy), nicht scipy.

Aufruf (Python des Test-venv, braucht scipy):
    tools/zfl_make_tw.py             schreibt data/zfl_tw.json
    tools/zfl_make_tw.py --check     rechnet neu und vergleicht (Toleranz 1e-6 je Kurvenwert, 1e-4 bei Mittel/Varianz/Schiefe; Exit 1 bei Abweichung)"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

WURZEL = Path(__file__).resolve().parent.parent
DATEI = WURZEL / "data" / "zfl_tw.json"
START, ENDE, SCHRITT = -10.0, 8.0, 0.01
KNOTEN, OBERES_ENDE = 110, 14.0


def f2(s: float, knoten: int = KNOTEN) -> float:
    """F₂(s) als Fredholm-Determinante des Airy-Kerns (Gauß-Legendre-Quadratur)."""
    from scipy.special import airy

    x, w = np.polynomial.legendre.leggauss(knoten)
    x = s + (x + 1) * (OBERES_ENDE - s) / 2
    w = w * (OBERES_ENDE - s) / 2
    ai, aip, _, _ = airy(x)
    zaehler = np.outer(ai, aip) - np.outer(aip, ai)
    nenner = x[:, None] - x[None, :]
    np.fill_diagonal(nenner, 1.0)
    kern = zaehler / nenner
    np.fill_diagonal(kern, aip ** 2 - x * ai ** 2)
    sw = np.sqrt(w)
    return float(np.linalg.det(np.eye(knoten) - sw[:, None] * kern * sw[None, :]))


def momente(gitter: np.ndarray, werte: np.ndarray) -> tuple[float, float, float]:
    """Mittel, Varianz, Schiefe der Verteilung mit der Verteilungsfunktion `werte` auf dem Gitter (Dichte per Differenzenquotient)."""
    dichte = np.gradient(werte, gitter)
    mittel = float(np.trapezoid(gitter * dichte, gitter))
    var = float(np.trapezoid((gitter - mittel) ** 2 * dichte, gitter))
    schiefe = float(np.trapezoid((gitter - mittel) ** 3 * dichte, gitter)) / var ** 1.5
    return mittel, var, schiefe


def rechne() -> dict:
    gitter = np.arange(START, ENDE + SCHRITT / 2, SCHRITT)
    werte = np.array([f2(float(s)) for s in gitter])
    mittel, var, schiefe = momente(gitter, werte)
    return {"start": START, "schritt": SCHRITT, "werte": [round(float(v), 12) for v in werte],
            "mittel": round(mittel, 6), "varianz": round(var, 6), "schiefe": round(schiefe, 6)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    neu = rechne()
    if args.check:
        alt = json.loads(DATEI.read_text(encoding="utf-8"))
        abstand = float(np.max(np.abs(np.array(alt["werte"]) - np.array(neu["werte"]))))
        ok = len(alt["werte"]) == len(neu["werte"]) and abstand < 1e-6 and all(abs(alt[k] - neu[k]) < 1e-4 for k in ("mittel", "varianz", "schiefe"))
        print(f"zfl_tw.json: {'ok' if ok else 'ABWEICHUNG'} (größter Abstand der Kurvenwerte {abstand:.2e})")
        return 0 if ok else 1
    zeilen = ["{", f'"start": {neu["start"]}, "schritt": {neu["schritt"]},',
              f'"mittel": {neu["mittel"]}, "varianz": {neu["varianz"]}, "schiefe": {neu["schiefe"]},',
              '"quelle": "tools/zfl_make_tw.py: Fredholm-Determinante des Airy-Kerns, Gauß-Legendre 110 Knoten",',
              '"werte": [' + ",".join(str(v) for v in neu["werte"]) + "]", "}"]
    DATEI.parent.mkdir(parents=True, exist_ok=True)
    DATEI.write_text("\n".join(zeilen) + "\n", encoding="utf-8", newline="\n")
    print(f"geschrieben: {DATEI}; Mittel {neu['mittel']}, Varianz {neu['varianz']}, Schiefe {neu['schiefe']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
