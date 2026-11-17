"""Stapelregeln und längste wachsende Teilfolge (LIS) einer Ankunftsfolge.

Konvention: Jeder Container hat eine Abholrangzahl 1 bis n (Rang 1 wird zuerst geholt). Container-Stapel sind **fallend**: Ein Container darf nur auf einen
Stapel, dessen oberster Container einen größeren Rang hat (oben liegt der kleinste, er wird zuerst geholt). Beim verzögerten Einlagern (alle n Container
liegen zuerst, danach wird in Rangfolge geholt, ohne Umsetzen) ist die Mindestzahl Stapel die Länge der längsten wachsenden Teilfolge (LIS) der Rangfolge.

Gleichstände (gleiche Ränge) sind nicht unterstützt: ohne Gleichstände ist die Mindestzahl die LIS, mit Gleichständen ist sie es nicht mehr."""

import bisect

REGEL_ERSTER = "erster passender Stapel von links"
REGEL_GROESSTE = "größte passende Spitze (Gegenbeispiel)"
REGELN = (REGEL_ERSTER, REGEL_GROESSTE)


def pruefe_folge(folge) -> list:
    """Gibt die Folge als Liste zurück. Eine leere Folge und Gleichstände sind keine zulässige Eingabe (ValueError mit Meldung)."""
    liste = list(folge)
    if not liste:
        raise ValueError("Eine leere Folge braucht keinen Stapel: n muss mindestens 1 sein.")
    if len(set(liste)) != len(liste):
        raise ValueError("Gleichstände (gleiche Ränge) sind nicht unterstützt: die Mindestzahl Stapel ist dann nicht mehr die längste wachsende Teilfolge.")
    return liste


def lis_laenge(folge) -> int:
    """Länge der längsten streng wachsenden Teilfolge (Patience-Verfahren mit Bisektion, O(n log n))."""
    spitzen: list = []
    for x in pruefe_folge(folge):
        i = bisect.bisect_left(spitzen, x)
        if i == len(spitzen):
            spitzen.append(x)
        else:
            spitzen[i] = x
    return len(spitzen)


def lis_positionen(folge) -> list[int]:
    """Positionen (0-basiert) einer längsten wachsenden Teilfolge, über Rückverweise; bei mehreren gleich langen eine davon."""
    liste = pruefe_folge(folge)
    spitzen: list = []        # kleinster Endwert je Länge
    spitzen_pos: list[int] = []
    vorgaenger = [-1] * len(liste)
    for pos, x in enumerate(liste):
        i = bisect.bisect_left(spitzen, x)
        if i == len(spitzen):
            spitzen.append(x)
            spitzen_pos.append(pos)
        else:
            spitzen[i] = x
            spitzen_pos[i] = pos
        vorgaenger[pos] = spitzen_pos[i - 1] if i > 0 else -1
    kette = []
    pos = spitzen_pos[-1]
    while pos != -1:
        kette.append(pos)
        pos = vorgaenger[pos]
    return kette[::-1]


def lds_laenge(folge) -> int:
    """Länge der längsten fallenden Teilfolge (bei wachsenden Stapeln die Mindestzahl Stapel)."""
    return lis_laenge([-x for x in pruefe_folge(folge)])


def stapel_legen(folge, regel: str = REGEL_ERSTER) -> list[list]:
    """Legt die Folge in Ankunftsreihenfolge auf fallende Stapel (jeder Stapel von unten nach oben). `REGEL_ERSTER`: der erste Stapel von links, dessen Spitze größer
    ist, sonst ein neuer Stapel rechts; diese Regel legt genau LIS Stapel. `REGEL_GROESSTE`: unter den passenden Stapeln der mit der größten Spitze (Gegenbeispiel,
    braucht manchmal mehr Stapel als die LIS)."""
    if regel not in REGELN:
        raise ValueError(f"unbekannte Regel: {regel}")
    stapel: list[list] = []
    for x in pruefe_folge(folge):
        passend = [s for s in stapel if s[-1] > x]
        if not passend:
            stapel.append([x])
        elif regel == REGEL_ERSTER:
            passend[0].append(x)
        else:
            max(passend, key=lambda s: s[-1]).append(x)
    return stapel


def ein_stapel_sortiert(folge) -> bool:
    """Sofort ausgeben: jeden Container auf den einen Stapel legen und ausgeben, sobald der nächste fällige Rang oben liegt. Sortiert die Folge genau dann, wenn
    sie kein Muster 231 enthält (Eingabe, die ein Stapel sortiert). Ein anderes Ziel als die Mindestzahl Stapel beim verzögerten Einlagern."""
    liste = pruefe_folge(folge)
    rang_von = {x: i + 1 for i, x in enumerate(sorted(liste))}
    stapel: list = []
    naechster = 1
    for x in liste:
        stapel.append(x)
        while stapel and rang_von[stapel[-1]] == naechster:
            stapel.pop()
            naechster += 1
    return not stapel
