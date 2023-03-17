from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

fn = "/elevation.tif"
ds = gdal.Open(fn)

data_array = ds.GetRasterBand(1).ReadAsArray()
print(data_array.shape)