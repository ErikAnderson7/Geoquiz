import pandas
import geopandas
import numpy as np
import math
from sqlalchemy import func, asc
from project.config import LOG
from project import db
from project.guesses import Guess
import project.geodata as gd

# Queries database for guesses where countryid was the correct country
# Converts the query to a pandas dataframe
def getPerCountryDF(countryid):
    LOG.info("Getting Country: " + str(countryid) + "'s dataframe")
    # SQLAlchemy Query 
    # SELECT correctcountry, guesscountry, count(guesscountry) from guesses where correctcountry = countryid group by guesscountry, correctcountry order by guesscountry asc;
    countryQuery = db.session.query(Guess.correctcountry, Guess.guesscountry, func.count(Guess.guesscountry).label('count')) \
        .filter(Guess.correctcountry == countryid) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.guesscountry)) \
        .statement
    countryDF = pandas.read_sql_query(countryQuery, db.session.bind)
    # If there is no data for a requested country append one row representing no correct guesses to the dataframe
    if countryDF.empty:
        countryDF = countryDF.append({"correctcountry": countryid, "guesscountry": countryid, "count":0}, ignore_index=True)
    countryDF = calculatePerCountryStats(countryDF)
    countryDF = countryDF.fillna(0)

    return countryDF


# Queries database for guesses where country_id was the correct country
# Converts the query to a pandas dataframe
def getGlobalDF():
    LOG.info("Getting global stats dataframe")
    # Query that gets the number of correct guesses for each country
    correctCountQuery = db.session.query(Guess.correctcountry.label('countryid'), func.count(Guess.guesscountry).label('correctCount')) \
        .filter(Guess.correctcountry == Guess.guesscountry) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.correctcountry), asc(Guess.guesscountry)) \
        .statement
    # Turn query into dataframe
    correctCountDF = pandas.read_sql_query(correctCountQuery, db.session.bind)

    # Query that gets the number of total guesses for a country
    totalCountQuery = db.session.query(Guess.correctcountry.label('countryid'), func.count(Guess.correctcountry).label('totalCount')) \
        .group_by(Guess.correctcountry) \
        .order_by(asc(Guess.correctcountry)) \
        .statement
    # Turn query into dataframe
    totalCountDF = pandas.read_sql_query(totalCountQuery, db.session.bind)

    # Start with an empty dataframe and populate the country id column with every country id 0-175
    globalDF = pandas.DataFrame()
    globalDF['countryid'] = range(0, 176)

    # Join the correct count and total count dataframes to the global dataframe
    globalDF = globalDF.join(correctCountDF.set_index('countryid'), on='countryid')
    globalDF = globalDF.join(totalCountDF.set_index('countryid'), on='countryid')

    # Calculate the percentage of correct guesses
    globalDF['percentCorrect'] = globalDF.apply(lambda x: float(x['correctCount'] / x['totalCount']), axis = 1)

    globalDF = globalDF.fillna(0)

    return globalDF

# Calculates the distance between countries, percent of total guesses for each country
def calculatePerCountryStats(countryDF):
    LOG.info("Calculating per country stats")
    geodataDF = gd.openGeoData()
    # Calculate distance between correct country and guess country for each row (axis=1)
    countryDF['distance'] = countryDF.apply(lambda x: gd.calculateDistance(geodataDF, x['correctcountry'], x['guesscountry']), axis=1) 
    
    # Calculate the percentage of guesses for each country
    total_guesses = countryDF['count'].sum()
    LOG.info("Total Guesses: " + str(total_guesses))
    if total_guesses != 0:
        countryDF['percentOfGuesses'] = countryDF.apply(lambda x: float(x['count'] / total_guesses), axis=1)
    else:
        countryDF['percentOfGuesses'] = 0

    return countryDF

# Calculates the average distance of every guess
def calculateGlobalAverageDistance():
    LOG.info("Calculating average distance between correctcountry and guesscountry for every guess")
    distanceQuery = db.session.query(Guess.correctcountry, Guess.guesscountry, func.count(Guess.guesscountry).label('count')) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.correctcountry)) \
        .statement
    distanceDF = pandas.read_sql_query(distanceQuery, db.session.bind)
    cdf = gd.openGeoData()
    distanceDF['distance'] = distanceDF.apply(lambda x: gd.calculateDistance(cdf, x['correctcountry'], x['guesscountry']), axis=1)
    
    totalGuesses = distanceDF['count'].sum()
    averageDistance = (distanceDF['distance'] * distanceDF['count']).sum() / totalGuesses
    return averageDistance

# Returns a given country's statistics
def getPerCountryStats(countryid):
    LOG.info("Calculating Country: " + str(countryid) + "'s stats")
    countryDF = getPerCountryDF(countryid)
    
    try:
        totalCorrectGuesses = int(countryDF[countryDF.guesscountry == countryid].iloc[0]['count'])
        percentageGuessedCorrectly = float(countryDF[countryDF.guesscountry == countryid].iloc[0]['percentOfGuesses'])
    except IndexError as e: # Catch when there are no correct guesses for a country
        LOG.info("No correct guesses for this country")
        totalCorrectGuesses = 0
        percentageGuessedCorrectly = 0
    
    totalGuesses = int(countryDF['count'].sum())
    totalDistance = (countryDF['distance'] * countryDF['count']).sum()

    if totalGuesses != 0:
        averageDistance = int(totalDistance / totalGuesses)
    else:
        percentageGuessedCorrectly = 0
        averageDistance = 0

    stats = {
        "timesGuessedCorrectly": totalCorrectGuesses,
        "totalGuesses": totalGuesses,
        "percentGuessedCorrectly": percentageGuessedCorrectly,
        "averageDistance": averageDistance    
    }

    # Try to create a list of the top 5 most commonly mistaken countries
    try:
        top5DF = countryDF[countryDF.guesscountry != countryid].nlargest(5, ['percentOfGuesses'])
        LOG.info(top5DF)
        stats['mostCommonlyConfused'] = {
                "1st": {"name": gd.lookupCountryName(top5DF.iloc[0]['guesscountry']), 
                        "times": int(top5DF.iloc[0]['count']), 
                        "percentage": float(top5DF.iloc[0]['percentOfGuesses']),
                        "distance": int(top5DF.iloc[0]['distance'])
                        },
                "2nd": {"name": gd.lookupCountryName(top5DF.iloc[1]['guesscountry']), 
                        "times": int(top5DF.iloc[1]['count']), 
                        "percentage": float(top5DF.iloc[1]['percentOfGuesses']),
                        "distance": int(top5DF.iloc[1]['distance'])
                        },
                "3rd": {"name": gd.lookupCountryName(top5DF.iloc[2]['guesscountry']), 
                        "times": int(top5DF.iloc[2]['count']), 
                        "percentage": float(top5DF.iloc[2]['percentOfGuesses']),
                        "distance": int(top5DF.iloc[2]['distance'])
                        },
                "4th": {"name": gd.lookupCountryName(top5DF.iloc[3]['guesscountry']), 
                        "times": int(top5DF.iloc[3]['count']), 
                        "percentage": float(top5DF.iloc[3]['percentOfGuesses']),
                        "distance": int(top5DF.iloc[3]['distance'])
                        },
                "5th": {"name": gd.lookupCountryName(top5DF.iloc[4]['guesscountry']), 
                        "times": int(top5DF.iloc[4]['count']), 
                        "percentage": float(top5DF.iloc[4]['percentOfGuesses']),
                        "distance": int(top5DF.iloc[4]['distance'])
                        }
                }
    except IndexError as e: # Catches when 5 different countries have not been guessed for the country
        LOG.info("Not enough data yet for this country to create a top 5 list")
    
    return stats

# Returns a map containing statistics for a given country
def getPerCountryMap(countryid):
    LOG.info("Getting Country: " + str(countryid) + "'s statistics map")
    statsDF = getPerCountryDF(countryid)
    geodataDF = gd.openGeoData()

    # Combine stats and geodata dataframes by using guesscountry as the key
    # Does the equivalent of a right join in SQL on keys guesscountry from stats_df and id from geodata_df
    combinedDF = statsDF.merge(geodataDF, how='right', left_on='guesscountry', right_on='id')
    combinedGDF = geopandas.GeoDataFrame(combinedDF) # Convert the pandas dataframe to a Geopandas dataframe
    combinedGDF = combinedGDF.fillna(0) # replace NaN values with 0
    # Calculate distances for countries that have not been guessed for the requested country
    combinedGDF['distance'] = combinedGDF.apply(lambda x: x['distance'] if x['distance'] != 0 else gd.calculateDistance(geodataDF, countryid, int(x['id'])), axis=1)

    # These columns are not needed during displaying the map
    combinedGDF = combinedGDF.drop(columns=['correctcountry', 'guesscountry'])

    return combinedGDF.to_json()

# Returns a map containing global statistics
def getGlobalStatsMap():
    LOG.info("Getting global stats map")
    globalDF = getGlobalDF()
    geodataDF = gd.openGeoData()

    combinedDF = globalDF.merge(geodataDF, how='right', left_on='countryid', right_on='id')
    combinedGDF = geopandas.GeoDataFrame(combinedDF)
    combinedGDF = combinedGDF.fillna(0)

    return combinedGDF.to_json()

# Returns global statistics
def getGlobalStats():
    LOG.info("Calculating global stats")
    globalDF = getGlobalDF()

    totalGuesses = int(globalDF['totalCount'].sum())
    totalCorrectGuesses = int(globalDF['correctCount'].sum())
    percentCorrect = float(totalCorrectGuesses / totalGuesses)

    averageDistance = calculateGlobalAverageDistance()

    top5DF = globalDF.nlargest(5, ['percentCorrect'])
    stats = {
        "totalCorrectGuesses": totalCorrectGuesses,
        "totalGuesses": totalGuesses,
        "percentGuessedCorrectly": percentCorrect,
        "averageDistance": int(averageDistance)        
    }

    # Try to create a list of the top 5 most commonly correctly guessed countries
    try:
        stats["mostCommonlyGuessedCorrectly"] =  {
            "1st": {"name": gd.lookupCountryName(top5DF.iloc[0]['countryid']), 
                    "times": int(top5DF.iloc[0]['correctCount']),
                    "total": int(top5DF.iloc[0]['totalCount']), 
                    "percentage": float(top5DF.iloc[0]['percentCorrect']),
                    "distance": 0 
                    },
            "2nd": {"name": gd.lookupCountryName(top5DF.iloc[1]['countryid']), 
                    "times": int(top5DF.iloc[1]['correctCount']),
                    "total": int(top5DF.iloc[1]['totalCount']), 
                    "percentage": float(top5DF.iloc[1]['percentCorrect']),
                    "distance": 0
                    },
            "3rd": {"name": gd.lookupCountryName(top5DF.iloc[2]['countryid']), 
                    "times": int(top5DF.iloc[2]['correctCount']),
                    "total": int(top5DF.iloc[2]['totalCount']), 
                    "percentage": float(top5DF.iloc[2]['percentCorrect']),
                    "distance": 0
                    },
            "4th": {"name": gd.lookupCountryName(top5DF.iloc[3]['countryid']), 
                    "times": int(top5DF.iloc[3]['correctCount']),
                    "total": int(top5DF.iloc[3]['totalCount']), 
                    "percentage": float(top5DF.iloc[3]['percentCorrect']),
                    "distance": 0
                    },
            "5th": {"name": gd.lookupCountryName(top5DF.iloc[4]['countryid']), 
                    "times": int(top5DF.iloc[4]['correctCount']),
                    "total": int(top5DF.iloc[4]['totalCount']),  
                    "percentage": float(top5DF.iloc[4]['percentCorrect']),
                    "distance": 0
                    }
        }
    except IndexError as e:
        LOG.info("Not enough data for top 5 list")

    return stats