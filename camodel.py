from math import sqrt
import numpy as np

g = 9.81
man = 0.03
delta_X = 1
tol = 0
A = 1
delta_t = 1
delta_e = 1

def update_D(L, D, I, m, n):
    ibabawas = np.zeros((m, n))
    idadagdag = np.zeros((m, n))
    print(L.shape, D.shape, I.shape)

    for i in range(m):
        for j in range(n):
            if ((i * m) + j) % 1000000 == 0:
                print(f'I am at cell[{i}][{j}]')
            
            central = L[i][j]
            neighbor_directory = dict()

            if (i - 1) >= 0:
                neighbor_directory["north"] = L[i-1][j]
            if (i + 1) < len(L):
                neighbor_directory["south"] = L[i+1][j]
            if (j + 1) < len(L[0]):
                neighbor_directory["east"] = L[i][j+1]
            if (j - 1) >= 0:
                neighbor_directory["west"] = L[i][j-1]
            
            delta_L = {i: central - neighbor_directory[i] for i in neighbor_directory}
            delta_V = {i: A * max(delta_L[i], 0) for i in delta_L}
            
            to_compute = [delta_V[i] for i in delta_V if delta_V[i] > tol]
            if len(to_compute) == 0:
                continue

            V_min = min(to_compute)
            V_max = max(to_compute)
            delta_Vs = [delta_V[i] for i in delta_V]
            V_total = sum(delta_Vs)

            weights = {i: delta_V[i]/(V_total + V_min) for i in delta_V}
            weights["central"] = V_min/(V_total + V_min)
            max_weight = max([weights[i] for i in weights if i != "central"])
            v_M = min(sqrt(D[i][j] * g), (1/man) * (D[i][j]**(2/3)) * sqrt((V_max/A)/delta_X))
            i_M = v_M * D[i][j] * delta_t * delta_e

            candidates = (D[i][j] * A, i_M/max_weight, V_min + I[i][j])
            to_distribute = min(candidates)
            #to_distribute = min(D[i][j] * A, i_M/max_weight, V_min + I[i][j])
            I_next = {i: weights[i] * to_distribute for i in weights if i != "central"}
            ibabawas[i][j] = sum([I_next[i] for i in I_next])
            I[i][j] = ibabawas[i][j]
        
            if "north" in I_next:
                idadagdag[i-1][j] += I_next["north"]
            if "south" in I_next:
                idadagdag[i+1][j] += I_next["south"]
            if "east" in I_next:
                idadagdag[i][j+1] += I_next["east"]
            if "west" in I_next:
                idadagdag[i][j-1] += I_next["west"]
            
    return I, ibabawas, idadagdag