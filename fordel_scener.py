import argparse
from pulp import LpProblem, LpVariable, LpBinary, LpMaximize, lpSum, value
import pandas as pd


## Parse input arguments 
parser = argparse.ArgumentParser(description='Assign roles to actors')
parser.add_argument('--filename', default='mulige_roller.xlsx',
                            help='Name of file containing possible roles')
args = parser.parse_args()
filename = args.filename


## Import data from excel-file, assume it is structured as specified in README
filename = "mulige_roller.xlsx"
data = pd.read_excel(filename)
scenes = data.iloc[:, 0]
roles = data.iloc[:, 1]
scene_start_indices = [index for index, scene in enumerate(scenes.notnull()) if scene]

# Use m, n and t as compact notation for number of roles, actors and scenes, respectively
# Some ugly hacks, but nothing breaks down as long as the structure is as specified
(m, n) = data.shape
n -= 2
actors = data.columns[2:n+2].values
scenes = scenes.dropna().tolist()
t = len(scenes)


## Build python dictionaries from pandas dataframes
# Dictionary: Key = Role, Value = All actors that may play the role
possible_actors = {}
for i in range(0, m):
    possible_actor_indices = data.iloc[i, 2:] == 1
    possible_actors[roles[i]] = actors[possible_actor_indices]

# Dictionary: Key = Scene, Value = Coliumn indices of all roles in the scene 
scene_indices = {}
for s in range(0, t-1):
    scene_indices[scenes[s]] = range(scene_start_indices[s], scene_start_indices[s+1])
scene_indices[scenes[t-1]] = range(scene_start_indices[t-1], m)

scene_sizes = [len(scene_indices[scenes[i]]) for i in range(0, len(scenes))]

# Matrix on same format as decision variable, R[i, j] = 1 if actor j can play role i
R = {}
for i in range(0, m):
    for j in range(0, n):
        R[i, j] = int(actors[j] in possible_actors[roles[i]])


## State binary LP
# Decision variable
x = LpVariable.dicts('Rollefordeling', 
                        [(i, j) for i in range(0, m)
                                for j in range(0, n)],
                        0, 1, LpBinary)
prob = LpProblem('RoleDistribution', LpMaximize) 

# Maximize number of people who have a role
prob += lpSum(x[i, j] for i in range(0, m) for j in range(0, n))
# Only one role per person
for j in range(0, n):
    prob += lpSum(x[i, j] for i in range(0, m)) <= 1

# Only one person per role
for i in range(0, m):
    prob += lpSum(x[i, j] for j in range(0, n)) <= 1

# Each scene should either have all roles assigned, or none (meaning it is not included)
scene_included = LpVariable.dicts('SceneChoice', range(0, t), 0, 1, LpBinary)
for s in range(0, t):
    current_scene_indices = scene_indices[scenes[s]]
    prob += lpSum(x[i, j] for i in current_scene_indices for j in range(0, n)) == scene_included[s]*scene_sizes[s]

# Respect the excel sheet 
for i in range(0, m):
    for j in range(0, n):
        prob += x[i, j] <= R[i, j]

prob.solve()
objective_value = int(value(prob.objective))


## Print results
# Make bold print possible
BOLD = '\033[1m'
REGULAR = '\033[0m'

final_roles = {}
for i in range(0, m):
    for j in range(0, n):
        if x[i, j].varValue == 1:
            final_roles[actors[j]] = roles[i]

final_scenes = []
for s in range(0, t):
    if scene_included[s].varValue == 1:
     final_scenes.append(scenes[s])

print()
print(f"Ferdig med rollefordeling. Har funnet roller til {objective_value} skuespillere.")
print()

for scene in final_scenes:
    print("Scenen " + BOLD + scene + REGULAR + " er med.")

print()
for rolle in final_roles:
    print(BOLD + final_roles[rolle] + REGULAR + " spilles av " + BOLD + rolle + REGULAR  + ".")
print()
