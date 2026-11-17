"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import numpy as np
import plotly.graph_objects as go

import zfl_constants as C
import zfl_evaluation as ev
import zfl_exact as E
import zfl_sim as S
import zfl_tw as TW


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.22), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_stapel(m: ev.Mischung):
    """Die Stapel als Karten (von unten nach oben fallend, oben liegt der kleinste Rang); die Karten einer längsten wachsenden Teilfolge sind farbig."""
    lis_raenge = {m.folge[p] for p in m.lis_positionen}
    position = {x: i + 1 for i, x in enumerate(m.folge)}
    anzahl = len(m.stapel)
    hoechster = max(len(s) for s in m.stapel)
    groesse = max(12.0, min(30.0, 700.0 / anzahl * 0.8, 340.0 / (hoechster + 1) * 0.85))
    xs, ys, texte, farben, hover = [], [], [], [], []
    for j, s in enumerate(m.stapel, start=1):
        for h, rang in enumerate(s):
            xs.append(j)
            ys.append(h)
            texte.append(str(rang))
            farben.append(C.COLOR_LIS if rang in lis_raenge else C.COLOR_STAPEL)
            hover.append(f"Stapel {j}, Rang {rang}, als {position[rang]}. Container angekommen")
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="markers+text", text=texte, textfont=dict(color="white", size=int(max(8, min(13, groesse * 0.45)))),
                               marker=dict(symbol="square", size=groesse, color=farben, line=dict(color="white", width=1)),
                               hovertext=hover, hovertemplate="%{hovertext}<extra></extra>", showlegend=False))
    fig.update_xaxes(title_text="Stapel (von links, in der Reihenfolge ihrer Eröffnung)", range=[0.4, anzahl + 0.6], dtick=1 if anzahl <= 30 else None)
    fig.update_yaxes(title_text="Lage im Stapel (oben = zuerst geholt)", range=[-0.7, hoechster - 0.3], showticklabels=False)
    return _base(fig, height=int(min(460, max(240, 70 + (hoechster + 1) * (groesse + 8)))))


def build_verteilung(r: ev.Verteilungsvergleich):
    """Balken: exakte Verteilung P(L = k); Punkte mit Fehlerbalken: Anteil der simulierten Zufallsfolgen (± ein Standardfehler des Anteils)."""
    p = r.exakt.wahrscheinlichkeit
    ks = [k for k in range(len(p)) if p[k] > 1e-4 or k in r.simulation.haeufigkeit]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ks, y=[p[k] for k in ks], name="exakt (alle Folgen)", marker_color=C.COLOR_EXAKT, hovertemplate="k = %{x}: %{y:.4f}<extra></extra>"))
    anteile = [r.simulation.haeufigkeit.get(k, 0) / r.simulation.mischungen for k in ks]
    fehler = [math.sqrt(a * (1 - a) / r.simulation.mischungen) for a in anteile]
    fig.add_trace(go.Scatter(x=ks, y=anteile, mode="markers", name=f"Simulation ({r.simulation.mischungen} Mischungen)", marker=dict(color=C.COLOR_SIM, size=9),
                             error_y=dict(type="data", array=fehler, visible=True, color=C.COLOR_SIM), hovertemplate="k = %{x}: %{y:.4f}<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Stapel k (= längste wachsende Teilfolge)", dtick=1 if len(ks) <= 25 else None)
    fig.update_yaxes(title_text="Anteil der Folgen")
    return _base(fig)


def build_naeherung_kurven(n_gewaehlt: int):
    """Exaktes Mittel gegen 2√n und die Näherungen, für n = 5 bis 150."""
    ns = list(range(5, 151))
    exakt = [E.kennzahlen_eingefroren(n)[0] for n in ns]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[ev.zwei_wurzel(n) for n in ns], name="2√n", line=dict(color="#c0504d", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=ns, y=[ev.tw_naeherung(n) + 0.5 for n in ns], name="2√n − 1,7711·n^(1/6) + ½", line=dict(color=C.COLOR_KURVE, width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=ns, y=[ev.tw_naeherung(n) for n in ns], name="2√n − 1,7711·n^(1/6)", line=dict(color="#8d6bb0", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=ns, y=exakt, name="exakt (Mittel der Stapelzahl)", line=dict(color=C.COLOR_EXAKT, width=3)))
    a = ev.naeherung(n_gewaehlt)
    fig.add_trace(go.Scatter(x=[n_gewaehlt, n_gewaehlt], y=[a.exakt, a.zwei_wurzel], mode="lines+markers", name=f"Lücke bei n = {n_gewaehlt}", line=dict(color="black", width=2), marker=dict(size=7)))
    fig.update_xaxes(title_text="Zahl der Container n")
    fig.update_yaxes(title_text="Stapel")
    return _base(fig, height=380)


def build_luecke_prozent(zeilen_gross: list[dict]):
    """Abstand von 2√n zum Mittel in Prozent des Mittels: exakt für n bis 150 (Folgen), darüber vorgerechnete Simulation (Zufallsfolgen), Achse n logarithmisch."""
    ns = list(range(5, 151))
    exakt = [100.0 * (ev.zwei_wurzel(n) - E.kennzahlen_eingefroren(n)[0]) / E.kennzahlen_eingefroren(n)[0] for n in ns]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=exakt, name="exakt (n ≤ 150)", line=dict(color=C.COLOR_EXAKT, width=3)))
    fig.add_trace(go.Scatter(x=[z["n"] for z in zeilen_gross], y=[100.0 * z["luecke_relativ"] for z in zeilen_gross], mode="markers+lines", name="Simulation (vorgerechnet)",
                             line=dict(color=C.COLOR_SIM, width=2, dash="dot"), marker=dict(size=8, color=C.COLOR_SIM)))
    fig.update_xaxes(title_text="Zahl der Container n (logarithmisch)", type="log")
    fig.update_yaxes(title_text="2√n über dem Mittel (%)", rangemode="tozero")
    return _base(fig, height=320)


def build_form(n: int, p, shift: float):
    """Exakte Verteilungsfunktion P(L ≤ k) (Stufen, Punkte an den ganzen k) gegen die Tracy-Widom-Kurve F₂((k + c − 2√n)/n^(1/6))."""
    kum = np.cumsum(np.asarray(p, dtype=float))
    ks = np.arange(len(kum))
    sichtbar = (kum > 1e-4) & (np.concatenate(([1.0], kum[:-1])) < 1 - 1e-4)
    k_lo, k_hi = max(0, int(ks[sichtbar].min()) - 1), min(len(kum) - 1, int(ks[sichtbar].max()) + 2)
    kk = np.linspace(k_lo, k_hi, 240)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=kk, y=TW.f2(TW.skaliert(kk, n, shift)), name=f"Tracy-Widom F₂ (Verschiebung c = {shift:+.2f})".replace(".", ","), line=dict(color="#8d6bb0", width=2)))
    fig.add_trace(go.Scatter(x=ks[k_lo:k_hi + 1], y=kum[k_lo:k_hi + 1], mode="lines+markers", line=dict(color=C.COLOR_EXAKT, width=2, shape="hv"), marker=dict(size=8),
                             name="exakt P(L ≤ k), nur an den ganzen k", hovertemplate="k = %{x}: %{y:.4f}<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Stapel k", range=[k_lo - 0.3, k_hi + 0.3])
    fig.update_yaxes(title_text="Wahrscheinlichkeit", range=[-0.02, 1.02])
    return _base(fig, height=340)


def build_planung(pl: ev.Planung):
    """P(L ≤ m) als Stufen über der Stapelzahl m, die Waagerechte der gewünschten Sicherheit und die kleinste ausreichende Zahl."""
    p = np.asarray(pl.wahrscheinlichkeit, dtype=float)
    kum = np.cumsum(p)
    ms = np.arange(len(kum))
    sichtbar = np.where((kum > 1e-4) & (np.concatenate(([1.0], kum[:-1])) < 1 - 1e-5))[0]
    lo, hi = max(0, int(sichtbar.min()) - 1), min(len(kum) - 1, int(sichtbar.max()) + 2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ms[lo:hi + 1], y=kum[lo:hi + 1], mode="lines+markers", line=dict(color=C.COLOR_EXAKT, width=2, shape="hv"), marker=dict(size=7),
                             name="P(L ≤ m): Anteil der Folgen, die in m Stapeln liegen", hovertemplate="m = %{x}: %{y:.4f}<extra></extra>"))
    fig.add_hline(y=pl.q, line=dict(color="#c0504d", dash="dash"), annotation_text=f"Sicherheit {de_pct(pl.q)}", annotation_position="bottom right")
    fig.add_trace(go.Scatter(x=[pl.m], y=[pl.p_m], mode="markers", marker=dict(size=13, color=C.COLOR_LIS, symbol="diamond"), name=f"kleinste ausreichende Zahl: {pl.m} Stapel"))
    fig.update_xaxes(title_text="Zahl der Stapel m", range=[lo - 0.3, hi + 0.3], dtick=1 if hi - lo < 25 else None)
    fig.update_yaxes(title_text="Anteil der Folgen", range=[-0.02, 1.02])
    return _base(fig, height=340)


def de_pct(anteil: float) -> str:
    return ev.prozent(anteil, 1)


def build_verweilzeit(n: int, d_gewaehlt: int):
    """Mittlere Stapelzahl über der mittleren Verweilzeit D (logarithmisch) bei festem n, mit der gleichverteilten Folge (Modell U) als Waagerechte; vorgerechnet."""
    ds = list(C.V_D_WERTE)
    mes = [S.modell_v(n, d) for d in ds]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ds, y=[x.mittel for x in mes], mode="lines+markers", name="Modell V: mittlere Stapelzahl", line=dict(color=C.COLOR_KURVE, width=3),
                             error_y=dict(type="data", array=[x.fehler for x in mes], visible=True), hovertemplate="D = %{x}: %{y:.1f}<extra></extra>"))
    u = E.mittel(n) if n <= E.exakt_n_max() else S.modell_u_gemessen(n).mittel
    fig.add_hline(y=u, line=dict(color=C.COLOR_EXAKT, dash="dash"), annotation_text="gleichverteilte Folge (Modell U)", annotation_position="top left")
    i = ds.index(d_gewaehlt)
    fig.add_trace(go.Scatter(x=[d_gewaehlt], y=[mes[i].mittel], mode="markers", marker=dict(size=14, color=C.COLOR_LIS, symbol="diamond"), name=f"gewählt: D = {d_gewaehlt}"))
    fig.update_xaxes(title_text="mittlere Verweilzeit D in Ankunftsabständen (logarithmisch)", type="log")
    fig.update_yaxes(title_text="Stapel im Mittel", rangemode="tozero")
    return _base(fig, height=340)
