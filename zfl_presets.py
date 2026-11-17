"""Permalink (Begrenzen), Schnellstart-Szenarien (Presets) und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio).

Die Regler stehen bei ihren Experimenten im Hauptbereich; jeder hat einen Eintrag in SETTING_SPECS, damit die Hervorhebung des aktiven Schnellstart-Szenarios
(`aktives_preset`) bei jeder Änderung eines Reglers erlischt (tests/test_layout.py prüft das für jeden Regler)."""

import random
from dataclasses import dataclass

import streamlit as st

import zfl_constants as C
import zfl_lis as L


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    step: float | None = None
    options: tuple | None = None      # Auswahlregler: erlaubte Werte (der Permalink speichert die laufende Nummer, bei Zahlen den Wert)


D = C.DEFAULTS
SETTING_SPECS = {
    "n1_slider": SettingSpec("n1", int, D["n1"], C.N1_MIN, C.N1_MAX),
    "seed_input": SettingSpec("seed", int, D["seed"], 0, C.SEED_MAX),
    "regel_select": SettingSpec("regel", str, D["regel"], options=L.REGELN),
    "n2_slider": SettingSpec("n2", int, D["n2"], C.N2_MIN, C.N2_MAX),
    "t_slider": SettingSpec("t", int, D["t"], C.T_MIN, C.T_MAX, C.T_SCHRITT),
    "n3_slider": SettingSpec("n3", int, D["n3"], C.N3_MIN, C.N3_MAX),
    "n4_slider": SettingSpec("n4", int, D["n4"], C.N4_MIN, C.N4_MAX),
    "shift_slider": SettingSpec("c", float, D["shift"], C.SHIFT_MIN, C.SHIFT_MAX, C.SHIFT_SCHRITT),
    "n5_slider": SettingSpec("n5", int, D["n5"], C.N5_MIN, C.N5_MAX),
    "q_slider": SettingSpec("q", float, D["q"], C.Q_MIN, C.Q_MAX, C.Q_SCHRITT),
    "nv_select": SettingSpec("nv", int, D["nv"], options=C.V_N_WERTE),
    "dv_select": SettingSpec("dv", int, D["dv"], options=C.V_D_WERTE),
}
PRESET_KEYS = {"n1": "n1_slider", "seed": "seed_input", "regel": "regel_select", "n2": "n2_slider", "t": "t_slider", "n3": "n3_slider", "n4": "n4_slider",
               "shift": "shift_slider", "n5": "n5_slider", "q": "q_slider", "nv": "nv_select", "dv": "dv_select"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def _aus_url(spec: SettingSpec, roh: str):
    """Wert aus der Adresszeile, auf die Reglergrenzen begrenzt und auf das Raster des Reglers gelegt; ungültig: None."""
    if spec.options is not None:
        try:
            wert = spec.options[int(roh)] if spec.caster is str else spec.caster(roh)
        except (ValueError, TypeError, IndexError):
            return None
        return wert if wert in spec.options else None
    try:
        wert = spec.caster(roh)
    except (ValueError, TypeError):
        return None
    if spec.lo is not None:
        wert = max(spec.lo, wert)
    if spec.hi is not None:
        wert = min(spec.hi, wert)
    if spec.step is not None and spec.lo is not None:
        wert = spec.lo + round((wert - spec.lo) / spec.step) * spec.step
        wert = spec.caster(round(wert, 6)) if spec.caster is float else spec.caster(wert)
        wert = max(spec.lo, min(spec.hi, wert))
    return wert


def _in_url(spec: SettingSpec, wert) -> str:
    if spec.options is not None and spec.caster is str:
        return str(spec.options.index(wert))
    return str(wert)


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            wert = _aus_url(spec, qp[spec.url_param])
            if wert is not None:
                st.session_state[state_key] = wert
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            spec = SETTING_SPECS[state_key]
            st.query_params[spec.url_param] = _in_url(spec, value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen Standardwert) mit dem Session State."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden (setzt die Regler der Experimente):")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
