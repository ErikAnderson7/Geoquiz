import pandas
import geopandas
import shapely

def openGeoData():
    #path = "data/countries.shp"
    #countries_df = geopandas.read_file(path)

    #Using the geopandas dataset for now because it is much more compact and the performance is much better. 
    #Additionally it has useful data such as country name which my data does not. Makes it easier to check answers, etc.
    gpdf = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    gpdf = gpdf.drop(columns=['pop_est', 'gdp_md_est']) #Filtering out irrelevant columns.
    gpdf.insert(0, 'id', range(0, len(gpdf))) #Adding anonymous id's to countries so the names do not reveal what the countries are. 
    gpdf_noa = gpdf[gpdf.id != 159] #Filter out antartica, which coverst the entire map except for some african countries. 
    #print(gpdf.head())
    return gpdf_noa

def getGameWorldMap():
    cdf = openGeoData()
    cdf = cdf.drop(columns = ['iso_a3', 'continent', 'name'])
    return cdf

def printCountriesDF(gdf):
    print(gdf.show())

def gdfToGeoJSON(gdf):
    return gdf.to_json()

def getCountry(cdf, country_id):
    geo = cdf[cdf.id == country_id]
    country = geo.to_json()
    return country
