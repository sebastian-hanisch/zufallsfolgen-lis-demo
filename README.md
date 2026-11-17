# Zufallsfolgen: Wie viele Stapel braucht eine zufällige Ankunftsfolge? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-zufallsfolgen-lis-demo.streamlit.app/)** -->

Demo der Konzepte-Gruppe „Sortiermaschinen und Permutationen“ für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Gruppe fragt: **Welche Folgen schafft eine Maschine aus Stapeln und Warteschlangen, und wie viel Platz braucht eine Folge selbst?**
Diese Demo gehört zur zweiten Frage (Platz): Die Folge ist nicht eine gegebene und nicht alle n! Folgen eines kleinen n, sondern **zufällig** (alle Reihenfolgen gleich wahrscheinlich), n liegt **über der Aufzählbarkeitsgrenze**, und gefragt ist die **Verteilung** der Stapelzahl und ihre Näherung.
Nachbar-Demos: [stapel-sortieren-demo](https://github.com/sebastian-hanisch/stapel-sortieren-demo) (ein Stapel, der Container sofort ausgibt), [patience-stapel-demo](https://github.com/sebastian-hanisch/patience-stapel-demo) (die Stapelregel und die Gleichheit mit der längsten wachsenden Teilfolge),
[erdos-szekeres-demo](https://github.com/sebastian-hanisch/erdos-szekeres-demo) (Schärfe des Satzes von Erdős und Szekeres), [tableaux-rsk-demo](https://github.com/sebastian-hanisch/tableaux-rsk-demo) (die Bijektion hinter der Plancherel-Summe) und
[sortierbar-umstauen-demo](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) (was die Stapelzahl für das Umstauen aussagt); Patience mit Gleichständen und einer Route als Beispiel zeigt [mehrhafenstau-demo](https://github.com/sebastian-hanisch/mehrhafenstau-demo), andere Statistiken von Permutationen (Abstiege, Inversionen, Zyklen)
[zaehlen-nach-parameter-demo](https://github.com/sebastian-hanisch/zaehlen-nach-parameter-demo). Das Beispiel ist **ausgedacht: ein Modell und kein Fall.** Die Folgen sind gleichverteilt oder haben eine gesetzte Verweilzeit; gemessene Ankunftsfolgen eines Hafens oder Bahnhofs liegen uns nicht vor.

## Warum dieses Problem

Wer Container in Stapeln lagert, die nur von oben erreichbar sind, und erst abholt, wenn alle da sind, braucht für eine Ankunftsfolge mindestens so viele Stapel, wie die **längste wachsende Teilfolge** (LIS) der Abholränge lang ist. Für eine **zufällige** Folge gibt es zwei geläufige Antworten: „etwa 2√n“ (eine Aussage für sehr große n) und
die exakte Verteilung. Die Demo zeigt beide nebeneinander. Kernfragen: (1) Wie viele Stapel braucht eine zufällige Folge? (2) Wie gut ist die Formel 2√n bei Demo-Größen? (3) Wie viele Stapel muss man einplanen, und was ändert eine kurze Verweilzeit der Wagen? **Neu im wissenschaftlichen Sinn ist nichts davon**: LIS, Plancherel-Summe, Gessel-Formel und die Tracy-Widom-Grenzverteilung
sind Lehrbuchstoff; neu ist nur die Vorführbarkeit mit Zähleinheiten und die gemessenen Abstände bei Demo-Größen.

## Modell

**Konvention.** Jeder Container hat eine **Abholrangzahl** 1 bis n (1 wird zuerst geholt); die Ankunftsfolge ist eine Folge dieser Ränge. **Container-Stapel sind fallend**: ein Container darf nur auf einen Stapel, dessen oberster Container einen größeren Rang hat (oben liegt der kleinste, er wird zuerst geholt). **Verzögertes Einlagern** heißt: alle n Container werden erst eingelagert und danach in Rangfolge geholt, ohne Umsetzen.
Dann ist die **Mindestzahl Stapel L = Länge der längsten wachsenden Teilfolge**; bei wachsenden Stapeln wäre es die längste fallende (LDS), die dieselbe Verteilung hat. Die Regel „erster passender Stapel von links“ legt genau L Stapel (für alle Folgen mit n ≤ 8 nachgezählt, n = 9 im Test; `tests/test_algorithm.py`). „Sofort ausgeben“ (die Maschine gibt jeden Rang aus, sobald er oben liegt) ist ein **anderes Ziel** mit anderen Stapelzahlen (B11).
**Zwei Stapel kommen in dieser Demo nicht vor.**

**Modell U** (gleichverteilt): alle n! Folgen mit paarweise verschiedenen Rängen gleich wahrscheinlich. Zähleinheit: **Folgen** (wo exakt gerechnet) oder **Zufallsfolgen** (wo gezogen).
**Modell V** (Verweilzeit D, ausgedacht): Wagen i kommt zur Zeit i, bleibt eine Exp-verteilte Zeit mit Mittel D (in Ankunftsabständen), Abfahrtszeit = i + Verweilzeit, der Rang ist der Rang der Abfahrtszeit. D steuert von fast sortiert (D klein) bis Modell U (D sehr groß). Es zählt nur die Rangfolge der Abfahrten.
**Gleichstände** (Wagen mit Zielgruppen) sind **nicht gemessen**; der Kern lehnt Folgen mit gleichen Rängen mit einer Meldung ab, weil die Mindestzahl dann nicht mehr die längste streng wachsende Teilfolge ist.

| Begriff | Bedeutung |
|---|---|
| L_n | Mindestzahl fallender Stapel (verzögertes Einlagern) = LIS einer Folge der Länge n |
| Plancherel-Summe | P(L = k) = Summe der f² über alle Formen mit erster Zeile k, geteilt durch n!; f nach der Hakenformel |
| Gessel-Rekursion | exakte Zahl der Folgen mit L ≤ k aus einer Determinante von Besselfunktionen, in Brüchen gerechnet (nur im Werkzeug, nach Gedächtnis, gegen Aufzählung und Plancherel-Summe bestätigt) |
| Rest | exaktes Mittel minus (2√n − 1,7711·n^(1/6)) |
| Rest nach Abzug von ½ | der Rest minus 0,5 (ein halber Stapel passt zur Ganzzahligkeit der Stapelzahl, B6) |
| Kolmogorov-Abstand | größter Abstand zwischen P(L ≤ k) und F₂ **nur an den ganzen k** |
| Schnellstart-Szenario (Preset) | ein Knopf in der Seitenleiste, der die Regler der Experimente setzt |

Die Formeln stehen im 📐-Expander der App, beginnend mit einer Lesehilfe.

## Methodik

- **Verteilung exakt (Zähleinheit Folgen):** bis n = 8 durch **Aufzählung** aller n! Folgen, bis n = 30 live aus der **Plancherel-Summe** (alle Partitionen von n, Hakenformel, ganze Zahlen), für n = 1 bis 150 aus einer **vorgerechneten Tabelle** (`data/zfl_exakt.json`, Werkzeug `tools/zfl_make_exakt.py` mit `--check`, rund 20 Sekunden): die Gessel-Rekursion in exakten Brüchen. Die Tabelle enthält P(L = k) als ganze Zahl durch n! (Python rundet diese Division korrekt, die Zahlen sind auf jeder Plattform dieselben Bits) für k bis 50; für n über 50 steht der abgeschnittene Rest (L > 50) dabei und liegt unter der Markow-Schranke C(n, 51)/51!.
- **Simulation (Zähleinheit Zufallsfolgen):** Fisher-Yates mit SplitMix64 (`zfl_rng.py`, Kopie der geprüften Vorlage; `below` ist der Rest der Division, Fehler höchstens n·2⁻⁶⁴), LIS durch Bisektion. Live bis n × Mischungen = 1 Million (Experiment 2). Große n (200 bis 10 000, Modell U) und Modell V sind **vorgerechnet** (`data/zfl_sim.json`, Werkzeug `tools/zfl_make_sim.py` mit `--check`, rund zwei Minuten) und in der App als „vorgerechnet“ gekennzeichnet.
- **Modell V:** je Folge werden die Exp(1)-Zahlen einmal gezogen und für alle D mit D·e skaliert (gleiche Zufallszahlen für alle D, das gibt glatte Kurven); das ist bitgleich zur direkten Ziehung mit Mittel D. n = 20, 100, 400 und 1000, 14 Werte von D von 1 bis 100 000 Ankunftsabständen.
- **Tracy-Widom-Kurve:** F₂ als Fredholm-Determinante des Airy-Kerns (Gauß-Legendre, 110 Knoten) auf dem Gitter −10 bis 8 in Schritten von 0,01, vorgerechnet (`data/zfl_tw.json`, `tools/zfl_make_tw.py`); die App braucht nur numpy.
- **Zufall:** nur ganzzahliger SplitMix64, nie `hash()` und nie `numpy.random`; der Zufalls-Seed der Mischung ist einstellbar und im Permalink (nur der Knopf „Neue Mischung würfeln“ wählt den Zufalls-Seed mit Pythons `random`, alles Weitere folgt aus dem Zufalls-Seed).
- **Rechenzeit** (Messung auf einem Windows-Entwicklungsrechner, kein Test): n × Mischungen = 1 Million etwa eine Sekunde; Seite etwa 9 700 Pixel lang bei 1 300 Pixel Breite.

## Befunde (gemessen, keine Behauptungen)

Zähleinheit: **Folgen** (exakt) oder **Zufallsfolgen** (Simulation, mit Zahl der Mischungen); Modell U, wenn nicht anders genannt.

| Nr | Frage | Befund | Test |
|---|---|---|---|
| B1 | Handfolge n = 6 | Die Folge 1 3 6 2 5 4 gibt die Stapel [1], [3, 2], [6, 5, 4], drei Stapel = LIS; die Regel „größte passende Spitze“ braucht vier | `test_b1_handfolge_drei_stapel` |
| B2 | Alle Folgen n = 5 und n = 9 | n = 5: 1, 41, 61, 16 und 1 von 120 Folgen brauchen 1 bis 5 Stapel; Mittel 67/24 = 2,792, Streuung 0,706. n = 9 (362 880 Folgen): 1, 4861, 89 497, 167 449, 83 029, 16 465, 1513, 64 und 1 | `test_b2_n5_alle_120_folgen`, `test_b2_n9_alle_362880_folgen` |
| B3 | Drei Rechenwege | Aufzählung gleich Plancherel-Summe (n ≤ 8, n = 9 im Test); Plancherel-Summe gleich der Tabelle bitgleich (n ≤ 30); Rest der Tabelle (L > 50) höchstens 5,3·10⁻²⁸ (n = 150), Markow-Schranke 2,5·10⁻²⁶ | `test_b3_aufzaehlung_plancherel_und_tabelle` |
| B4 | Mittel und Streuung (exakt) | n = 5 / 10 / 20 / 52 / 100 / 150: Mittel 2,792 / 4,335 / 6,615 / 11,566 / 16,738 / 20,960; Streuung 0,706 / 0,894 / 1,098 / 1,407 / 1,640 / 1,794 | `test_b4_mittel_und_streuung_exakt` |
| B5 | Wie weit liegt 2√n über dem Mittel? | exakt: +60,2 % (n = 5), +45,9 % (10), +35,2 % (20), +24,7 % (52), +19,5 % (100), +16,9 % (150); die Lücke in Stapeln wächst für n = 1 bis 150 mit n (3,26 bei n = 100, 3,53 bei n = 150). Simulation (vorgerechnet): +15,3 % (n = 200, 20 000 Zufallsfolgen), +8,6 % (n = 1000, 3000), +4,1 % (n = 10 000, 600); die Lücke ist dort 5,01 ± 0,05 (n = 1000) und 7,81 ± 0,17 Stapel (n = 10 000) | `test_b5_zwei_wurzel_n_liegt_darueber_exakt_bis_n150`, `test_b5_zwei_wurzel_n_gegen_vorgerechnete_simulation_n200_bis_10000` |
| B6 | Schließt die Korrektur 2√n − 1,7711·n^(1/6) die Lücke? | Zum größten Teil, aber nicht ganz: bei n = 100 sinkt die Lücke von 3,26 auf 0,55 Stapel, es bleibt etwa ein halber Stapel. Rest +0,636 (n = 5), +0,589 (20), +0,566 (52), +0,554 (100), +0,548 (150); nach Abzug von ½ bleiben +0,136, +0,089, +0,066 (n = 52), +0,054, +0,048; ein Abfall etwa wie n^(−0,30) (nur aus n = 20 und n = 150 gerechnet, kein Beweis); bei n = 100 gibt die Korrektur 16,18 und mit ½ 16,68 gegen exakt 16,74. In der Simulation (n = 200 bis 10 000) liegen die Punktwerte des Rests zwischen 0,42 und 0,59; die Standardfehler wachsen bis ± 0,11 (n = 5000) und ± 0,17 (n = 10 000) und sind dort so groß wie die Bandbreite | `test_b6_rest_zur_korrektur_und_nach_abzug_von_einhalb`, `test_b6_rest_aus_der_vorgerechneten_simulation_liegt_bei_0_4_bis_0_6` |
| B7 | Welcher Vorfaktor? | Aldous/Diaconis nennen nach Quellenbericht 1,711 (nicht im Original geprüft), Baik/Deift/Johansson und Bornemann 1,7711 (verbindlich); die Werte sind verschieden. n = 52: 11,12 gegen 11,00, exakt 11,57 | `test_b7_vorfaktor_1_711_gegen_1_7711_bei_n52` |
| B8 | Streuung, Schiefe, Form | n = 100 / 150: Streuung 84,4 % / 86,3 % des Grenzwerts 0,9018·n^(1/6); Schiefe 0,326 / 0,315 gegen 0,224 (Tracy-Widom, eigene Rechnung 0,2241). Kolmogorov-Abstand an den ganzen k: 0,139 (n = 10), 0,108 (20), 0,068 (52), 0,055 (100), 0,047 (150); mit der besten Verschiebung c (Gitter 0,01) 0,101 / 0,080 / 0,055 / 0,046 / 0,039 bei c = −0,15 / −0,13 / −0,10 / −0,09 / −0,07 | `test_b8_streuung_schiefe_und_kolmogorov_abstand` |
| B9 | Wie viele Stapel einplanen? | Kleinste Zahl für 50 / 90 / 95 / 99 / 99,9 % der Folgen: n = 10: 4 / 5 / 6 / 7 / 7; n = 20: 7 / 8 / 8 / 9 / 10; n = 52: 11 / 13 / 14 / 15 / 17; n = 100: 17 / 19 / 20 / 21 / 23. Zwei Stapel reichen bei n = 10 in 0,46 % (Catalan(10) = 16 796 von 3 628 800), drei in 16,2 %, vier in 60,4 %; bei n = 20 reichen vier in 1,09 %, bei n = 52 in 1,4·10⁻¹⁶ | `test_b9_stapelzahl_fuer_sicherheit`, `test_b9_wenige_stapel_reichen_fast_nie` |
| B10 | Kurze Verweilzeit (Modell V, vorgerechnet) | n = 100, D = 10 (4000 Zufallsfolgen): 40,1 ± 0,04 Stapel statt 16,7 bei gleichverteilter Folge (das 2,4-Fache), 2,5 Container je Stapel. Bei D = n liegt das Mittel noch das 1,20-Fache (n = 20), 1,24-Fache (100) und 1,27-Fache (1000) über Modell U, bei D = 5n das 1,04- bis 1,05-Fache, erst bei D = 10n unter 1,03 (1,018 / 1,023 / 1,026). Bei D = 1 liegt L/n bei 0,81 bis 0,82 (n = 20 bis 1000) | `test_b10_modell_v_n100_d10_und_container_je_stapel`, `test_b10_bei_d_gleich_n_noch_20_bis_27_prozent_ueber_modell_u`, `test_b10_erst_bei_d_gleich_10_n_unter_3_prozent`, `test_b10_bei_d_gleich_1_liegt_l_durch_n_bei_0_81_bis_0_82` |
| B11 | „Sofort“ gegen „verzögert“, n = 10 (Modell V, vorgerechnet, je 20 000 Zufallsfolgen) | D = 0,5: ein Stapel sortiert 99,7 % der Folgen sofort, verzögert braucht man 9,4 Stapel im Mittel; gleichverteilt sortiert ein Stapel 0,42 % (exakt 0,46 %, innerhalb von vier Standardfehlern), verzögert 4,3 Stapel | `test_b11_sofort_gegen_verzoegert_bei_n10` |
| B12 | Gegenregel „größte passende Spitze“ | Bei n = 8 braucht sie in 14 993 von 40 320 Folgen (37,2 %) mehr Stapel als die LIS | `test_b12_gegenregel_braucht_bei_n8_in_37_2_prozent_der_folgen_mehr_stapel` |
| B13 | Zufallsgenerator | n = 4, 48 000 Mischungen mit dem Zufalls-Seed 20261117: alle 24 Anordnungen, Chi-Quadrat 24,5 bei 23 Freiheitsgraden (Grenze für p = 0,001: 49,7) | `test_b13_alle_24_anordnungen_bei_n4_chi_quadrat_24_5` |

Jede Zahl dieser Tabelle wird vom Test der letzten Spalte nachgerechnet. **Nicht im Test, nur Messung dieser README:** die Rechenzeit und die Seitenlänge (oben); die Gegenprobe gegen die zehntausend Skat-Mischungen aus Tabelle 1 von Aldous und Diaconis 1999 (nach einem Quellenbericht): in einer früheren Rechnung außerhalb dieses Repos waren sie mit der exakten Verteilung für n = 52
verträglich (Chi-Quadrat 8,79 bei 9 Freiheitsgraden, p = 0,46; Mittel der Tabelle 11,546 gegen exakt 11,566). Die Tabelle selbst steht nicht im Repo (Weitergabe-Vermerk der Quelle), die Gegenprobe ist daher hier nicht nachrechenbar. Gleitkommazahlen sind auf die genannten Stellen gerundet verglichen; die Simulationszahlen stehen als Häufigkeiten in `data/zfl_sim.json`
und werden von `tests/test_daten.py` bitgleich neu gerechnet (n = 20 im schnellen Test, `u200`, `v100` und `sofort` im langsamen, alle Blöcke mit `tools/zfl_make_sim.py --check`).

## Befunde und Korrekturen gegenüber früheren Messungen

- **„2√n braucht D ≳ n“ ist nicht bestätigt** (eine frühere Annahme, nicht gemessen): bei D = n liegt das Mittel noch 20 bis 27 % über Modell U; erst ab D = 10n unter 3 % (B10). Gilt für dieses ausgedachte Modell mit Exp-Verweilzeit, nicht für echte Verweilzeiten.
- **Der Rest zur Korrektur ist nicht „unerklärt“ und nicht konstant:** ein halber Stapel (etwa 80 bis 90 % des Rests) passt zur Ganzzahligkeit der Stapelzahl (als Ursache eine Deutung, nicht gemessen und nicht bewiesen), der übrige Rest nach Abzug von ½ fällt von +0,136 (n = 5) auf +0,048 (n = 150); in einer früheren Simulation sah er konstant aus (B6).
- **n = 100 ist jetzt exakt statt simuliert:** 16,738 gegen früher 16,736 ± 0,007 (60 000 Zufallsfolgen); Streuung 1,640 gegen früher 1,638.
- **Neue Simulationen mit anderen Zufalls-Seeds:** n = 1000: +8,6 % statt früher 8,8 %, n = 10 000: +4,1 % statt 4,0 % (B5); n = 100, D = 10: 40,1 statt früher 40,2 (B10); „sofort“ bei D = 0,5: 99,7 % statt früher 99,4 % (B11). Die Unterschiede sind klein (höchstens 0,3 Prozentpunkte und 0,1 Stapel); ob sie über der Stichprobenschwankung liegen, ist nicht geprüft.
- **Modell V mit gemeinsamen Zufallszahlen für alle D:** die Tabelle wird dadurch glatt; sie ist eine neue Messung mit anderen Zufalls-Seeds als die frühere.
- **Grenzen der Regler:** die Zahl der Mischungen in Experiment 2 endet bei 10 000 (n × Mischungen höchstens 1 Million, sonst über zwei Sekunden Rechenzeit), und die Mischung in Experiment 1 geht bis n = 150 (so weit gibt es die exakte Vergleichsverteilung).

## Ehrliche Grenzen

- **Modell, kein Fall.** Alle Folgen sind ausgedacht; es gibt keine gemessene Ankunftsfolge. Modell V kennt nur Exp-verteilte Verweilzeiten (gleichverteilte oder Gamma-Verweilzeiten nicht gemessen); n = 1000 hat nur 800 Zufallsfolgen je D (Standardfehler 0,09 bis 0,38 Stapel); das Verhältnis zu Modell U ist ein Verhältnis zweier Mittel, nicht das Mittel der Verhältnisse.
- **n über 150 nur Simulation.** Die exakte Verteilung gibt es bis n = 150; für n von 51 bis 150 gibt es in diesem Repo **keinen zweiten exakten Weg** neben der Gessel-Rekursion (die Plancherel-Summe wäre bei n = 100 über 190 Millionen Formen); es stützen nur die Markow-Schranke für den Rest und die Simulation (B3, B4). Die Gleichheit mit der Plancherel-Summe gilt in den Tests für n ≤ 30 (live) und für n ≤ 40 mit k ≤ 20 (Rekursion neu gerechnet); eine frühere Rechnung außerhalb des Repos bestätigte n ≤ 40 und n = 52 für alle k.
- **Gessel-Formel und Rekursion** stehen nach Gedächtnis (die Originalarbeit ist nicht gelesen) und gelten hier nur, soweit Aufzählung und Plancherel-Summe sie bestätigen; für größere n ist das eine Prüfung der Rekursion, kein Beweis.
- **Der Kolmogorov-Abstand** ist nur an den ganzen k gerechnet; ein Vergleich mit der Dichte (Verschiebung, Stetigkeitskorrektur) ist nicht gemacht. Der Abfall des Rests wie n^(−0,30) ist aus zwei Punkten gerechnet.
- **„Sofort“ gegen „verzögert“** ist nur für n = 10 und Modell V gemessen, mit der Maschine „ein Stapel sofort“; die Mindestzahl paralleler Stapel „sofort“ (Graphfärbung über alle Folgen) ist nicht gerechnet.
- **Gleichstände, begrenzte Stapelhöhe und echte Ankunftsfolgen** sind nicht gemessen. Bei begrenzter Höhe ist die Mindestzahl nicht mehr die LIS.
- **Plattform:** gerechnet auf Windows (Python 3.14); Ganzzahlen und Tabellen sind plattformfest, Gleitkommazahlen (Mittel, Streuung, Tracy-Widom) als Band geprüft. Der Linux-Container (Python 3.12) hat alle Tests bestanden (siehe Verifikation); Windows und Linux sind die einzigen geprüften Plattformen.
- **Nicht mit echtem Mausklick getestet:** Regler, Auswahlfelder und Schnellstart-Knöpfe sind mit AppTest durchgespielt; im Browser-Fenster wurde die Seite gelesen und ein Schnellstart-Knopf per Skript ausgelöst, nicht mit einem Mausklick und nicht auf einem Telefon.

## Quellen

Aldous und Diaconis 1999 (Lemma 1 zur Stapelzahl, Mittelwertformel, Tabellen 1 und 2) und Baik, Deift und Johansson 1999 (Satz 1.1 und sein Folgesatz: Konvergenz in Verteilung und der Momente, Konstanten −1,7711 und 0,8132) sind nach einem Quellenbericht im Wortlaut geprüft, die **Beweise der Sätze nicht gelesen**; Bornemann, arXiv 2301.02022 (Konstanten): Auszug im Wortlaut.
**Nicht gelesen:** Hammersley 1972, Logan und Shepp 1977, Vershik und Kerov 1977, Ulam 1961 und Gessel 1990. Die Hakenformel und die Plancherel-Summe sind Lehrbuchstoff (Robinson, Schensted, Knuth); die Tabelle der Skat-Mischungen steht nicht im Repo.

## Verifikation

- **Kern:** Stapelregel und LIS gegen Handrechnung, gegen eine Doppelschleife und gegen die Aufzählung aller Mengenpartitionen (n ≤ 6 vollständig, n = 7 an 40 Folgen); Randfälle (n = 0, 1, 2, Identität, Umkehrfolge, Gleichstände, q = 100 %).
- **Orakel** (`tests/test_oracle_zufallsfolgen_lis.py`): Verteilung durch Aufzählung (eigene Doppelschleife), Plancherel-Summe, eingefrorene Tabelle und neu gerechnete Gessel-Rekursion; Markow-Schranke; Simulation gegen exaktes Mittel und exakte Verteilung (vier Standardfehler); Tracy-Widom aus eigener Fredholm-Rechnung (`scipy`, nur in den Tests, `requirements-dev.txt`).
- **Eigenschaften** (`tests/test_eigenschaften_zufallsfolgen_lis.py`): LIS gleich der LIS der inversen Folge, LIS der Umkehrfolge = LDS, Weglassen eines Elements ändert L um 0 oder 1, Mittelzuwachs in (0, 1], P(L ≤ k) wächst in k und fällt in n, höchstens zwei Stapel = Catalan(n)/n!, Modell V ist eine Permutation und verschiebungsfest.
- **Claims** (`tests/test_claims.py`): jede Zahl der Befundtabelle; **Verdikte** (`tests/test_verdicts.py`): jede Zahl im Text und jede Schwelle an handgesetzten Werten; **Daten** (`tests/test_daten.py`): Aufbau der Dateien und Neu-Rechnen mit den Werkzeugen.
- **Oberfläche:** AppTest (jeder Knopf, jeder Regler am Minimum und Maximum, jede Option der Auswahlfelder, größte Live-Rechnung), Layout und Hervorhebung des Schnellstart-Szenarios (`tests/test_layout.py`), Footer, Laufzeit-Importe.
- **Linux:** alle 167 Tests (auch die als `slow` markierten) bestehen im Linux-Container (Docker, Python 3.12, frische Installation aus `requirements-dev.txt`), 67,8 s Testzeit; die Simulationshäufigkeiten (Block n = 20), die Gessel-Tabelle (neu gerechnet) und die Tracy-Widom-Kurve stimmen dort mit den Dateien überein.
- **Testzahl:** 167 Tests (`pytest --collect-only -q tests`), davon einige als `slow` markiert (`pytest -m "not slow"` lässt sie aus).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis (Experiment 1), Kernfragen, Experimente 2 bis 5, Grenzen, Formeln |
| `data/zfl_exakt.json` | vorgerechnete exakte Verteilung n = 1 bis 150 (Gessel-Rekursion) |
| `data/zfl_sim.json` | vorgerechnete Simulationen: große n (Modell U), Modell V, „sofort“ bei n = 10 |
| `data/zfl_tw.json` | vorgerechnete Tracy-Widom-Kurve |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (nur Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tools/zfl_make_exakt.py`, `tools/zfl_make_sim.py`, `tools/zfl_make_tw.py` | Werkzeuge, die die Dateien in `data/` erzeugen (mit `--check`) |
| `zfl_constants.py` | Regler-Grenzen, Quellenkonstanten, Farben, Schnellstart-Szenarien |
| `zfl_lis.py` | Stapelregeln, LIS, LDS, „ein Stapel sofort“ |
| `zfl_exact.py` | Aufzählung, Plancherel-Summe, Zugriff auf die Tabelle, Kennzahlen, Quantile |
| `zfl_sim.py` | Simulation und vorgerechnete Messungen |
| `zfl_scenario.py` | Ankunftsmodelle U und V |
| `zfl_tw.py` | Tracy-Widom-Kurve, Kolmogorov-Abstand |
| `zfl_evaluation.py` | Kennzahlen und Verdikte (reine Funktionen) |
| `zfl_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `zfl_layout.py` | Fester Kopf (Stylesheet) |
| `zfl_presets.py` | Permalink, Schnellstart-Szenarien (aktives Szenario hervorgehoben), Zufalls-Seed-Button |
| `zfl_rng.py` | SplitMix64 (Kopie der geprüften Vorlage) |
| `tests/` | Handbeispiele, Orakel, Eigenschaften, Claims, Verdikte, Daten, Randfälle, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **PDF-Export:** die Demo hat keinen; die Ergebnisse stehen als Tabellen und Texte auf der Seite.
- **Gleichstände (Zielgruppen), begrenzte Stapelhöhe, gleichverteilte oder Gamma-Verweilzeiten, echte Ankunftsfolgen:** nicht gemessen (siehe Ehrliche Grenzen).
- **Exakte Verteilung für n über 150:** die Rechnung wächst weiter; es bleibt bei der vorgerechneten Simulation (n bis 10 000).
- **Eine Herleitung der Grenzverteilung und der Gessel-Formel:** die Demo zählt und misst, sie beweist nichts.
- **Mehr Zählaussagen über Muster-Klassen und das Wachstum von Zählfolgen:** dafür verweist die Demo auf die Abzähl-Demos des Portfolios.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
