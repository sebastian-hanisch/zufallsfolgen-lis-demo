"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): n = 0, 1, 2, Identität, Umkehrfolge, Gleichstände, Grenzen inklusive, Mischungen = 0, q = 100 %."""

import pytest

import zfl_constants as C
import zfl_evaluation as ev
import zfl_exact as E
import zfl_lis as L
import zfl_sim as S
from zfl_rng import SplitMix64
from zfl_scenario import folge_modell_u, folge_modell_v, raenge_aus_verweilzeiten


def test_n_gleich_null_gibt_eine_meldung_statt_einer_zahl():
    for f in (L.lis_laenge, L.stapel_legen, L.lis_positionen, L.ein_stapel_sortiert):
        with pytest.raises(ValueError, match="leere Folge"):
            f([])
    for f in (E.verteilung, E.plancherel, E.aufzaehlung):
        with pytest.raises(ValueError):
            f(0)
    with pytest.raises(ValueError):
        folge_modell_u(0, SplitMix64(1))
    with pytest.raises(ValueError):
        folge_modell_v(0, 1.0, SplitMix64(1))
    with pytest.raises(ValueError):
        raenge_aus_verweilzeiten([])


def test_n_gleich_eins_und_zwei():
    assert L.stapel_legen([1]) == [[1]] and L.lis_laenge([1]) == 1
    assert E.verteilung(1).wahrscheinlichkeit[1] == 1.0 and E.kennzahlen(E.verteilung(1).wahrscheinlichkeit) == (1.0, 0.0, 0.0)
    assert L.stapel_legen([1, 2]) == [[1], [2]] and L.stapel_legen([2, 1]) == [[2, 1]]
    assert E.plancherel(2) == (0, 1, 1)                     # Folge 12 braucht 2 Stapel, Folge 21 braucht 1
    assert E.mittel(2) == 1.5


def test_identitaet_braucht_n_stapel_und_die_umkehrfolge_einen():
    for n in (1, 2, 7, 50):
        assert len(L.stapel_legen(list(range(1, n + 1)))) == n == L.lis_laenge(list(range(1, n + 1)))
        assert L.stapel_legen(list(range(n, 0, -1))) == [list(range(n, 0, -1))] and L.lis_laenge(list(range(n, 0, -1))) == 1
        assert L.lds_laenge(list(range(n, 0, -1))) == n


def test_gleichstaende_werden_mit_meldung_abgelehnt():
    for f in (L.lis_laenge, L.stapel_legen, L.lis_positionen, L.ein_stapel_sortiert, L.lds_laenge):
        with pytest.raises(ValueError, match="Gleichstände"):
            f([1, 2, 2, 3])


def test_unbekannte_regel_wird_abgelehnt():
    with pytest.raises(ValueError):
        L.stapel_legen([1, 2], "irgendeine")


def test_n150_ist_die_grenze_der_exakten_verteilung():
    assert E.exakt_n_max() == 150 and len(E.verteilung(150).wahrscheinlichkeit) == 51
    with pytest.raises(ValueError, match="150"):
        E.verteilung(151)


def test_mischungen_gleich_null_und_zu_grosse_rechnung():
    with pytest.raises(ValueError):
        S.simuliere(10, 0, 1)
    with pytest.raises(ValueError):
        S.messung_aus_haeufigkeit({})
    with pytest.raises(ValueError, match="höchstens"):
        ev.verteilungsvergleich(100, C.T_MAX + C.T_SCHRITT, 1)


def test_sicherheit_100_prozent_ist_nicht_zulaessig_und_nahe_100_geht():
    p = E.verteilung(10).wahrscheinlichkeit
    for q in (1.0, 0.0, -0.1, 1.5):
        with pytest.raises(ValueError, match="Sicherheit"):
            E.kleinstes_m(p, q)
    assert E.kleinstes_m(p, 0.999999) <= 10 and E.kleinstes_m(p, 0.001) >= 1
    with pytest.raises(ValueError):
        S.simuliere(5, 10, 1).kleinstes_m(1.0)


def test_reglergrenzen_inklusive():
    """Die Grenzen der Regler gelten inklusive: kleinstes und größtes n, T_MAX mit n = 100 ergibt genau die Live-Grenze."""
    assert C.N2_MAX * C.T_MAX == C.LIVE_PRODUKT_MAX
    for n in (C.N1_MIN, C.N1_MAX):
        assert ev.mischung(n, 1).n == n
    for n in (C.N5_MIN, C.N5_MAX):
        assert ev.planung(n, C.Q_MAX).m >= 1 and ev.planung(n, C.Q_MIN).m >= 1
    for n in (C.N3_MIN, C.N3_MAX):
        assert ev.naeherung(n).zwei_wurzel > ev.naeherung(n).exakt


def test_modell_v_ohne_positive_verweilzeit_wird_abgelehnt():
    for d in (0, -1.0):
        with pytest.raises(ValueError, match="Verweilzeit"):
            folge_modell_v(5, d, SplitMix64(1))


def test_modell_v_gleiche_abfahrtszeiten_werden_nach_der_ankunft_geordnet():
    """Wagen 1 (Verweilzeit 1) und Wagen 2 (Verweilzeit 0) fahren beide zur Zeit 2 ab: der frühere Wagen bekommt den kleineren Rang."""
    assert raenge_aus_verweilzeiten([1.0, 0.0]) == [1, 2]


def test_vorgerechnete_modell_v_gibt_bei_unbekanntem_n_oder_d_einen_schluesselfehler():
    with pytest.raises(KeyError):
        S.modell_v(50, 10)
    with pytest.raises(KeyError):
        S.modell_v(100, 3)
