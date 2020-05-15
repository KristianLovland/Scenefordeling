# Fordeling av sketsjer til en gitt gruppe skuespillere
Dette scriptet leser inn et excelark som inneholder informasjon om hva slags sketsjer man ønsker å øve på, hvilke roller hver av disse sketsjene har, og hvilke skuespillere som kan passe til å spille hvilke roller. Dette oppgis i en tabell på følgende form (der Ri er rolle 1 og Pj er person j).

|           |           |  Person 1     | Person 2      | ... | Person n      |
| --------- | --------- | ------------- | ------------- | --- | --------      |
| Sketsj 1  | Rolle 1   | Kan P1 ha R1? | Kan P2 ha R1? | ... | Kan Pn ha R1? |
|           | Rolle 2   | Kan P1 ha R2? | Kan P2 ha R2? | ... | Kan Pn ha R2? |
| Sketsj 2  | Rolle 3   | Kan P1 ha R3? | Kan P2 ha R3? | ... | Kan Pn ha R3? |
|    ...    |    ...    |      ...      |      ...      | ... |       ...     |
| Sketsj t  | Rolle t   | Kan P1 ha Rt? | Kan P2 ha Rt? | ... | Kan Pn ha Rt? |

Kolonnen helt til venstre er tom med mindre rollen er den første som inngår i en ny sketsj (dvs. alle roller som er del av samme sketsj må skrives etter hverandre). [Et eksempel](mulige_roller.xlsx) ligger sammen med koden for scriptet. Dette tabellformatet passer godt overens med en form for betinget formatering som viser om en person kan ha en rolle eller ikke vha. fargelegging eller lignende.

## Løsningsmetode
Rollefordelingen løses som et lineært programmeringsproblem med binære beslutningsvariable, der målet er å maksimere antall personer som har noe å øve på, samtidig som ingen har mer enn én rolle, og alle roller i sketsjene som øves på er besatt.

## Avhengigheter
Scriptet er avhengig av `pandas` for å laste inn data fra regneark, og `pulp` for å løse optimeringsproblemet.

## Bruk
Scriptet brukes fra terminal.Den enkleste måten å bruke det på er å lagre en fil ved navn `mulige_roller.xlsx`. Scriptet kan da kjøres direkte ved å bruke `python fordel_scener.py`. Om man vil kjøre det på en fil med et annet navn, eller på en fil som ligger i en annen mappe, bruker man `python fordel_scener.py --filnavn path/til/fil`.

## Advarsel
Dette er knapt halvferdig kode, så stabil oppførsel kan neppe forventes.