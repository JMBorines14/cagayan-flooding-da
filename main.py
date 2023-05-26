from osgeo import gdal
from camodel import update_D
import numpy as np
import netCDF4 as nc
import sys

def write_to_output(time, C, D, depth_var, m, n):
    for i in range(m):
        for j in range(n):
            depth_var[time, C[i][j][0], C[i][j][1]] = D[i][j]

def simulation(C, L, D, I, depth_var, m, n):
    for time in range(1):
        #update R by calling update_R
        #update D
        I, ibabawas, idadagdag = update_D(L, D, I, m, n)
        D = D - ibabawas + idadagdag

        write_to_output(time, C, D, depth_var, m, n)
        L = S + D

#initialize the dataset
dataset = gdal.Open(sys.argv[1])
n, m, band = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount
print(f'The size is {m} x {n}')
xoff, a, b, yoff, d, e = dataset.GetGeoTransform()

#initialize output file and dimensions
output_dataset = nc.Dataset('output.nc', 'w', format = 'NETCDF4')
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
dataset = None

#initialize rainfall matrix
R = np.zeros((m,n)) #rainfall
R[4093][4093] = 100

#define the I and D matrices
I = np.zeros((m,n)) #I_total
L = S
D = R

#call to simulation function
simulation(C, L, D, I, depth, m, n)
output_dataset.close()