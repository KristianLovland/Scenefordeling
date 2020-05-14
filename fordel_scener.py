from pulp import *
import numpy as np
import pandas as pd

# TODO: Renskriv koden, den er fullstendig uleselig
# TODO: Importer data fra csv-fil

# Importer data fra csv-fil
# Antar at fila har sketsjnavn i venstre kolonne, tilhørende roller i kolonna til
# høyre for denne, og om en person kan spille denne rollen i hver kolonne til høyre
# for disse igjen. Sjekk fila for eksempel

filename = "mulige_roller.csv"
data = pd.read_csv(filename, sep=";")
scenes = data.iloc[:, 0]
scene_indices = [index for index, scene in enumerate(scenes.notnull()) if scene]
print(f"Indekser som inneholder en ny scene: {scene_indices}")



# Dette er litt av et stjernelag
skuespillere = ['Kriss', 'Eskil', 'Erling'];
roller = ['Gutt', 'Pirat', 'Hai', 'Bestefar', 'Nesoddengutt']
# Jobber med to sketsjer
#mulige_roller = {'Gutt': ['Kriss', 'Erling'], 'Pirat': ['Eskil'], 'Hai': ['Eskil', 'Erling'], 'Bestefar': ['Eskil', 'Erling'], 'Nesoddengutt': ['Kriss', 'Eskil']}
mulige_roller = {'Gutt': ['Kriss', 'Erling'], 'Pirat': ['Eskil'], 'Hai': ['Eskil', 'Erling'], 'Bestefar': ['Eskil', 'Erling'], 'Nesoddengutt': ['Kriss', 'Eskil'], 'Lærer': ['Kriss', 'Eskil', 'Erling']}

# Gutt og pirat er med i første sketsj, bestefar og Nesoddengutt er med i andre sketsj
scener = ['Hav til besvær', 'Ferja']
scener_indekser = {'Hav til besvær': [0, 1, 2], 'Ferja': [3, 4]}
scene_storleik = [len(scener_indekser[scener[i]]) for i in range(0, len(scener))]

# m er antall roller til sammen, n er antall skuespillere, t er antall scener
m = len(roller)
n = len(skuespillere)
t = len(scener)
R = {}
# Lag matrise der [i, j] = 1 hvis skuepiller j kan spille rolle i
for i in range(0, m):
    for j in range(0, n):
        R[i, j] = int(skuespillere[j] in mulige_roller[roller[i]])


# Formuler problem vha. PuLP
x = LpVariable.dicts('Rollefordeling', 
                        [(i, j) for i in range(0, m)
                                for j in range(0, n)],
                        0, 1, LpBinary)

prob = LpProblem('RoleDistribution', LpMaximize) 
# Legger til deler av formuleringen med den merkelige +=-indeksen

# Maksimér sysselsetting, dvs. sum av alle x
prob += lpSum(x[i, j] for i in range(0, m) for j in range(0, n))
# Kun én rolle per pers
for j in range(0, n):
    prob += lpSum(x[i, j] for i in range(0, m)) <= 1

# Kun én pers per rolle
for i in range(0, m):
    prob += lpSum(x[i, j] for j in range(0, n)) <= 1

# En scene er enten fylt eller ikke
scene_med = LpVariable.dicts('Scenevalg', range(0, t), 0, 1, LpBinary)
for s in range(0, t):
    scene_indekser = scener_indekser[scener[s]]
    prob += lpSum(x[i, j] for i in scene_indekser for j in range(0, n)) == scene_med[s]*scene_storleik[s]

# Det er begrenset hvem som kan spille hvilke roller
for i in range(0, m):
    for j in range(0, n):
        prob += x[i, j] <= R[i, j]

prob.solve()

# Print resultatene

endelige_roller = {}
for i in range(0, m):
    for j in range(0, n):
        #print(f"x[i, j]: {x[i, j].varValue}, R[i, j]: {R[i, j]}")
        if x[i, j].varValue == 1:
            endelige_roller[skuespillere[j]] = roller[i]

endelige_scener = []
for s in range(0, t):
    if scene_med[s].varValue == 1:
     endelige_scener.append(scener[s])


for rolle in endelige_roller:
    print(f"{endelige_roller[rolle]} spilles av {rolle}")

for scene in endelige_scener:
    print(f"Scenen {scene} er med")
