"""Kennzahlen und Verdikte der fünf Experimente. Jedes Verdikt ist eine reine Funktion `verdict_*(...) -> (Art, Text)`; die App ruft `getattr(st, Art)(Text)`.

Zähleinheiten: **Folgen** (exakte Zahlen, alle n! Folgen gleich wahrscheinlich, ohne Gleichstände, unbegrenzte Stapelhöhe) und **Zufallsfolgen** (Simulation).
Alle Folgen sind ausgedacht (Modell U gleichverteilt, Modell V mit gesetzter Verweilzeit); es gibt keine reale Ankunftsfolge."""

import math
from dataclasses import dataclass

import zfl_constants as C
import zfl_exact as E
import zfl_lis as L
import zfl_sim as S
import zfl_tw as TW
from zfl_scenario import folge_aus_zufalls_seed


# --- Zahlenformat (deutsch) ----------------------------------------------------------------------------------------------------------------------

def de(x: float, stellen: int = 2) -> str:
    """Zahl mit Dezimalkomma; negative Zahlen mit Minuszeichen."""
    return f"{x:.{stellen}f}".replace(".", ",").replace("-", "−")


def de_vz(x: float, stellen: int = 2) -> str:
    """Zahl mit Vorzeichen (+ oder −) und Dezimalkomma."""
    return ("+" if x >= 0 else "−") + de(abs(x), stellen)


def prozent(anteil: float, stellen: int = 1) -> str:
    """Anteil (0 bis 1) als Prozentzahl mit Dezimalkomma."""
    return de(100.0 * anteil, stellen) + " %"


def prozent_vz(anteil: float, stellen: int = 1) -> str:
    return de_vz(100.0 * anteil, stellen) + " %"


def ganz(x: int) -> str:
    """Ganze Zahl mit geschütztem Leerzeichen als Tausendertrenner."""
    return f"{x:,}".replace(",", " ")


@dataclass(frozen=True)
class Settings:
    n1: int = C.DEFAULTS["n1"]
    seed: int = C.DEFAULTS["seed"]
    regel: str = C.DEFAULTS["regel"]
    n2: int = C.DEFAULTS["n2"]
    t: int = C.DEFAULTS["t"]
    n3: int = C.DEFAULTS["n3"]
    n4: int = C.DEFAULTS["n4"]
    shift: float = C.DEFAULTS["shift"]
    n5: int = C.DEFAULTS["n5"]
    q: float = C.DEFAULTS["q"]
    nv: int = C.DEFAULTS["nv"]
    dv: int = C.DEFAULTS["dv"]


# --- Experiment 1: eine Mischung legen ------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Mischung:
    n: int
    seed: int
    regel: str
    folge: tuple[int, ...]
    stapel: tuple[tuple[int, ...], ...]
    lis: int                              # Mindestzahl Stapel (= längste wachsende Teilfolge)
    lis_positionen: tuple[int, ...]
    erwartung: float
    streuung: float
    anteil_weniger: float                 # P(L < lis)
    anteil_gleich: float                  # P(L = lis)
    anteil_mehr: float                    # P(L > lis)

    @property
    def stapelzahl(self) -> int:
        return len(self.stapel)


def mischung(n: int, seed: int, regel: str = L.REGEL_ERSTER) -> Mischung:
    folge = folge_aus_zufalls_seed(n, seed)
    stapel = L.stapel_legen(folge, regel)
    lis = L.lis_laenge(folge)
    v = E.verteilung(n)
    p = v.wahrscheinlichkeit
    weniger = E.wahrscheinlichkeit_hoechstens(p, lis - 1)
    bis = E.wahrscheinlichkeit_hoechstens(p, lis)
    mittel, var, _ = E.kennzahlen(p)
    return Mischung(n, seed, regel, tuple(folge), tuple(tuple(s) for s in stapel), lis, tuple(L.lis_positionen(folge)),
                    mittel, math.sqrt(var), weniger, bis - weniger, 1.0 - bis)


def verdict_mischung(m: Mischung) -> tuple[str, str]:
    text = (f"n = {m.n}, Zufalls-Seed {m.seed}: Diese Folge braucht mindestens **{m.lis} Stapel** (längste wachsende Teilfolge). Erwartet werden {de(m.erwartung)} ± {de(m.streuung)} "
            f"(Modell U, exakt): In {prozent(m.anteil_weniger)} der Folgen genügen weniger Stapel, in {prozent(m.anteil_gleich)} genau so viele, in {prozent(m.anteil_mehr)} braucht man mehr.")
    if m.regel != L.REGEL_ERSTER:
        if m.stapelzahl > m.lis:
            text += f" Die Regel „{m.regel}“ legt hier {m.stapelzahl} Stapel, also {m.stapelzahl - m.lis} mehr als nötig."
        else:
            text += f" Die Regel „{m.regel}“ kommt bei dieser Folge mit {m.stapelzahl} Stapeln aus; bei anderen Folgen braucht sie mehr (Handfolge n = 6: vier statt drei)."
    return "info", text


# --- Experiment 2: exakte Verteilung gegen Simulation -----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Verteilungsvergleich:
    n: int
    mischungen: int
    seed: int
    exakt: E.Verteilung
    mittel: float
    streuung: float
    schiefe: float
    simulation: S.Messung
    abweichung_se: float                  # |Simulationsmittel − exaktes Mittel| in Standardfehlern
    aufzaehlung_gleich: bool | None       # nur für n <= 8: Aufzählung gleich Plancherel-Summe


def verteilungsvergleich(n: int, mischungen: int, seed: int) -> Verteilungsvergleich:
    if n * mischungen > C.LIVE_PRODUKT_MAX:
        raise ValueError(f"n × Mischungen darf live höchstens {ganz(C.LIVE_PRODUKT_MAX)} sein (Rechenzeit etwa eine Sekunde).")
    v = E.verteilung(n)
    mittel, var, schiefe = E.kennzahlen(v.wahrscheinlichkeit)
    sim = S.simuliere(n, mischungen, seed)
    abw = abs(sim.mittel - mittel) / sim.fehler if sim.fehler > 0 else (0.0 if sim.mittel == mittel else math.inf)
    gleich = (E.aufzaehlung(n) == E.plancherel(n)) if n <= E.LIVE_AUFZAEHLUNG_MAX else None
    return Verteilungsvergleich(n, mischungen, seed, v, mittel, math.sqrt(var), schiefe, sim, abw, gleich)


def verdict_verteilung(r: Verteilungsvergleich) -> tuple[str, str]:
    if r.exakt.haeufigkeiten is not None and r.n <= E.LIVE_AUFZAEHLUNG_MAX:
        zahlen = ", ".join(ganz(c) for c in r.exakt.haeufigkeiten[1:])
        kopf = (f"n = {r.n}: Aufzählung aller {ganz(math.factorial(r.n))} Folgen und Plancherel-Summe geben dieselben Zahlen: {zahlen} Folgen mit 1 bis {r.n} Stapeln "
                f"(Mittel {de(r.mittel, 3)}, Streuung {de(r.streuung, 3)}).")
    else:
        kopf = f"n = {r.n}: Mittel {de(r.mittel, 3)}, Streuung {de(r.streuung, 3)} ({r.exakt.quelle})."
    if r.abweichung_se <= 4.0:
        sim = (f" Die Simulation ({ganz(r.mischungen)} Mischungen, Zufalls-Seed {r.seed}) gibt {de(r.simulation.mittel, 3)} ± {de(r.simulation.fehler, 3)} "
               f"und liegt innerhalb von vier Standardfehlern des exakten Mittels.")
        return "success", kopf + sim
    if math.isinf(r.abweichung_se):
        abstand = "außerhalb jeder Zufallsschwankung (alle Mischungen gaben dieselbe Stapelzahl)"
    else:
        abstand = f"{de(r.abweichung_se, 1)} Standardfehler vom exakten Mittel entfernt (bei reinem Zufall träfe das in weniger als 1 von 10 000 Fällen zu, Normalnäherung)"
    sim = (f" Die Simulation ({ganz(r.mischungen)} Mischungen, Zufalls-Seed {r.seed}) gibt {de(r.simulation.mittel, 3)} ± {de(r.simulation.fehler, 3)} "
           f"und liegt {abstand}.")
    return "warning", kopf + sim


# --- Experiment 3: wie gut ist 2√n? -----------------------------------------------------------------------------------------------------------------

def zwei_wurzel(n: int) -> float:
    return 2.0 * math.sqrt(n)


def tw_naeherung(n: int, faktor: float | None = None) -> float:
    """2√n − c·n^(1/6) mit c = 1,7711 (Konstante F₂-Mittel bei voller Genauigkeit); `faktor` setzt c ersatzweise (z. B. 1,711)."""
    if faktor is None:
        return zwei_wurzel(n) + C.TW_MITTEL * n ** (1.0 / 6.0)
    return zwei_wurzel(n) - faktor * n ** (1.0 / 6.0)


@dataclass(frozen=True)
class Naeherung:
    n: int
    exakt: float
    zwei_wurzel: float
    luecke: float             # 2√n − exakt (Stapel)
    luecke_relativ: float     # bezogen auf den exakten Wert
    tw: float                 # 2√n − 1,7711 n^(1/6)
    rest: float               # exakt − tw
    tw_halb: float            # tw + 1/2
    rest_halb: float          # exakt − tw_halb


def naeherung(n: int) -> Naeherung:
    exakt = E.kennzahlen_eingefroren(n)[0] if n > E.LIVE_PLANCHEREL_MAX else E.mittel(n)
    w = zwei_wurzel(n)
    tw = tw_naeherung(n)
    return Naeherung(n, exakt, w, w - exakt, (w - exakt) / exakt, tw, exakt - tw, tw + 0.5, exakt - (tw + 0.5))


def rest_exponent(n_klein: int = 20, n_gross: int = 150) -> float:
    """Wie schnell fällt der Rest nach Abzug von ½? Exponent e mit Rest ~ n^(−e), nur aus zwei Punkten gerechnet (kein Beweis)."""
    a, b = naeherung(n_klein).rest_halb, naeherung(n_gross).rest_halb
    return math.log(a / b) / math.log(n_gross / n_klein)


def quellenvergleich(n: int = 52) -> dict:
    """Die verschiedenen Vorfaktoren: n-Wert mit 1,711 (Aldous/Diaconis, nach Quellenbericht), mit 1,7711 (Baik/Deift/Johansson, Bornemann) und exakt."""
    return {"n": n, "faktor_ad": tw_naeherung(n, C.FAKTOR_ALDOUS_DIACONIS), "faktor_bdj": tw_naeherung(n, C.FAKTOR_BDJ), "exakt": E.kennzahlen_eingefroren(n)[0]}


def grosse_n_zeilen() -> list[dict]:
    """Vorgerechnete Simulation Modell U für große n: Mittel, Standardfehler, 2√n und Abstand in Prozent des Mittels."""
    zeilen = []
    for n, (mes, seed) in sorted(S.grosse_n().items()):
        w = zwei_wurzel(n)
        zeilen.append({"n": n, "mischungen": mes.mischungen, "seed": seed, "mittel": mes.mittel, "fehler": mes.fehler, "zwei_wurzel": w, "luecke_relativ": (w - mes.mittel) / mes.mittel,
                       "luecke": w - mes.mittel, "rest": mes.mittel - tw_naeherung(n)})
    return zeilen


def verdict_naeherung(a: Naeherung) -> tuple[str, str]:
    text = (f"n = {a.n}: exakt {de(a.exakt, 3)} Stapel im Mittel; 2√n = {de(a.zwei_wurzel)} ({prozent_vz(a.luecke_relativ)} gegen das exakte Mittel, also {de(a.luecke)} Stapel zu viel); "
            f"mit der Korrektur −1,7711·n^(1/6): {de(a.tw)} ({de_vz(a.tw - a.exakt)} gegen exakt); mit der Korrektur plus ½: {de(a.tw_halb)} ({de_vz(a.tw_halb - a.exakt)}).")
    return ("warning" if a.luecke_relativ > 0.10 else "info"), text


# --- Experiment 4: Streuung und Form gegen Tracy-Widom -----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Form:
    n: int
    streuung: float
    streuung_anteil: float    # Streuung / (0,9018 · n^(1/6))
    schiefe: float
    abstand: float            # Kolmogorov-Abstand an den ganzen k, Verschiebung 0
    beste_verschiebung: float
    abstand_beste: float
    abstand_shift: float      # mit der eingestellten Verschiebung


def form(n: int, shift: float = 0.0) -> Form:
    p = E.verteilung(n).wahrscheinlichkeit
    _, var, schiefe = E.kennzahlen(p)
    c, best = TW.beste_verschiebung(p, n)
    return Form(n, math.sqrt(var), math.sqrt(var) / (C.TW_STREUUNG * n ** (1.0 / 6.0)), schiefe, TW.kolmogorov_abstand(p, n), c, best, TW.kolmogorov_abstand(p, n, shift))


def verdict_form(f: Form, abstand_n10: float) -> tuple[str, str]:
    text = (f"n = {f.n}: Die Streuung ist {prozent(f.streuung_anteil)} des Grenzwerts 0,9018·n^(1/6) (exakt {de(f.streuung, 3)}), die Schiefe {de(f.schiefe, 3)} gegen {de(C.TW_SCHIEFE, 3)} bei Tracy-Widom. "
            f"Der Kolmogorov-Abstand zur Tracy-Widom-Verteilung, nur an den ganzen k gemessen, ist {de(f.abstand, 3)} (mit der besten Verschiebung c = {de(f.beste_verschiebung)}: {de(f.abstand_beste, 3)}); "
            f"bei n = 10 sind es {de(abstand_n10, 3)}. Die Annäherung ist langsam.")
    return "info", text


# --- Experiment 5: wie viele Stapel einplanen -------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Planung:
    n: int
    q: float                  # Sicherheit als Anteil (0 bis 1)
    mittel: float
    m: int                    # kleinste Stapelzahl mit P(L <= m) >= q
    p_m: float
    p_vorher: float           # P(L <= m − 1)
    m_median: int
    wahrscheinlichkeit: tuple[float, ...]


def planung(n: int, q_prozent: float) -> Planung:
    q = q_prozent / 100.0
    p = E.verteilung(n).wahrscheinlichkeit
    m = E.kleinstes_m(p, q)
    return Planung(n, q, E.kennzahlen(p)[0], m, E.wahrscheinlichkeit_hoechstens(p, m), E.wahrscheinlichkeit_hoechstens(p, m - 1), E.kleinstes_m(p, 0.5), tuple(p))


def verdict_planung(pl: Planung) -> tuple[str, str]:
    text = (f"n = {pl.n}: {pl.m_median} Stapel reichen in der Hälfte der Folgen, **{pl.m} Stapel** in mindestens {prozent(pl.q)} (genau {prozent(pl.p_m, 2)}; mit {pl.m - 1} Stapeln wären es nur {prozent(pl.p_vorher, 2)}). "
            f"Im Mittel braucht eine Folge {de(pl.mittel)} Stapel, das sind {de(pl.n / pl.mittel)} Container je Stapel (Modell U, exakt, Zähleinheit Folgen).")
    return "success", text


@dataclass(frozen=True)
class Verweilzeit:
    n: int
    d: int
    messung: S.Messung
    modell_u: float           # Mittel bei gleichverteilter Folge (exakt bis n = 150, sonst gemessen)
    modell_u_exakt: bool
    verhaeltnis: float        # Mittel Modell V / Mittel Modell U (Verhältnis zweier Mittel)
    container_je_stapel: float
    m_q: int                  # Stapelzahl, die in mindestens q der Zufallsfolgen reicht
    q: float


def verweilzeit(n: int, d: int, q_prozent: float) -> Verweilzeit:
    mes = S.modell_v(n, d)
    if n <= E.exakt_n_max():
        u, exakt = E.mittel(n), True
    else:
        u, exakt = S.modell_u_gemessen(n).mittel, False
    q = q_prozent / 100.0
    return Verweilzeit(n, d, mes, u, exakt, mes.mittel / u, n / mes.mittel, mes.kleinstes_m(q), q)


def verdict_verweilzeit(v: Verweilzeit) -> tuple[str, str]:
    u_art = "exakt" if v.modell_u_exakt else "gemessen"
    text = (f"Bleiben die Wagen im Mittel D = {ganz(v.d)} Ankunftsabstände (Modell V, ausgedacht), braucht eine Folge mit n = {v.n} im Mittel {de(v.messung.mittel, 1)} ± {de(v.messung.fehler, 2)} Stapel "
            f"({ganz(v.messung.mischungen)} Zufallsfolgen) statt {de(v.modell_u, 1)} bei gleichverteilter Folge ({u_art}): das {de(v.verhaeltnis)}-Fache, {de(v.container_je_stapel, 1)} Container je Stapel. "
            f"{v.m_q} Stapel reichen in mindestens {prozent(v.q)} der Zufallsfolgen.")
    return "info", text


def sofort_zeilen() -> list[dict]:
    """n = 10: je D der Anteil der Folgen, die ein Stapel sofort sortiert, und die mittlere Stapelzahl beim verzögerten Einlagern (vorgerechnet, Zufallsfolgen)."""
    zeilen = []
    for d, e in S.sofort_gegen_verzoegert().items():
        zeilen.append({"d": d, "sortiert": e["sortiert"], "verzoegert": e["verzoegert"].mittel, "mischungen": e["mischungen"]})  # sortiert: Anteil der Folgen (0 bis 1)
    return zeilen


def verdict_sofort(zeilen: list[dict]) -> tuple[str, str]:
    klein = next(z for z in zeilen if z["d"] == str(C.SOFORT_D[0]))
    u = next(z for z in zeilen if z["d"] == "unendlich")
    text = (f"Verbindungsfaden bei n = {C.SOFORT_N} (vorgerechnet, {ganz(klein['mischungen'])} Zufallsfolgen je Zeile): Bei D = {de(float(klein['d']), 1)} sortiert **ein** Stapel {prozent(klein['sortiert'])} der Folgen "
            f"sofort, verzögert braucht man im Mittel {de(klein['verzoegert'], 1)} Stapel; bei gleichverteilter Folge sortiert ein Stapel {prozent(u['sortiert'], 2)}, verzögert sind es {de(u['verzoegert'], 1)} Stapel im Mittel. "
            f"„Sofort ausgeben“ und „verzögert einlagern“ sind verschiedene Ziele mit verschiedenen Stapelzahlen.")
    return "info", text


# --- Kernfragen -------------------------------------------------------------------------------------------------------------------------------------

def verdict_kernfrage_1(n: int) -> tuple[str, str]:
    p = E.verteilung(n).wahrscheinlichkeit
    mittel, var, _ = E.kennzahlen(p)
    return "info", f"Eine zufällige Ankunftsfolge von n = {n} Containern braucht beim verzögerten Einlagern im Mittel **{de(mittel, 3)} Stapel** (Streuung {de(math.sqrt(var), 3)}; Modell U, exakt, Zähleinheit Folgen)."


def verdict_kernfrage_2(a: Naeherung) -> tuple[str, str]:
    art = "warning" if a.luecke_relativ > 0.10 else "info"
    return art, (f"Die Formel 2√n sagt für n = {a.n} {de(a.zwei_wurzel)} Stapel, exakt sind es {de(a.exakt, 3)}: sie liegt **{prozent(a.luecke_relativ)}** darüber ({de(a.luecke)} Stapel). "
                 f"Die Formel gilt für sehr große n; bei dieser Größe ist sie zu hoch.")


def verdict_kernfrage_3(pl: Planung) -> tuple[str, str]:
    return "success", f"Für n = {pl.n} Container reichen **{pl.m} Stapel** in mindestens {prozent(pl.q)} der Folgen (Modell U, exakt); mit kurzer Verweilzeit werden es deutlich mehr (Experiment 5)."
