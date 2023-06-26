import pandas as pd
import os
import pandas as pd
import geopandas
from shapely.geometry import Point
from pathlib import Path
from osgeo import gdal
from osgeo import ogr

data = pd.read_csv("S-042023-055_rainfall.csv")
data = data.fillna(0)   # Fill NaN values with 0s

# Weather Station coordinates
# Aparri, Baguio City, Calayan, Casiguran, Tuguegarao City
lat = [18.359681, 16.4041, 19.266678, 16.265428, 17.64768]
long = [121.630433, 120.601447, 121.471175, 122.128814, 121.75856]

ctr = 1

for index, row in data.iterrows():
    filename = str(ctr)
    rainfall = [row['Aparri'], row['Baguio'], row['Calayan'], row['Casiguran'], row['Tuguegarao']]

    new_df = pd.DataFrame(data = {'lat': lat,
                                  'long': long,
                                  'rain': rainfall}, index=[0,1,2,3,4])
    
    new_df.to_csv('csv/{fn}.csv'.format(fn = filename))
    ctr += 1

for filename in os.listdir('csv'):
    f = os.path.join('csv', filename)

    table = pd.read_csv(f)
    table['coordinates'] = table[['long', 'lat']].values.tolist()
    table['coordinates'] = table['coordinates'].apply(Point)
    stations = geopandas.GeoDataFrame(table, geometry = 'coordinates')
    stations = stations.set_crs('epsg:4326')
    stations.to_file('shp/{fn}.shp'.format(fn = Path(f).stem))