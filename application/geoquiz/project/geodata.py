import pandas
import geopandas
import shapely
from project.config import LOG

def openGeoData():
    LOG.info("Opening the Geopandas DF")
    #Using the geopandas dataset for now because it is much more compact and the performance is much better. 
    #Additionally it has useful data such as country name which my data does not. Makes it easier to check answers, etc.
    gpdf = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    gpdf = gpdf.drop(columns=['pop_est', 'gdp_md_est']) #Filtering out irrelevant columns.
    gpdf = gpdf[gpdf.name != 'Antarctica'] #Filter out antartica, which coverst the entire map except for some african countries.
    gpdf.insert(0, 'id', range(0, len(gpdf))) #Adding anonymous id's to countries so the names do not reveal what the countries are. 
    
    return gpdf

def getGameWorldMap():
    LOG.info("Getting the game world map")
    cdf = openGeoData()
    cdf = cdf.drop(columns = ['iso_a3', 'continent', 'name'])
    return cdf

def printCountriesDF(gdf):
    LOG.info(gdf.show())

def gdfToGeoJSON(gdf):
    LOG.info("Converting the GDF to GeoJSON")
    return gdf.to_json()

def getCountry(cdf, country_id):
    LOG.info("Getting Country: " + str(country_id))
    geo = cdf[cdf.id == country_id]
    country = geo.to_json()
    return country

# Calculates the distance between two countries with the haversine method
def calcDistance(cdf, country1_id, country2_id):
    LOG.info("Calculating the Distance between Countries: " + str(country1_id) + " and " + str(country2_id))
    import math

    c1 = cdf.iloc[country1_id]
    country1Coords = [c1['geometry'].centroid.x, c1['geometry'].centroid.y]

    c2 = cdf.iloc[country2_id]
    country2Coords = [c2['geometry'].centroid.x, c2['geometry'].centroid.y]

    lon1, lat1 = country1Coords
    lon2, lat2 = country2Coords
    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters
    km = meters / 1000.0  # output distance in kilometers

    meters = round(meters)
    km = round(km, 3)
    return km

def lookupCountryByID(cid):
    cdf = openGeoData()
    country = cdf[cdf.id == cid]['name']