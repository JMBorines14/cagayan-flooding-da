from osgeo import gdal
from camodel import update_D
import numpy as np
import netCDF4 as nc
import sys

def x_coord(idx):
    return a*idx + b*idx + xoff

def y_coord(idx):
    return d*idx + e*idx + yoff

if __name__ == "__main__":
    #open the TIFF file
    dataset = gdal.Open(sys.argv[1])
    n, m, band = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount
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
    depth.grid_mapping = 'phlvfour'

    phlvfour = output_dataset.createVariable('phlvfour', 'c')
    phlvfour.spatial_ref = dataset.GetProjectionRef()
    phlvfour.GeoTransform = " ".join(str(x) for x in dataset.GetGeoTransform())

    #output latitudes and longitudes to the dataset
    lats[:] = np.array([x_coord(k) for k in range(m)])
    lons[:] = np.array([y_coord(k) for k in range(n)])

    data1 = dataset.GetRasterBand(1).ReadAsArray()
    dataset = None

    #define the surface and depth matrices
    S = np.array([list(i) for i in list(data1)])
    I = np.zeros((m,n)) #I_total
    D = np.zeros((m,n))

    #initialize the rainfall distribution matrix
    R = np.zeros((m,n)) #rainfall
    R[4093][4093] = 100

    D += R #update the depth
    L = S + D #initialize L as the sum of S and D

    for time in range(1):
        I, ibabawas, idadagdag = update_D(L, D, I, m, n)
        D = D - ibabawas + idadagdag

        depth[time, :, :] = D
        print(depth[0, 4093, 4093], depth[0, 4093, 4094], depth[0, 4093, 4092], depth[0, 4092,4093], depth[0, 4094, 4093])
        R = np.zeros((m, n)) #update this to the rainfall function
        D += R
        L = S + D
    
    output_dataset.close()
    print("I am done with the simulation.")