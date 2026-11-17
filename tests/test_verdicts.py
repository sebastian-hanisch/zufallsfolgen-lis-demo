"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier. Ein Verdikt ist eine reine Funktion (Art, Text)."""

import math
from dataclasses import replace

import zfl_evaluation as ev
import zfl_exact as E
import zfl_lis as L
import zfl_sim as S


def _mischung(regel=L.REGEL_ERSTER, stapel=((1,), (3, 2), (6, 5, 4))):
    return ev.Mischung(6, 218, regel, (1, 3, 6, 2, 5, 4), stapel, 3, (0, 1, 5), 3.14, 0.76, 0.183, 0.529, 0.287)


def test_zahlenformat():
    assert ev.de(3.14159, 2) == "3,14" and ev.de(-0.55, 2) == "−0,55" and ev.de(2, 0) == "2"
    assert ev.de_vz(0.05) == "+0,05" and ev.de_vz(-0.55) == "−0,55" and ev.de_vz(0.0) == "+0,00"
    assert ev.prozent(0.1949) == "19,5 %" and ev.prozent_vz(0.247) == "+24,7 %" and ev.prozent(0.0046, 2) == "0,46 %"
    assert ev.ganz(3628800) == "3 628 800" and ev.ganz(120) == "120"


def test_verdict_mischung_nennt_n_seed_mindestzahl_erwartung_und_anteile():
    art, text = ev.verdict_mischung(_mischung())
    assert art == "info"
    for teil in ("n = 6, Zufalls-Seed 218", "mindestens **3 Stapel**", "3,14 ± 0,76", "In 18,3 % der Folgen genügen weniger Stapel", "in 52,9 % genau so viele", "in 28,7 % braucht man mehr"):
        assert teil in text
    assert "Regel" not in text


def test_verdict_mischung_gegenregel_mehr_oder_gleich_viele_stapel():
    _, mehr = ev.verdict_mischung(_mischung(L.REGEL_GROESSTE, ((1,), (3,), (6, 2), (5, 4))))
    assert "legt hier 4 Stapel, also 1 mehr als nötig" in mehr
    _, gleich = ev.verdict_mischung(_mischung(L.REGEL_GROESSTE, ((1,), (3, 2), (6, 5, 4))))
    assert "kommt bei dieser Folge mit 3 Stapeln aus" in gleich and "mehr als nötig" not in gleich


def _vergleich(haeufigkeit, n=5, t=None):
    sim = S.messung_aus_haeufigkeit(haeufigkeit)
    v = E.verteilung(n)
    mittel, var, schiefe = E.kennzahlen(v.wahrscheinlichkeit)
    abw = abs(sim.mittel - mittel) / sim.fehler
    return ev.Verteilungsvergleich(n, sim.mischungen, 7, v, mittel, math.sqrt(var), schiefe, sim, abw, True if n <= 8 else None)


def test_verdict_verteilung_n5_nennt_die_haeufigkeiten_und_ist_gruen_innerhalb_von_vier_standardfehlern():
    art, text = ev.verdict_verteilung(_vergleich({1: 10, 2: 410, 3: 610, 4: 160, 5: 10}))     # genau 10 mal die Verteilung 1, 41, 61, 16, 1
    assert art == "success"
    for teil in ("n = 5: Aufzählung aller 120 Folgen und Plancherel-Summe geben dieselben Zahlen: 1, 41, 61, 16, 1 Folgen mit 1 bis 5 Stapeln", "Mittel 2,792", "Streuung 0,706",
                 "1 200 Mischungen", "Zufalls-Seed 7", "gibt 2,792 ± 0,020", "innerhalb von vier Standardfehlern"):
        assert teil in text, teil


def test_verdict_verteilung_warnt_ab_mehr_als_vier_standardfehlern():
    art, text = ev.verdict_verteilung(_vergleich({2: 600, 4: 600}))                              # Mittel 3, exakt 2,7917: 7,2 Standardfehler
    assert art == "warning" and "7,2 Standardfehler vom exakten Mittel entfernt" in text and "1 von 10 000" in text


def test_verdict_verteilung_grenze_bei_genau_vier_standardfehlern_ist_noch_gruen():
    r = _vergleich({1: 10, 2: 410, 3: 610, 4: 160, 5: 10})
    assert ev.verdict_verteilung(replace(r, abweichung_se=4.0))[0] == "success"
    assert ev.verdict_verteilung(replace(r, abweichung_se=4.01))[0] == "warning"


def test_verdict_verteilung_gross_nennt_die_quelle():
    r = _vergleich({10: 100, 11: 100, 12: 100}, n=52)
    _, text = ev.verdict_verteilung(r)
    assert text.startswith("n = 52: Mittel 11,566, Streuung 1,407 (Gessel-Rekursion, vorgerechnet).")


def test_verdict_naeherung_zahlen_und_schwelle_zehn_prozent():
    a = ev.Naeherung(100, 16.7384, 20.0, 3.2616, 0.1949, 16.1842, 0.5542, 16.6842, 0.0542)
    art, text = ev.verdict_naeherung(a)
    assert art == "warning"
    for teil in ("n = 100: exakt 16,738", "2√n = 20,00 (+19,5 % gegen das exakte Mittel, also 3,26 Stapel zu viel)", "16,18 (−0,55 gegen exakt)", "plus ½: 16,68 (−0,05)"):
        assert teil in text, teil
    assert ev.verdict_naeherung(ev.Naeherung(100, 18.0, 19.8, 1.8, 0.10, 17.5, 0.5, 18.0, 0.0))[0] == "info"        # genau 10 %: noch info
    assert ev.verdict_naeherung(ev.Naeherung(100, 18.0, 19.8, 1.8, 0.1001, 17.5, 0.5, 18.0, 0.0))[0] == "warning"


def test_verdict_form_zahlen():
    f = ev.Form(100, 1.6398, 0.844, 0.3257, 0.0548, -0.09, 0.0456, 0.0548)
    art, text = ev.verdict_form(f, 0.1388)
    assert art == "info"
    for teil in ("n = 100: Die Streuung ist 84,4 % des Grenzwerts 0,9018·n^(1/6) (exakt 1,640)", "die Schiefe 0,326 gegen 0,224", "Abstand zur Tracy-Widom-Verteilung, nur an den ganzen k gemessen, ist 0,055",
                 "c = −0,09: 0,046", "bei n = 10 sind es 0,139"):
        assert teil in text, teil


def _planung(n=52, q=0.95):
    return ev.Planung(n, q, 11.566, 14, 0.9751, 0.9127, 11, (0.0,))


def test_verdict_planung_zahlen():
    art, text = ev.verdict_planung(_planung())
    assert art == "success"
    for teil in ("n = 52: 11 Stapel reichen in der Hälfte", "**14 Stapel** in mindestens 95,0 %", "genau 97,51 %", "mit 13 Stapeln wären es nur 91,27 %", "11,57 Stapel", "4,50 Container je Stapel"):
        assert teil in text, teil


def _verweilzeit(d=10, verhaeltnis=2.4, exakt=True):
    mes = S.messung_aus_haeufigkeit({40: 2000, 41: 2000})
    return ev.Verweilzeit(100, d, mes, 16.7, exakt, verhaeltnis, 100 / mes.mittel, 43, 0.95)


def test_verdict_verweilzeit_zahlen_und_art_der_referenz():
    art, text = ev.verdict_verweilzeit(_verweilzeit())
    assert art == "info"
    for teil in ("D = 10 Ankunftsabstände", "n = 100 im Mittel 40,5 ± 0,01 Stapel", "4 000 Zufallsfolgen", "statt 16,7 bei gleichverteilter Folge (exakt)", "das 2,40-Fache", "2,5 Container je Stapel",
                 "43 Stapel reichen in mindestens 95,0 %"):
        assert teil in text, teil
    assert "(gemessen)" in ev.verdict_verweilzeit(_verweilzeit(exakt=False))[1]
    assert "D = 100 000" in ev.verdict_verweilzeit(_verweilzeit(d=100000))[1]


def test_verdict_sofort_zahlen():
    zeilen = [{"d": "0.5", "sortiert": 0.9967, "verzoegert": 9.3866, "mischungen": 20000}, {"d": "unendlich", "sortiert": 0.0042, "verzoegert": 4.32855, "mischungen": 20000}]
    art, text = ev.verdict_sofort(zeilen)
    assert art == "info"
    for teil in ("n = 10", "20 000 Zufallsfolgen je Zeile", "Bei D = 0,5 sortiert **ein** Stapel 99,7 % der Folgen sofort", "im Mittel 9,4 Stapel", "sortiert ein Stapel 0,42 %", "sind es 4,3 Stapel"):
        assert teil in text, teil


def test_kernfragen():
    art, text = ev.verdict_kernfrage_1(52)
    assert art == "info" and "n = 52" in text and "**11,566 Stapel**" in text and "Streuung 1,407" in text
    a = ev.Naeherung(100, 16.7384, 20.0, 3.2616, 0.1949, 16.1842, 0.5542, 16.6842, 0.0542)
    art, text = ev.verdict_kernfrage_2(a)
    assert art == "warning" and "für n = 100 20,00 Stapel" in text and "exakt sind es 16,738" in text and "**19,5 %** darüber (3,26 Stapel)" in text
    art, text = ev.verdict_kernfrage_3(_planung())
    assert art == "success" and "n = 52 Container reichen **14 Stapel** in mindestens 95,0 %" in text
