import pandas
import geopandas
import shapely
from project.config import LOG

# Opens the Geodata Dataframe. Uses Geopandas built in dataset
def openGeoData():
    gpdf = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    gpdf = gpdf.drop(columns=['pop_est', 'gdp_md_est']) # Filtering out irrelevant columns.
    gpdf = gpdf[gpdf.name != 'Antarctica'] # Filter out antartica
    gpdf.insert(0, 'id', range(0, len(gpdf))) # Adding Country IDs 
    
    return gpdf

# Returns the map of the world without any country idenifying information
def getGameWorldData():
    LOG.info("Getting the game world map")
    gdpf = openGeoData()
    gdpf = gdpf.drop(columns = ['iso_a3', 'continent', 'name']) # Drop the name and ISO as they can reveal the country
    return gdpf

# Returns the geographic data for a specific country
def getCountry(country_id):
    LOG.info("Getting Country: " + str(country_id))
    gpdf = getGameWorldData()
    geo = gpdf[gpdf.id == country_id]
    return country

# Calculates the distance between two countries with the haversine method
def calculateDistance(gpdf, country1_id, country2_id):
    LOG.info("Calculating the Distance between Countries: " + str(country1_id) + " and " + str(country2_id))
    import math

    # Get the coordinates of the centroid of each country
    c1 = gpdf.iloc[country1_id]
    country1Coords = [c1['geometry'].centroid.x, c1['geometry'].centroid.y]
    c2 = gpdf.iloc[country2_id]
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
    gpdf = openGeoData()
    return gpdf['name']

# Looks up a country's name based on its ID
def lookupCountryName(cid):
    LOG.info("Looking up Country: " + str(cid) + "'s name")
    gpdf = openGeoData()
    country = gpdf[gpdf.id == cid].iloc[0]['name']
    return country

# Looks up a country's ID based on its name
def lookupCountryID(country):
    LOG.info("Looking up " + country + "'s id")
    gpdf = openGeoData()
    country_id = gpdf[gpdf.name == country].iloc[0]['id']
    return int(country_id) # Convert from numpy int64 to python int