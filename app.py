"""Zufallsfolgen: Wie viele Stapel braucht eine zufällige Ankunftsfolge? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Eine zufällige Ankunftsfolge von Containern (Abholränge 1 bis n, alle Reihenfolgen gleich wahrscheinlich) braucht beim verzögerten Einlagern so viele Stapel, wie ihre
längste wachsende Teilfolge lang ist. Die Demo zeigt die exakte Verteilung dieser Zahl, wie schlecht die Formel 2√n bei Demo-Größen ist und wie viele Stapel man einplanen muss.
Die Ankunftsfolgen sind ausgedacht (Modell, kein Betrieb).

Lauffähig mit: streamlit run app.py
"""

import math

import streamlit as st

import zfl_constants as C
import zfl_evaluation as ev
import zfl_exact as E
import zfl_lis as L
from zfl_layout import dunkles_design, kopf_css
from zfl_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from zfl_visualization import (
    build_form,
    build_luecke_prozent,
    build_naeherung_kurven,
    build_planung,
    build_stapel,
    build_verteilung,
    build_verweilzeit,
)

st.set_page_config(page_title="Zufallsfolgen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _mischung(n, seed, regel):
    return ev.mischung(n, seed, regel)


@st.cache_data(show_spinner="Ziehe die Mischungen …")
def _vergleich(n, t, seed):
    return ev.verteilungsvergleich(n, t, seed)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in zfl_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🎲 Zufallsfolgen: Wie viele Stapel braucht eine zufällige Ankunftsfolge?")
st.markdown(
    """
Container kommen in zufälliger Reihenfolge an und werden erst abgeholt, wenn **alle** da sind. Jeder hat eine Abholrangzahl (Rang 1 zuerst); auf einen Stapel darf nur ein Container mit **kleinerem**
Rang als der oberste. Dann ist die **Mindestzahl Stapel** die Länge der **längsten wachsenden Teilfolge** (LIS). Wie viele Stapel braucht eine **zufällige** Folge von n Containern, **wie gut ist die bekannte Formel
2√n**, und **wie viele Stapel muss man einplanen**? Die Folgen sind **ausgedacht** (alle Reihenfolgen gleich wahrscheinlich, oder Wagen mit einer gesetzten Verweilzeit): ein **Modell, keine reale Ankunftsfolge**.

Weiter unten: die Kernfragen, vier weitere **🔬 Experimente**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So legt man die Stapel und so zählt man die Folgen", expanded=True):
    st.markdown(
        """
1. **Stapelregel (fallende Stapel):** Der nächste Container kommt auf den ersten Stapel von links, dessen oberster Container einen **größeren** Rang hat; passt keiner, beginnt ein neuer Stapel rechts.
   Beispiel Handfolge 1 3 6 2 5 4: 1 neu, 3 neu, 6 neu, 2 auf die 3, 5 auf die 6, 4 auf die 5. Es entstehen die Stapel [1], [3, 2], [6, 5, 4]: **drei Stapel**, und die längste wachsende Teilfolge (zum Beispiel 1 3 4) hat Länge 3.
2. **Warum die LIS die Mindestzahl ist:** Zwei Container einer wachsenden Teilfolge (kleiner Rang zuerst) können nie auf demselben fallenden Stapel liegen; also braucht man mindestens so viele Stapel, wie die Teilfolge lang ist, und die Regel oben schafft genau so viele.
3. **Alle Folgen zählen:** Bei n = 5 gibt es 120 Folgen: genau 1, 41, 61, 16 und 1 von ihnen brauchen 1 bis 5 Stapel. Für große n geht das Aufzählen nicht mehr (n = 10: 3 628 800 Folgen); die Zahlen kommen dann aus der Plancherel-Summe (live bis n = 30) und aus einer vorgerechneten Tabelle (bis n = 150).
4. **Zwei Ziele nicht verwechseln:** Hier wird **verzögert eingelagert** (alle liegen, dann wird geholt). „Sofort ausgeben“ ist ein anderes Ziel mit anderen Stapelzahlen (Experiment 5).
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.caption("Die Regler stehen bei ihren Experimenten.")

# --- Ergebnis: eine Mischung legen (Experiment 1) -----------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis (Experiment 1): Eine zufällige Ankunftsfolge legen")
c1, c2, c3 = st.columns([2, 2, 3])
with c1:
    n1 = st.slider("Zahl der Container n", *bounds("n1_slider"), key="n1_slider", help="Zahl der Container der Ankunftsfolge (die exakte Vergleichsverteilung gibt es bis n = 150).")
with c2:
    seed = st.number_input("Zufalls-Seed der Mischung", *bounds("seed_input"), key="seed_input", step=1, help="Gleicher Zufalls-Seed, gleiche Folge (SplitMix64, auf jeder Plattform dieselbe).")
    st.button("🎲 Neue Mischung würfeln", width="stretch", on_click=randomize_seed)
with c3:
    regel = st.selectbox("Stapelregel", list(L.REGELN), key="regel_select",
                         help="Die erste Regel legt genau so viele Stapel wie die LIS. Die zweite (größte passende Spitze) ist ein Gegenbeispiel und braucht manchmal mehr.")

m = _mischung(int(n1), int(seed), regel)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Mindestzahl Stapel (LIS)", m.lis)
k2.metric("Stapel der gewählten Regel", m.stapelzahl, delta=f"{m.stapelzahl - m.lis:+d} gegen die Mindestzahl", delta_color="inverse" if m.stapelzahl > m.lis else "off")
k3.metric("Erwartung (exakt)", ev.de(m.erwartung, 2), delta=f"± {ev.de(m.streuung, 2)} Streuung", delta_color="off")
k4.metric("Folgen mit weniger Stapeln", ev.prozent(m.anteil_weniger), delta=f"gleich viele: {ev.prozent(m.anteil_gleich)}", delta_color="off")
st.plotly_chart(build_stapel(m), width="stretch", key="chart_stapel")
st.caption("Jede Karte ist ein Container mit seinem Rang; oben liegt der kleinste Rang. Orange: die Container einer längsten wachsenden Teilfolge (eine davon).")
with st.expander("Die Ankunftsfolge im Wortlaut"):
    st.markdown("Ränge in Ankunftsreihenfolge: " + " ".join(str(x) for x in m.folge))
kind, text = ev.verdict_mischung(m)
getattr(st, kind)(text)

# --- Kernfragen ---------------------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfragen")
n3_stand = int(st.session_state.get("n3_slider", C.DEFAULTS["n3"]))
n5_stand = int(st.session_state.get("n5_slider", C.DEFAULTS["n5"]))
q_stand = float(st.session_state.get("q_slider", C.DEFAULTS["q"]))
st.markdown("**1. Wie viele Stapel braucht eine zufällige Folge?** (n aus dem Ergebnis oben)")
kind, text = ev.verdict_kernfrage_1(int(n1))
getattr(st, kind)(text)
st.markdown("**2. Wie gut ist die Formel 2√n?** (n aus Experiment 3)")
kind, text = ev.verdict_kernfrage_2(ev.naeherung(n3_stand))
getattr(st, kind)(text)
st.markdown("**3. Wie viele Stapel muss ich einplanen?** (n und Sicherheit aus Experiment 5)")
kind, text = ev.verdict_kernfrage_3(ev.planung(n5_stand, q_stand))
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 2: exakte Verteilung gegen Simulation ----------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Die ganze Verteilung, exakt und simuliert")
st.caption(f"Exakt: alle n! Folgen gleich wahrscheinlich (Zähleinheit Folgen; bis n = 8 aufgezählt, bis n = 30 live aus der Plancherel-Summe, darüber vorgerechnet bis n = 150). "
           f"Simulation: Zufallsfolgen mit dem Zufalls-Seed oben; n × Mischungen höchstens {ev.ganz(C.LIVE_PRODUKT_MAX)} (etwa eine Sekunde Rechenzeit).")
e1, e2 = st.columns(2)
with e1:
    n2 = st.slider("Zahl der Container n (Verteilung)", *bounds("n2_slider"), key="n2_slider", help="Bis n = 8 wird aufgezählt, bis n = 30 gerechnet, darüber aus der vorgerechneten Tabelle gelesen.")
with e2:
    t = st.slider("Zahl der Mischungen", *bounds("t_slider"), key="t_slider", step=C.T_SCHRITT, help="Zahl der simulierten Zufallsfolgen (je größer, desto kleiner der Standardfehler).")
r2 = _vergleich(int(n2), int(t), int(seed))
x1, x2, x3, x4 = st.columns(4)
x1.metric("Mittel exakt", ev.de(r2.mittel, 3))
x2.metric("Streuung exakt", ev.de(r2.streuung, 3))
x3.metric("Schiefe exakt", ev.de(r2.schiefe, 3))
x4.metric("Mittel simuliert", ev.de(r2.simulation.mittel, 3), delta=f"± {ev.de(r2.simulation.fehler, 3)} Standardfehler", delta_color="off")
st.plotly_chart(build_verteilung(r2), width="stretch", key="chart_verteilung")
zeilen = []
for k in range(1, len(r2.exakt.wahrscheinlichkeit)):
    p = r2.exakt.wahrscheinlichkeit[k]
    if p > 1e-6 or k in r2.simulation.haeufigkeit:
        zeile = {"Stapel k": k, "Anteil exakt (%)": 100.0 * p, "Anteil simuliert (%)": 100.0 * r2.simulation.haeufigkeit.get(k, 0) / r2.simulation.mischungen}
        if r2.exakt.haeufigkeiten is not None:
            zeile = {"Stapel k": k, "Folgen": ev.ganz(r2.exakt.haeufigkeiten[k]), **{a: b for a, b in zeile.items() if a != "Stapel k"}}
        zeilen.append(zeile)
st.dataframe(zeilen, hide_index=True, width="stretch", column_config={
    "Anteil exakt (%)": st.column_config.NumberColumn(format="%.4f %%"), "Anteil simuliert (%)": st.column_config.NumberColumn(format="%.2f %%")})
kind, text = ev.verdict_verteilung(r2)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 3: wie gut ist 2√n -------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Wie gut ist die Formel 2√n? (die Falle dieser Demo)")
st.caption("„Die Stapelzahl ist etwa 2√n“ gilt für sehr große n. Bei Demo-Größen liegt die Formel deutlich darüber, und die Lücke in Stapeln wächst weiter. Zähleinheit: Folgen (exakt, n bis 150) bzw. Zufallsfolgen (vorgerechnete Simulation, n ab 200).")
n3 = st.slider("Zahl der Container n (Näherung)", *bounds("n3_slider"), key="n3_slider", help="Bis n = 150 exakt; größere n stehen in der Tabelle darunter (vorgerechnete Simulation).")
a3 = ev.naeherung(int(n3))
y1, y2, y3, y4 = st.columns(4)
y1.metric("exakt (Mittel)", ev.de(a3.exakt, 3))
y2.metric("2√n", ev.de(a3.zwei_wurzel, 2), delta=f"{ev.prozent_vz(a3.luecke_relativ)} gegen exakt", delta_color="inverse")
y3.metric("2√n − 1,7711·n^(1/6)", ev.de(a3.tw, 2), delta=f"{ev.de_vz(a3.tw - a3.exakt)} gegen exakt", delta_color="off")
y4.metric("… plus ½", ev.de(a3.tw_halb, 2), delta=f"{ev.de_vz(a3.tw_halb - a3.exakt)} gegen exakt", delta_color="off")
st.plotly_chart(build_naeherung_kurven(int(n3)), width="stretch", key="chart_naeherung")
tab = []
for n in (5, 10, 20, 52, 100, 150):
    a = ev.naeherung(n)
    tab.append({"n": n, "Art": "exakt (Folgen)", "Mittel": ev.de(a.exakt, 3), "2√n": ev.de(a.zwei_wurzel, 2), "2√n über dem Mittel": ev.prozent_vz(a.luecke_relativ), "Lücke (Stapel)": ev.de(a.luecke, 2),
                "Rest zur Korrektur": ev.de_vz(a.rest, 3), "Rest nach Abzug von ½": ev.de_vz(a.rest_halb, 3)})
for z in ev.grosse_n_zeilen():
    tab.append({"n": z["n"], "Art": f"vorgerechnet, {ev.ganz(z['mischungen'])} Zufallsfolgen", "Mittel": f"{ev.de(z['mittel'], 2)} ± {ev.de(z['fehler'], 2)}", "2√n": ev.de(z["zwei_wurzel"], 2),
                "2√n über dem Mittel": ev.prozent_vz(z["luecke_relativ"]), "Lücke (Stapel)": ev.de(z["luecke"], 2), "Rest zur Korrektur": ev.de_vz(z["rest"], 2), "Rest nach Abzug von ½": "–"})
st.dataframe(tab, hide_index=True, width="stretch")
st.plotly_chart(build_luecke_prozent(ev.grosse_n_zeilen()), width="stretch", key="chart_luecke")
kind, text = ev.verdict_naeherung(a3)
getattr(st, kind)(text)
qv = ev.quellenvergleich(52)
ex = ev.rest_exponent()
st.warning(
    f"**Die Korrektur schließt die Lücke zum größten Teil, aber nicht ganz:** bei n = 100 sinkt die Lücke von {ev.de(ev.naeherung(100).luecke, 2)} auf {ev.de(ev.naeherung(100).rest, 2)} Stapel. Der Rest zur Korrektur ist dort {ev.de_vz(ev.naeherung(100).rest, 2)} Stapel und fällt nur langsam (n = 20: {ev.de_vz(ev.naeherung(20).rest, 2)}, n = 150: {ev.de_vz(ev.naeherung(150).rest, 2)}). "
    f"Ein halber Stapel passt zur Ganzzahligkeit (die Stapelzahl ist eine ganze Zahl, die Näherung gilt für eine stetige Größe; als Ursache eine Deutung, nicht gemessen und nicht bewiesen); nach Abzug von ½ bleiben {ev.de_vz(ev.naeherung(20).rest_halb, 3)} (n = 20) und "
    f"{ev.de_vz(ev.naeherung(150).rest_halb, 3)} (n = 150), ein Abfall etwa wie n^(−{ev.de(ex, 2)}) (nur aus zwei Punkten gerechnet, kein Beweis). "
    f"**Die Quellen nennen verschiedene Werte für den Vorfaktor:** Aldous und Diaconis 1,711 (nach Quellenbericht, nicht im Original geprüft), Baik/Deift/Johansson und Bornemann 1,7711 (verbindlich). Bei n = 52 gibt das {ev.de(qv['faktor_ad'], 2)} gegen {ev.de(qv['faktor_bdj'], 2)}; exakt sind {ev.de(qv['exakt'], 2)}."
)

st.markdown("---")

# --- Experiment 4: Streuung und Form --------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Streuung und Form gegen die Tracy-Widom-Verteilung")
st.caption("Die Tracy-Widom-Verteilung F₂ ist die Grenzverteilung von (L − 2√n) / n^(1/6). Die Kurve ist vorgerechnet (Fredholm-Determinante). Verglichen wird nur an den ganzen Stapelzahlen k.")
g1, g2 = st.columns(2)
with g1:
    n4 = st.slider("Zahl der Container n (Form)", *bounds("n4_slider"), key="n4_slider", help="Bis n = 150 exakt.")
with g2:
    shift = st.slider("Verschiebung c der Kurve", *bounds("shift_slider"), key="shift_slider", step=C.SHIFT_SCHRITT,
                      help="Die Kurve wird an der Stelle (k + c − 2√n) / n^(1/6) ausgewertet; c = 0 ist die Formel ohne Verschiebung; gemessen passt c ≈ −0,1 besser (README B8).")
f4 = ev.form(int(n4), float(shift))
z1, z2, z3, z4 = st.columns(4)
z1.metric("Streuung (Anteil des Grenzwerts)", ev.prozent(f4.streuung_anteil), delta=f"exakt {ev.de(f4.streuung, 3)}", delta_color="off")
z2.metric("Schiefe", ev.de(f4.schiefe, 3), delta=f"Tracy-Widom {ev.de(C.TW_SCHIEFE, 3)}", delta_color="off")
z3.metric("Abstand bei c = 0", ev.de(f4.abstand, 3))
z4.metric(f"Abstand bei c = {ev.de(float(shift))}", ev.de(f4.abstand_shift, 3), delta=f"beste Verschiebung {ev.de(f4.beste_verschiebung)}: {ev.de(f4.abstand_beste, 3)}", delta_color="off")
st.plotly_chart(build_form(int(n4), E.verteilung(int(n4)).wahrscheinlichkeit, float(shift)), width="stretch", key="chart_form")
kind, text = ev.verdict_form(f4, ev.form(10).abstand)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 5: wie viele Stapel einplanen ---------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 5: Wie viele Stapel plane ich ein, und was ändert eine kurze Verweilzeit?")
st.caption("Teil A: gleichverteilte Folge (Modell U, exakt, Zähleinheit Folgen). Teil B: Wagen mit gesetzter Verweilzeit (Modell V, **ausgedacht**, vorgerechnete Simulation, Zähleinheit Zufallsfolgen); keine reale Ankunftsfolge.")
h1, h2 = st.columns(2)
with h1:
    n5 = st.slider("Zahl der Container n (Planung)", *bounds("n5_slider"), key="n5_slider", help="Bis n = 150 exakt.")
with h2:
    q5 = st.slider("Gewünschte Sicherheit q (%)", *bounds("q_slider"), key="q_slider", step=C.Q_SCHRITT, help="Anteil der Folgen, die in der geplanten Stapelzahl liegen sollen.")
pl = ev.planung(int(n5), float(q5))
st.plotly_chart(build_planung(pl), width="stretch", key="chart_planung")
kind, text = ev.verdict_planung(pl)
getattr(st, kind)(text)
qt = []
for n in (10, 20, 52, 100):
    p = E.verteilung(n).wahrscheinlichkeit
    qt.append({"n": n, "Mittel": ev.de(E.kennzahlen(p)[0], 3), **{f"q = {ev.de(100 * q, 1 if q == 0.999 else 0)} %": E.kleinstes_m(p, q) for q in (0.5, 0.9, 0.95, 0.99, 0.999)}})
st.caption("Kleinste Stapelzahl m mit P(L ≤ m) ≥ q (Folgen, exakt):")
st.dataframe(qt, hide_index=True, width="stretch")

st.markdown("**Teil B: Wagen mit gesetzter Verweilzeit (Modell V)**")
st.caption("Wagen i kommt zur Zeit i und bleibt im Mittel D Ankunftsabstände (Exp-verteilt); der Rang ist die Platznummer der Abfahrt. Kleine D machen die Folge fast sortiert und die Stapelzahl groß.")
w1, w2 = st.columns(2)
with w1:
    nv = st.selectbox("Zahl der Container n (Verweilzeit)", C.V_N_WERTE, key="nv_select", help="Vorgerechnet für diese vier Größen.")
with w2:
    dv = st.selectbox("Mittlere Verweilzeit D (Ankunftsabstände)", C.V_D_WERTE, key="dv_select", help="Vorgerechnet; D = 100 000 entspricht praktisch der gleichverteilten Folge.")
vz = ev.verweilzeit(int(nv), int(dv), float(q5))
v1, v2, v3, v4 = st.columns(4)
v1.metric("Stapel im Mittel", ev.de(vz.messung.mittel, 1), delta=f"± {ev.de(vz.messung.fehler, 1)} Standardfehler", delta_color="off")
v2.metric("gleichverteilte Folge", ev.de(vz.modell_u, 1), delta=f"{ev.de(vz.verhaeltnis)}-Faches", delta_color="inverse")
v3.metric("Container je Stapel", ev.de(vz.container_je_stapel, 1))
v4.metric(f"Stapel für {ev.de(float(q5), 1)} %", vz.m_q)
st.plotly_chart(build_verweilzeit(int(nv), int(dv)), width="stretch", key="chart_verweilzeit")
kind, text = ev.verdict_verweilzeit(vz)
getattr(st, kind)(text)
sz = ev.sofort_zeilen()
st.dataframe([{"D": z["d"].replace(".", ",") if z["d"] != "unendlich" else "gleichverteilt", "ein Stapel sortiert sofort": ev.prozent(z["sortiert"], 2), "Stapel verzögert (Mittel)": ev.de(z["verzoegert"], 2)} for z in sz],
             hide_index=True, width="stretch")
kind, text = ev.verdict_sofort(sz)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
_kurz = ev.verweilzeit(100, 10, 95.0)
_sofort_u = E.catalan(C.SOFORT_N) / math.factorial(C.SOFORT_N)
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Alle n! Folgen gleich wahrscheinlich (Modell U)** | Bei kurzer Verweilzeit (Modell V, n = 100, D = 10) braucht die Folge im Mittel {ev.de(_kurz.messung.mittel, 1)} statt {ev.de(_kurz.modell_u, 1)} Stapel; erst bei D = 10n (n = 20, 100, 1000) liegt der Unterschied unter 3 %. | Experiment 5 |
| **Keine Gleichstände** (alle Ränge verschieden) | Mit gleichen Rängen (Wagen mit Zielgruppen) ist die Mindestzahl nicht mehr die längste streng wachsende Teilfolge. Nicht gemessen; der Kern lehnt solche Folgen mit einer Meldung ab. | [mehrhafenstau-demo](https://github.com/sebastian-hanisch/mehrhafenstau-demo) |
| **Unbegrenzte Stapelhöhe** | Bei begrenzter Höhe ist die Mindestzahl nicht mehr die LIS. Nicht gemessen. | [sortierbar-umstauen-demo](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) |
| **Verzögertes Einlagern** (erst alle einlagern, dann holen) | „Sofort ausgeben“ ist ein anderes Ziel: Bei gleichverteilter Folge sortiert ein Stapel bei n = {C.SOFORT_N} nur {ev.prozent(_sofort_u, 2)} der Folgen (Catalan({C.SOFORT_N}) von {C.SOFORT_N}! Folgen). | [stapel-sortieren-demo](https://github.com/sebastian-hanisch/stapel-sortieren-demo) |
| **Das Modell ist ausgedacht** | Es gibt keine gemessene Ankunftsfolge eines Hafens oder Bahnhofs; Modell V kennt nur eine Exp-verteilte Verweilzeit (andere Verteilungen nicht gemessen). | – |
| **n ≤ 150 exakt** | Für n über 150 gibt es nur die vorgerechnete Simulation (n = 200 bis 10 000). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* eine Folge $\pi = (\pi_1, \dots, \pi_n)$ der Abholränge $1, \dots, n$ in Ankunftsreihenfolge (alle verschieden), bei Modell U alle $n!$ Folgen gleich wahrscheinlich. *Gesucht:* die Verteilung der
Mindestzahl Stapel $L_n$ und wie gut $2\sqrt{n}$ sie beschreibt. Es gibt kein Optimierungsmodell, sondern eine Zählung.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Container; Ränge $1, \dots, n$, Rang 1 wird zuerst geholt |
| $\pi$ | Ankunftsfolge der Ränge |
| $L_n$ | Mindestzahl fallender Stapel (verzögertes Einlagern) = Länge der längsten wachsenden Teilfolge von $\pi$ |
| $\lambda$ | Partition von $n$ (Form eines Young-Tableaus), $\lambda_1$ die erste Zeile |
| $f^\lambda$ | Zahl der Standard-Young-Tableaus der Form $\lambda$ (Hakenformel) |
| $u_k(n)$ | Zahl der Folgen der Länge $n$ mit $L_n \le k$ |
| $I_j$ | modifizierte Besselfunktion erster Art |
| $D$ | mittlere Verweilzeit in Ankunftsabständen (Modell V) |
| $F_2$ | Tracy-Widom-Verteilungsfunktion (GUE) |

**Mindestzahl Stapel.** Mit fallenden Stapeln und verzögertem Einlagern gilt:

$$L_n(\pi) = \max\{\, \ell : \exists\, i_1 < \dots < i_\ell,\ \pi_{i_1} < \dots < \pi_{i_\ell} \,\}$$

Die Regel „erster passender Stapel von links“ legt genau $L_n(\pi)$ Stapel (Aldous/Diaconis 1999, Lemma 1; hier für alle Folgen mit $n \le 8$ nachgezählt, $n = 9$ im langsamen Test).

**Verteilung, Plancherel-Summe** (über die Bijektion von Robinson, Schensted und Knuth; die Bijektion selbst zeigt die Nachbar-Demo [tableaux-rsk-demo](https://github.com/sebastian-hanisch/tableaux-rsk-demo)):

$$P(L_n = k) = \frac{1}{n!} \sum_{\lambda \vdash n,\ \lambda_1 = k} \left(f^\lambda\right)^2, \qquad f^\lambda = \frac{n!}{\prod_{c \in \lambda} h(c)}$$

Dabei ist $h(c)$ die Hakenlänge der Zelle $c$. Die Summe über alle Formen ist live bis $n = 30$ gerechnet.

**Verteilung, Gessel-Rekursion** (nach Gedächtnis, nicht gelesen; hier nur als Werkzeug und gegen Aufzählung und Plancherel-Summe bestätigt):

$$u_k(n) = (n!)^2 \,[x^{2n}] \det\left[ I_{|i-j|}(2x) \right]_{i,j=1}^{k}$$

Die Determinante wird über eine Rekursion in exakten Brüchen gebildet; die Tabelle bis $n = 150$ ist vorgerechnet.

**Näherung und Grenzverteilung** (Baik/Deift/Johansson 1999, Satz 1.1 und sein Folgesatz, nach Quellenbericht):

$$\frac{L_n - 2\sqrt{n}}{n^{1/6}} \longrightarrow F_2 \ \text{in Verteilung}, \qquad \mathbb{E}[L_n] \approx 2\sqrt{n} - 1{,}7711\, n^{1/6}$$

Das Mittel von $F_2$ ist $-1{,}7711$, die Varianz $0{,}8132$. Die Näherung gilt für große $n$ und ist bei Demo-Größen zu niedrig (Experiment 3).

**Obere Schranke für den abgeschnittenen Rest** (Markow):

$$P(L_n \ge k) \le \binom{n}{k} \frac{1}{k!}$$

**Modell V.** Wagen $i = 1, \dots, n$ kommt zur Zeit $i$, bleibt $W_i \sim \mathrm{Exp}$ mit Mittel $D$; Abfahrtszeit $i + W_i$, Rang $\pi_i$ = Platz von $i + W_i$ unter allen Abfahrtszeiten. Es zählt nur die Rangfolge der Abfahrten.

**Was fehlt.** Das ist die Zählung im Modell, keine Herleitung der Sätze; Beweise der Grenzverteilung und der Gessel-Formel stehen nicht in dieser Demo.

**Literatur** (nur wie gelesen, Stufen nach dem Quellenbericht): Aldous und Diaconis 1999 (Lemma 1, Mittelwertformel; nach dem Quellenbericht im Wortlaut); Baik, Deift und Johansson 1999 (Satz 1.1 und sein Folgesatz; nach dem Quellenbericht im Wortlaut, Beweise nicht gelesen);
Bornemann, arXiv 2301.02022 (Konstanten; Auszug). **Nicht gelesen:** Hammersley 1972, Logan und Shepp 1977, Vershik und Kerov 1977, Ulam 1961, Gessel 1990.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
