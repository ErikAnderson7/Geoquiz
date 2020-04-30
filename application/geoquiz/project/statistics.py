from flask import Blueprint, jsonify, request
import project.geodata as gd
import pandas
import geopandas
import numpy as np
import random
import math
from sqlalchemy import func, asc
from project.config import LOG
from project import db
from project.guesses import Guess

stats_blueprint = Blueprint('stats', __name__)

@stats_blueprint.route("/whenCorrectMap")
def getCorrectCountryMap():
    country = request.args.get('country', default=0, type = str)
    LOG.info("Getting stats for: " + str(country))
    
    country_id = gd.lookupCountryID(country).item() # .item() to convert numpy int64 -> python int

    stats_df = getCorrectCountryDF(country_id)
    LOG.info(stats_df.columns)

    geodata_df = gd.openGeoData()
    LOG.info(geodata_df.columns)

    # Combine stats and geodata dataframes by using guesscountry as the key
    # Does the equivalent of a right join in SQL on keys guesscountry from stats_df and id from geodata_df
    combined_df = stats_df.merge(geodata_df, how='right', left_on='guesscountry', right_on='id')
    combined_gdf = geopandas.GeoDataFrame(combined_df)
    combined_gdf = combined_gdf.fillna(0) # replace NaN values with 0
    # Calculate distances for countries that have not been guessed for the requested country
    combined_gdf['distance'] = combined_gdf.apply(lambda x: x['distance'] if x['distance'] != 0 else gd.calculateDistance(geodata_df, country_id, int(x['id'])), axis=1)

    # These columns are not needed during displaying the map
    combined_gdf = combined_gdf.drop(columns=['correctcountry', 'guesscountry'])

    combined_json = combined_gdf.to_json()
    return jsonify(combined_json)

@stats_blueprint.route("/whenCorrect")
def getCorrectCountryStats():
    country = request.args.get('country', default=0, type = str)
    country_id = gd.lookupCountryID(country).item()
    LOG.info(country_id)
    df = getCorrectCountryDF(country_id)
    
    try:
        totalCorrectGuesses = int(df[df.guesscountry == country_id].iloc[0]['count'])
        percentageGuessedCorrectly = float(df[df.guesscountry == country_id].iloc[0]['percentOfGuesses'])
    except IndexError as e:
        LOG.info("No correct guesses for this country")
        totalCorrectGuesses = 0
        percentageGuessedCorrectly = 0
    
    totalGuesses = int(df['count'].sum())
    

    totalDistance = (df['distance'] * df['count']).sum()

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

    try:
        top5df = df[df.guesscountry != country_id].nlargest(5, ['percentOfGuesses'])
        LOG.info(top5df)
        stats['mostCommonlyConfused'] = {
                "1st": {"name": gd.lookupCountryName(top5df.iloc[0]['guesscountry']), 
                        "times": int(top5df.iloc[0]['count']), 
                        "percentage": float(top5df.iloc[0]['percentOfGuesses']),
                        "distance": int(top5df.iloc[0]['distance'])
                        },
                "2nd": {"name": gd.lookupCountryName(top5df.iloc[1]['guesscountry']), 
                        "times": int(top5df.iloc[1]['count']), 
                        "percentage": float(top5df.iloc[1]['percentOfGuesses']),
                        "distance": int(top5df.iloc[1]['distance'])
                        },
                "3rd": {"name": gd.lookupCountryName(top5df.iloc[2]['guesscountry']), 
                        "times": int(top5df.iloc[2]['count']), 
                        "percentage": float(top5df.iloc[2]['percentOfGuesses']),
                        "distance": int(top5df.iloc[2]['distance'])
                        },
                "4th": {"name": gd.lookupCountryName(top5df.iloc[3]['guesscountry']), 
                        "times": int(top5df.iloc[3]['count']), 
                        "percentage": float(top5df.iloc[3]['percentOfGuesses']),
                        "distance": int(top5df.iloc[3]['distance'])
                        },
                "5th": {"name": gd.lookupCountryName(top5df.iloc[4]['guesscountry']), 
                        "times": int(top5df.iloc[4]['count']), 
                        "percentage": float(top5df.iloc[4]['percentOfGuesses']),
                        "distance": int(top5df.iloc[4]['distance'])
                        }
                }
    except IndexError as e:
        LOG.info("Not enough data yet for this country to create a top 5 list")    

    return jsonify(stats)

@stats_blueprint.route("/globalStatsMap")
def getGlobalStatsMap():
    LOG.info("Getting global stats map")
    global_df = getGlobalDF()
    geodata_df = gd.openGeoData()

    combined_df = global_df.merge(geodata_df, how='right', left_on='countryid', right_on='id')
    combined_gdf = geopandas.GeoDataFrame(combined_df)
    combined_gdf = combined_gdf.fillna(0)

    return jsonify(combined_gdf.to_json())

@stats_blueprint.route("/globalStats")
def getGlobalStats():
    LOG.info("Getting global stats")
    df = getGlobalDF()

    LOG.info(df.columns)

    totalGuesses = int(df['totalCount'].sum())
    totalCorrectGuesses = int(df['correctCount'].sum())
    percentCorrect = float(totalCorrectGuesses / totalGuesses)

    averageDistance = calculateGlobalAverageDistance()

    top5df = df.nlargest(5, ['percentCorrect'])
    stats = {
        "totalCorrectGuesses": totalCorrectGuesses,
        "totalGuesses": totalGuesses,
        "percentGuessedCorrectly": percentCorrect,
        "averageDistance": int(averageDistance)        
    }

    try:
        stats["mostCommonlyGuessedCorrectly"] =  {
            "1st": {"name": gd.lookupCountryName(top5df.iloc[0]['countryid']), 
                    "times": int(top5df.iloc[0]['correctCount']),
                    "total": int(top5df.iloc[0]['totalCount']), 
                    "percentage": float(top5df.iloc[0]['percentCorrect']),
                    "distance": 0 
                    },
            "2nd": {"name": gd.lookupCountryName(top5df.iloc[1]['countryid']), 
                    "times": int(top5df.iloc[1]['correctCount']),
                    "total": int(top5df.iloc[1]['totalCount']), 
                    "percentage": float(top5df.iloc[1]['percentCorrect']),
                    "distance": 0
                    },
            "3rd": {"name": gd.lookupCountryName(top5df.iloc[2]['countryid']), 
                    "times": int(top5df.iloc[2]['correctCount']),
                    "total": int(top5df.iloc[2]['totalCount']), 
                    "percentage": float(top5df.iloc[2]['percentCorrect']),
                    "distance": 0
                    },
            "4th": {"name": gd.lookupCountryName(top5df.iloc[3]['countryid']), 
                    "times": int(top5df.iloc[3]['correctCount']),
                    "total": int(top5df.iloc[3]['totalCount']), 
                    "percentage": float(top5df.iloc[3]['percentCorrect']),
                    "distance": 0
                    },
            "5th": {"name": gd.lookupCountryName(top5df.iloc[4]['countryid']), 
                    "times": int(top5df.iloc[4]['correctCount']),
                    "total": int(top5df.iloc[4]['totalCount']),  
                    "percentage": float(top5df.iloc[4]['percentCorrect']),
                    "distance": 0
                    }
        }
    except IndexError as e:
        LOG.info("Not enough data for top 5 list")

    return jsonify(stats)

# Queries database for guesses where country_id was the correct country
# Converts the query to a pandas dataframe with correctcountry, guesscountry, and count columns
def getCorrectCountryDF(country_id):
    # SQLAlchemy Query 
    # SELECT correctcountry, guesscountry, count(guesscountry) from guesses where correctcountry = country_id group by guesscountry, correctcountry order by guesscountry asc;
    country_query = db.session.query(Guess.correctcountry, Guess.guesscountry, func.count(Guess.guesscountry).label('count')) \
        .filter(Guess.correctcountry == country_id) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.guesscountry)) \
        .statement
    df = pandas.read_sql_query(country_query, db.session.bind)
    # If there is no data for a requested country return an empty dataframe
    if df.empty:
        LOG.info(df)
        df = df.append({"correctcountry":country_id, "guesscountry":country_id, "count":0}, ignore_index=True)
        LOG.info(df)
    df = calculateStats(df)
    df = df.fillna(0)

    return df

def getGlobalDF():
    # Query that gets the number of correct guesses for each country
    correct_count_query = db.session.query(Guess.correctcountry.label('countryid'), func.count(Guess.guesscountry).label('correctCount')) \
        .filter(Guess.correctcountry == Guess.guesscountry) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.correctcountry), asc(Guess.guesscountry)) \
        .statement
    # Turn query into dataframe
    correctCountDF = pandas.read_sql_query(correct_count_query, db.session.bind)

    # Query that gets the number of total guesses for a country
    total_count_query = db.session.query(Guess.correctcountry.label('countryid'), func.count(Guess.correctcountry).label('totalCount')) \
        .group_by(Guess.correctcountry) \
        .order_by(asc(Guess.correctcountry)) \
        .statement
    # Turn query into dataframe
    totalCountDF = pandas.read_sql_query(total_count_query, db.session.bind)

    # Start with an empty dataframe and populate the country id column with every country id 0-175
    global_df = pandas.DataFrame()
    global_df['countryid'] = range(0, 176)

    # Join the correct count and total count dataframes to the global dataframe
    global_df = global_df.join(correctCountDF.set_index('countryid'), on='countryid')
    global_df = global_df.join(totalCountDF.set_index('countryid'), on='countryid')

    # Calculate the percentage of correct guesses
    global_df['percentCorrect'] = global_df.apply(lambda x: float(x['correctCount'] / x['totalCount']), axis = 1)

    global_df = global_df.fillna(0)

    return global_df

def calculateStats(df):
    LOG.info("Calculating stats")
    cdf = gd.openGeoData()
    # Calculate distance between correct country and guess country for each row (axis=1)
    df['distance'] = df.apply(lambda x: gd.calculateDistance(cdf, x['correctcountry'], x['guesscountry']), axis=1) 
    
    # Calculate the percentage of guesses for each country
    total_guesses = df['count'].sum()
    LOG.info("Total Guesses: " + str(total_guesses))
    if total_guesses != 0:
        df['percentOfGuesses'] = df.apply(lambda x: float(x['count'] / total_guesses), axis=1)
    else:
        df['percentOfGuesses'] = 0

    return df

def calculateGlobalAverageDistance():
    dist_query = db.session.query(Guess.correctcountry, Guess.guesscountry, func.count(Guess.guesscountry).label('count')) \
        .group_by(Guess.guesscountry, Guess.correctcountry) \
        .order_by(asc(Guess.correctcountry)) \
        .statement
    df = pandas.read_sql_query(dist_query, db.session.bind)
    cdf = gd.openGeoData()
    df['distance'] = df.apply(lambda x: gd.calculateDistance(cdf, x['correctcountry'], x['guesscountry']), axis=1)
    
    totalGuesses = df['count'].sum()
    averageDistance = (df['distance'] * df['count']).sum() / totalGuesses
    return averageDistance

