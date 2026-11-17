"""Werkzeug: exakte Verteilung der Stapelzahl L (= LIS) für n = 1 bis 150 nach der Gessel-Formel, in exakten Brüchen, als eingefrorene Tabelle `data/zfl_exakt.json`.

Gessel (1990, nach Gedächtnis, nicht gelesen): Die Zahl u_k(n) der Folgen der Länge n mit L <= k ist (n!)² mal der Koeffizient von x^(2n) in der Determinante
D_k(x) = det[I_{|i-j|}(2x)] mit i, j = 1..k (I_j die modifizierte Besselfunktion). Die Determinante wird nicht ausmultipliziert, sondern über die Rekursion
der Verblunsky-Koeffizienten gebildet (ebenfalls nicht aus einer Quelle gelesen):
    α_0 = 1, α_1 = I_1/I_0, D_0 = 1, D_1 = I_0, R_0 = I_0,
    R_k = R_{k-1} (1 - α_k²),  D_{k+1} = D_k R_k,  α_{k+1} = (k/x) α_k / (1 - α_k²) - α_{k-1},
alles als Potenzreihen in x mit Brüchen als Koeffizienten (`fractions`). Die Rekursion gilt in diesem Repo nur, soweit die Tests sie bestätigen: ganzzahlig gleich der
Aufzählung (n <= 9) und der Plancherel-Summe (n <= 40 und n = 52); für n von 53 bis 150 gibt es keinen zweiten exakten Weg, dort stützt nur die Markow-Schranke
für den abgeschnittenen Rest.

Aufruf (Python des Test-venv, aus dem Repo-Ordner):
    tools/zfl_make_exakt.py                 schreibt data/zfl_exakt.json (n <= 150, k <= 50; rund 25 bis 60 Sekunden)
    tools/zfl_make_exakt.py --check         rechnet neu und vergleicht mit der Datei (Exit 1 bei Abweichung)
    tools/zfl_make_exakt.py --check --nmax 40 --kmax 20    Teilvergleich: nur die Einträge n <= 40, k <= 20 (wenige Sekunden)"""

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEI = WURZEL / "data" / "zfl_exakt.json"
N_MAX, K_MAX = 150, 50


class Reihen:
    """Potenzreihen in x bis Grad P als Listen von Brüchen."""

    def __init__(self, grad: int):
        self.grad = grad

    def null(self):
        return [Fraction(0)] * (self.grad + 1)

    def eins(self):
        r = self.null()
        r[0] = Fraction(1)
        return r

    def mal(self, a, b):
        r = self.null()
        b_nichtnull = [(j, x) for j, x in enumerate(b) if x]
        for i, x in enumerate(a):
            if not x:
                continue
            for j, y in b_nichtnull:
                if i + j > self.grad:
                    break
                r[i + j] += x * y
        return r

    def kehrwert(self, a):
        r = self.null()
        r[0] = 1 / a[0]
        a_nichtnull = [(i, x) for i, x in enumerate(a) if x and i > 0]
        for m in range(1, self.grad + 1):
            s = Fraction(0)
            for i, x in a_nichtnull:
                if i > m:
                    break
                s += x * r[m - i]
            r[m] = -s / a[0]
        return r

    @staticmethod
    def minus(a, b):
        return [x - y for x, y in zip(a, b)]

    @staticmethod
    def skaliert(a, c):
        return [x * c for x in a]

    def durch_x(self, a):
        assert a[0] == 0, "Division durch x braucht Konstante 0"
        return a[1:] + [Fraction(0)]

    def bessel(self, j: int):
        """I_j(2x) = Summe über m von x^(2m+j) / (m! (m+j)!)."""
        r = self.null()
        m = 0
        while 2 * m + j <= self.grad:
            r[2 * m + j] = Fraction(1, math.factorial(m) * math.factorial(m + j))
            m += 1
        return r


def gessel_u(n_max: int, k_max: int) -> dict[int, list[int]]:
    """u[k][n]: Zahl der Folgen der Länge n mit höchstens k Stapeln (k = 1..k_max, n = 0..n_max), ganze Zahlen."""
    # Jeder Schritt dividiert durch x und kostet einen Koeffizienten; darum k_max Reserve.
    R = Reihen(2 * n_max + k_max + 4)
    eins = R.eins()
    i0, i1 = R.bessel(0), R.bessel(1)
    alpha = {0: eins, 1: R.mal(i1, R.kehrwert(i0))}
    D = {0: eins, 1: i0}
    r_k = i0
    for k in range(1, k_max):
        a = alpha[k]
        q = R.minus(eins, R.mal(a, a))
        r_k = R.mal(r_k, q)
        D[k + 1] = R.mal(D[k], r_k)
        alpha[k + 1] = R.minus(R.skaliert(R.durch_x(R.mal(a, R.kehrwert(q))), k), alpha[k - 1])
    u: dict[int, list[int]] = {}
    for k in range(1, k_max + 1):
        zeile = []
        for n in range(n_max + 1):
            v = D[k][2 * n] * math.factorial(n) ** 2
            assert v.denominator == 1, (k, n, v)
            zeile.append(int(v))
        u[k] = zeile
    return u


def eintrag(u: dict[int, list[int]], n: int, k_max: int) -> dict:
    """Wahrscheinlichkeiten P(L = k) (Index k, 0..k_max) als ganze Zahl / n!, Rest P(L > k_max) und Kennzahlen aus exakten Brüchen."""
    fak = math.factorial(n)
    haeufig = [0] * (k_max + 1)
    vorher = 0
    for k in range(1, k_max + 1):
        haeufig[k] = u[k][n] - vorher
        vorher = u[k][n]
    rest_ganz = fak - vorher
    p = [c / fak for c in haeufig]
    gesamt = sum(haeufig)                      # bei n > k_max ohne den abgeschnittenen Rest (höchstens 2,5e-26 bei n = 150)
    m1 = Fraction(sum(k * c for k, c in enumerate(haeufig)), gesamt)
    m2 = Fraction(sum(k * k * c for k, c in enumerate(haeufig)), gesamt)
    var = m2 - m1 * m1
    m3 = Fraction(sum((k - m1) ** 3 * c for k, c in enumerate(haeufig)), gesamt)
    return {"p": p, "rest": rest_ganz / fak, "mittel": float(m1), "varianz": float(var), "schiefe": float(m3) / float(var) ** 1.5 if var > 0 else 0.0}


def rechne(n_max: int, k_max: int) -> dict:
    u = gessel_u(n_max, k_max)
    return {n: eintrag(u, n, k_max) for n in range(1, n_max + 1)}


def schreibe(daten: dict, n_max: int, k_max: int) -> None:
    zeilen = ["{", f'"n_max": {n_max}, "k_max": {k_max},',
              '"quelle": "tools/zfl_make_exakt.py: Gessel-Rekursion in Brüchen; P(L = k) als ganze Zahl / n! (Index k = 0..k_max), rest = P(L > k_max), mittel/varianz/schiefe aus exakten Brüchen",']
    for name, schluessel in (("wahrscheinlichkeit", "p"), ("rest", "rest"), ("mittel", "mittel"), ("varianz", "varianz"), ("schiefe", "schiefe")):
        zeilen.append(f'"{name}": {{')
        eintraege = [f'"{n}": {json.dumps(daten[n][schluessel])}' for n in range(1, n_max + 1)]
        zeilen.append(",\n".join(eintraege))
        zeilen.append("}" + ("," if name != "schiefe" else ""))
    zeilen.append("}")
    DATEI.parent.mkdir(parents=True, exist_ok=True)
    DATEI.write_text("\n".join(zeilen) + "\n", encoding="utf-8", newline="\n")


def vergleiche(neu: dict, n_max: int, k_max: int) -> list[str]:
    alt = json.loads(DATEI.read_text(encoding="utf-8"))
    fehler = []
    for n in range(1, n_max + 1):
        zeile_alt = alt["wahrscheinlichkeit"][str(n)]
        zeile_neu = neu[n]["p"]
        if zeile_alt[: k_max + 1] != zeile_neu[: k_max + 1]:
            fehler.append(f"n = {n}: Wahrscheinlichkeiten weichen ab")
        if k_max == alt["k_max"]:
            for name, schluessel in (("rest", "rest"), ("mittel", "mittel"), ("varianz", "varianz"), ("schiefe", "schiefe")):
                if alt[name][str(n)] != neu[n][schluessel]:
                    fehler.append(f"n = {n}: {name} weicht ab")
    return fehler


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="neu rechnen und mit der Datei vergleichen, nichts schreiben")
    ap.add_argument("--nmax", type=int, default=N_MAX)
    ap.add_argument("--kmax", type=int, default=K_MAX)
    args = ap.parse_args(argv)
    daten = rechne(args.nmax, args.kmax)
    if args.check:
        fehler = vergleiche(daten, args.nmax, args.kmax)
        print(f"zfl_exakt.json: {'ABWEICHUNG' if fehler else 'ok'} (n <= {args.nmax}, k <= {args.kmax})")
        for f in fehler[:20]:
            print("  ", f)
        return 1 if fehler else 0
    if (args.nmax, args.kmax) != (N_MAX, K_MAX):
        print("Schreiben nur mit den Standardgrenzen (n <= 150, k <= 50).")
        return 2
    schreibe(daten, args.nmax, args.kmax)
    print(f"geschrieben: {DATEI}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
