import pandas
import geopandas
import shapely
from project.config import LOG

# Opens the Geodata Dataframe. Uses Geopandas built in dataset
def openGeoData():
    geodataDF = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    geodataDF = geodataDF.drop(columns=['pop_est', 'gdp_md_est']) # Filtering out irrelevant columns.
    geodataDF = geodataDF[geodataDF.name != 'Antarctica'] # Filter out antartica
    geodataDF.insert(0, 'id', range(0, len(geodataDF))) # Adding Country IDs 
    
    return geodataDF

# Returns the map of the world without any country idenifying information
def getGameWorldData():
    LOG.info("Getting the game world map")
    geodataDF = openGeoData()
    geodataDF = geodataDF.drop(columns = ['iso_a3', 'continent', 'name']) # Drop the name and ISO as they can reveal the country
    return geodataDF

# Returns the geographic data for a specific country
def getCountry(country_id):
    LOG.info("Getting Country: " + str(country_id))
    geodataDF = getGameWorldData()
    geo = geodataDF[geodataDF.id == country_id]
    return country

# Calculates the distance between two countries with the haversine method
def calculateDistance(geodataDF, country1_id, country2_id):
    LOG.info("Calculating the Distance between Countries: " + str(country1_id) + " and " + str(country2_id))
    import math

    # Get the coordinates of the centroid of each country
    c1 = geodataDF.iloc[country1_id]
    country1Coords = [c1['geometry'].centroid.x, c1['geometry'].centroid.y]
    c2 = geodataDF.iloc[country2_id]
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

# Returns a list of countries
def getCountryList():
    LOG.info("Getting list of countries")
    geodataDF = openGeoData()
    return geodataDF['name']

# Looks up a country's name based on its ID
def lookupCountryName(cid):
    LOG.info("Looking up Country: " + str(cid) + "'s name")
    geodataDF = openGeoData()
    country = geodataDF[geodataDF.id == cid].iloc[0]['name']
    return country

# Looks up a country's ID based on its name
def lookupCountryID(country):
    LOG.info("Looking up " + country + "'s id")
    geodatDF = openGeoData()
    country_id = geodatDF[geodatDF.name == country].iloc[0]['id']
    return int(country_id) # Convert from numpy int64 to python int