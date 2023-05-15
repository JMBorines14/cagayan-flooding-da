from numba import cuda
import numpy as np
from math import sqrt, ceil

g = 9.81
man = 0.03
delta_X = 1
tol = 0
A = 1
delta_t = 600
delta_e = 1

@cuda.jit
def update_central(L, D, I, ibabawas, idadagdag):
    x, y = cuda.grid(2)
    central = L[x, y]

    neighbor_directory = dict()
    if (x - 1) >= 0:
        neighbor_directory["north"] = L[x-1, y]
    if (x + 1) < len(L):
        neighbor_directory["south"] = L[x+1, y]
    if (y + 1) < len(L[0]):
        neighbor_directory["east"] = L[x, y+1]
    if (y - 1) >= 0:
        neighbor_directory["west"] = L[x, y-1]
    
    delta_L = {i: central - neighbor_directory[i] for i in neighbor_directory}
    delta_V = {i: A * max(delta_L[i], 0) for i in delta_L}
    
    to_compute = [delta_V[i] for i in delta_V if delta_V[i] > tol]
    
    if len(to_compute) > 0:
        V_min = min(to_compute)
        delta_Vs = [delta_V[i] for i in delta_V]
        V_total = sum(delta_Vs)

        weights = {i: delta_V[i]/(V_total + V_min) for i in delta_V}
        weights["central"] = V_min/(V_total + V_min)
        max_weight = max([weights[i] for i in weights])
        v_M = min(D[x, y] * g, (1/man) * (D[x, y]**(2/3)) * sqrt(max_weight/delta_X))
        i_M = v_M * D[x, y] * delta_t * delta_e

        to_distribute = min(D[x, y] * A, i_M/max_weight, V_min + I[x, y])
        I[x, y] = to_distribute

        I_next = {i: weights[i] * to_distribute for i in weights if i != "central"}
        ibabawas[x, y] = sum([I_next[i] for i in I_next])

        if "north" in I_next:
            idadagdag[x-1, y] += I_next["north"]
        if "south" in I_next:
            idadagdag[x+1, y] += I_next["south"]
        if "east" in I_next:
            idadagdag[x, y+1] += I_next["east"]
        if "west" in I_next:
            idadagdag[x, y-1] += I_next["west"]

def update_D(L, D, I):
    ibabawas = np.array([[0. for _ in range(len(L[0]))] for _ in range(len(L))])
    idadagdag = np.array([[0. for _ in range(len(L[0]))] for _ in range(len(L))])

    gpu_L = cuda.to_device(L)
    gpu_D = cuda.to_device(D)
    gpu_I = cuda.to_device(I)
    gpu_ibabawas = cuda.to_device(ibabawas)
    gpu_idadagdag = cuda.to_device(idadagdag)

    threadsperblock = (32, 32) #fully utilize 1024 threads per block
    dims = L.shape
    blockspergrid_x = ceil(dims[0] / threadsperblock[0])
    blockspergrid_y = ceil(dims[1] / threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    update_central[blockspergrid, threadsperblock](gpu_L, gpu_D, gpu_I, gpu_ibabawas, gpu_idadagdag)
    D = gpu_D.copy_to_host()
    ibabawas = gpu_ibabawas.copy_to_host()
    idadagdag = gpu_idadagdag.copy_to_host()
    I = gpu_I.copy_to_host()

    D = D - ibabawas + idadagdag
    return D, I