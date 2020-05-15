# Her er en løsning på det klassiske "vi har øvelse i morgen men vi har fortsatt ikke fordelt
# roller, så nå må vi sitte oppe hele kvelden for å få alt til å gå opp"-problemet
# alle som har holdt på med revy kjenner til.

# TODO: Renskriv koden, den er fullstendig uleselig. Beklager til alle som måtte
#       kikke på det her. Jeg lover bot og bedring.

import argparse
from pulp import *
import pandas as pd

# Les argumenter scriptet er kalt med
parser = argparse.ArgumentParser(description='Fordel roller på skuespillere')
parser.add_argument('--filnavn', default='mulige_roller.xlsx',
                            help='Navn på fil som inneholder mulige roller')
args = parser.parse_args()
filename = args.filnavn

# Importer data fra excel-fil
# Antar at fila har sketsjnavn i venstre kolonne, tilhørende roller i kolonna til
# høyre for denne, og om en person kan spille denne rollen i hver kolonne til høyre
# for disse igjen. Sjekk fila for eksempel

filename = "mulige_roller.xlsx"
data = pd.read_excel(filename)
scenes = data.iloc[:, 0]
roles = data.iloc[:, 1]
scene_start_indices = [index for index, scene in enumerate(scenes.notnull()) if scene]

(m, n) = data.shape
n -= 2
actors = data.columns[2:n+2].values

possible_actors = {}
for i in range(0, m):
    possible_actor_indices = data.iloc[i, 2:] == 1
    possible_actors[roles[i]] = actors[possible_actor_indices]

scenes = scenes.dropna().tolist()
t = len(scenes)
# Hold oversikten over hvor de ulike scenen starter og slutter
scene_indices = {}
for s in range(0, t-1):
    scene_indices[scenes[s]] = range(scene_start_indices[s], scene_start_indices[s+1])
scene_indices[scenes[t-1]] = range(scene_start_indices[t-1], m)

# TODO: Vær konsekvent på språk, velg bedre variabelnavn
skuespillere = actors
roller = roles
mulige_roller = possible_actors 
scener = scenes
scener_indekser = scene_indices

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

objective_value = int(value(prob.objective))

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

print()
print(f"Ferdig med rollefordeling. Har funnet roller til {objective_value} skuespillere.")
print()

for scene in endelige_scener:
    print(f"Scenen {scene} er med")

print()
for rolle in endelige_roller:
    print(f"{endelige_roller[rolle]} spilles av {rolle}")
print()

