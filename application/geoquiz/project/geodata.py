import pandas
import geopandas
import shapely
import math
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
def getCountry(countryid):
    LOG.info("Getting Country: " + str(countryid))
    geodataDF = getGameWorldData()
    countryDF = geodataDF[geodataDF.id == countryid]
    return countryDF

# Calculates the distance between two countries with the haversine method
def calculateDistance(geodataDF, country1id, country2id):
    LOG.info("Calculating the Distance between Countries: " + str(country1id) + " and " + str(country2id))

    # Get the coordinates of the centroid of each country
    country1 = geodataDF.iloc[country1id]
    country1Coords = [country1['geometry'].centroid.x, country1['geometry'].centroid.y]
    country2 = geodataDF.iloc[country2id]
    country2Coords = [country2['geometry'].centroid.x, country2['geometry'].centroid.y]

    longitude1, latitude1 = country1Coords
    longitude2, latitude2 = country2Coords

    # Haversine method to calculate distance between two points
    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(latitude1)
    phi_2 = math.radians(latitude2)

    delta_phi = math.radians(latitude2 - latitude1)
    delta_lambda = math.radians(longitude2 - longitude1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters
    km = meters / 1000.0  # output distance in kilometers
    km = round(km, 3)

    return km

# Returns a list of countries
def getCountryList():
    LOG.info("Getting list of countries")
    geodataDF = openGeoData()
    return geodataDF['name']

# Looks up a country's name based on its ID
def lookupCountryName(countryid):
    LOG.info("Looking up Country: " + str(countryid) + "'s name")
    geodataDF = openGeoData()
    country = geodataDF[geodataDF.id == countryid].iloc[0]['name']
    return country

# Looks up a country's ID based on its name
def lookupCountryID(country):
    LOG.info("Looking up " + country + "'s id")
    geodatDF = openGeoData()
    countryid = geodatDF[geodatDF.name == country].iloc[0]['id']
    return int(countryid) # Convert from numpy int64 to python int
