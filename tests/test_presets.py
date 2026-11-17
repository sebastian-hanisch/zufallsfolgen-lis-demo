"""Presets (Schnellstart-Szenarien): Vollständigkeit, gültige Werte, Voreinstellung = Standardeinstellungen, jedes Preset hat eine Wirkung; Permalink begrenzt und rastet ein."""

import pytest

import zfl_constants as C
import zfl_evaluation as ev
import zfl_lis as L
import zfl_presets as P
from zfl_rng import SplitMix64


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_grenzen():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            if spec.options is not None:
                assert preset[key] in spec.options, (name, key)
            else:
                assert spec.lo <= preset[key] <= spec.hi, (name, key)
                if spec.step:
                    assert abs((preset[key] - spec.lo) / spec.step - round((preset[key] - spec.lo) / spec.step)) < 1e-9, (name, key)
        assert preset["n2"] * preset["t"] <= C.LIVE_PRODUKT_MAX, name


def test_default_preset_equals_the_default_settings():
    erstes = next(iter(C.PRESETS.values()))
    assert ev.Settings(**erstes) == ev.Settings()
    assert erstes == C.DEFAULTS


def test_jedes_preset_unterscheidet_sich_von_den_voreinstellungen_und_von_jedem_anderen():
    werte = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(werte)) == len(werte)


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert len({s.url_param for s in P.SETTING_SPECS.values()}) == len(P.SETTING_SPECS)


def test_handfolge_preset_erzeugt_die_handfolge():
    from zfl_scenario import folge_aus_zufalls_seed

    preset = C.PRESETS["Handfolge n = 6"]
    assert preset["n1"] == 6 and tuple(folge_aus_zufalls_seed(6, preset["seed"])) == C.HANDFOLGE == (1, 3, 6, 2, 5, 4)
    assert C.HANDFOLGE_SEED == 218
    assert preset["seed"] != C.DEFAULTS["seed"]


def test_preset_wirkung_je_preset_die_erwartete_kernaussage():
    """Je Preset die erwartete Zeile des ersten Verdikts bzw. der Verteilung: kein Preset ohne Wirkung meldet eine Wirkung."""
    hand = C.PRESETS["Handfolge n = 6"]
    assert ev.mischung(hand["n1"], hand["seed"]).lis == 3
    kleine = C.PRESETS["Handbeispiel n = 5, alle 120"]
    assert ev.verteilungsvergleich(kleine["n2"], kleine["t"], kleine["seed"]).exakt.haeufigkeiten[1:] == (1, 41, 61, 16, 1)
    bucht = C.PRESETS["Bucht n = 100"]
    assert ev.planung(bucht["n5"], bucht["q"]).m == 20                      # 20 Stapel für 95 % bei n = 100
    naeherung = C.PRESETS["Näherung bei n = 100"]
    assert round(100 * ev.naeherung(naeherung["n3"]).luecke_relativ, 1) == 19.5
    verweil = C.PRESETS["Verweilzeit D = 10, n = 100"]
    assert ev.verweilzeit(verweil["nv"], verweil["dv"], 95.0).verhaeltnis > 2.0
    skat = C.PRESETS["Skat-Blatt n = 52 (Voreinstellung)"]
    assert ev.planung(skat["n5"], skat["q"]).m == 14


def test_hand_seed_ist_der_kleinste_passende_zufalls_seed():
    for seed in range(1, C.HANDFOLGE_SEED):
        a = [1, 2, 3, 4, 5, 6]
        SplitMix64(seed).shuffle(a)
        assert tuple(a) != C.HANDFOLGE


def test_permalink_begrenzt_rastet_ein_und_lehnt_ungueltiges_ab():
    s = P.SETTING_SPECS
    assert P._aus_url(s["n1_slider"], "9999") == C.N1_MAX and P._aus_url(s["n1_slider"], "-3") == C.N1_MIN and P._aus_url(s["n1_slider"], "abc") is None
    assert P._aus_url(s["t_slider"], "150") == 100 and P._aus_url(s["t_slider"], "10001") == C.T_MAX
    assert P._aus_url(s["q_slider"], "99.95") == pytest.approx(99.9) and P._aus_url(s["q_slider"], "10") == C.Q_MIN
    assert P._aus_url(s["shift_slider"], "0.07") == pytest.approx(0.05) and P._aus_url(s["shift_slider"], "-5") == C.SHIFT_MIN
    assert P._aus_url(s["nv_select"], "400") == 400 and P._aus_url(s["nv_select"], "50") is None
    assert P._aus_url(s["dv_select"], "100000") == 100000 and P._aus_url(s["dv_select"], "3") is None
    assert P._aus_url(s["regel_select"], "1") == L.REGEL_GROESSTE and P._aus_url(s["regel_select"], "7") is None and P._aus_url(s["regel_select"], "x") is None
    assert P._in_url(s["regel_select"], L.REGEL_GROESSTE) == "1" and P._in_url(s["n1_slider"], 52) == "52"
