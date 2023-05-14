from osgeo import gdal
from camodel import update_D
import numpy as np
import netCDF4 as nc
import sys

#parameters
g = 9.81
man = 0.03
delta_X = 1
tol = 0
A = 1
delta_t = 600
delta_e = 1

def update_R(R):
    pass

def write_to_output(time, C, D, depth_var, m, n):
    for i in range(m):
        for j in range(n):
            depth_var[time, C[i][j][0], C[i][j][1]] = D[i][j]

def simulation(C, L, D, I, depth_var, m, n):
    for time in range(10):
        #update R by calling update_R
        #update D
        D, I = update_D(L, D, I)
        write_to_output(time, C, D, depth_var, m, n)
        L = S + D

#initialize the dataset
dataset = gdal.Open(sys.argv[1])
m, n, band = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount
xoff, a, b, yoff, d, e = dataset.GetGeoTransform()

#initialize output file and dimensions
output_dataset = nc.DataSet('output.nc', 'w', format = 'NETCDF4')
time = output_dataset.createDimension('time', None)
lat = output_dataset.createDimension('lat', m)
lon = output_dataset.createDimension('lon', n)

times = output_dataset.createVariable('time', 'f8', ('time',))
lats = output_dataset.createVariable('lat', 'f4', ('lat',))
lons = output_dataset.createVariable('lon', 'f4', ('lon',))
depth = output_dataset.createVariable('depth', 'f4', ('time', 'lat', 'lon',))

def pixeltocoord(x, y):
    xp = a*x + b*y + xoff
    yp = d*x + e*y + yoff
    return (xp, yp)

def extract_coords(row, col):
    C = [[0] * col] * row

    for i in range(row):
        for j in range(col):
            C[i][j] = pixeltocoord(i, j)
    
    return C

#get surface and coordinate matrix
C = extract_coords(m, n) #coordinate matrix
data1 = dataset.GetRasterBand(1).ReadAsArray()
S = np.array([list(i) for i in list(data1)])

#initialize rainfall matrix
R = np.array([[0. for _ in range(m)] for _ in range(n)]) #rainfall

#define the I and D matrices
I = np.array([[0. for _ in range(m)] for _ in range(n)]) #I_total
D = np.array([[0. for _ in range(m)] for _ in range(n)])

L = S
D = R

#call to simulation function

output_dataset.close()