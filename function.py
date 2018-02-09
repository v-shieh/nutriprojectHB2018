"""This page contains all the magic functions on this webapp."""

from flask_sqlalchemy import SQLAlchemy
from model import User, Group, Nutrient, Food, Group_Nutrient, Nutrient_Food
from model import connect_to_db, db
from flask import Flask
import requests
# from pprint import pprint


def get_food_info(foodname):
    """Checks in db for the food, if not there, makes a request to USDA and adds it
    """

    # Check to see if this is in the db to begin with.
    db_check = db.session.query(Food).filter(Food.food_name == foodname).first()

    if db_check != None:
        return db_check
    elif db_check == None:
        # Else if the db_check is none, pass the data to the usda_data_fetcher to
        # get data. In order to retrieve this data, we need the food id no that the
        # USDA assigns to its foods which is where ndbno_fetcher comes in. Please
        # go to that function to see how this works.
        usda_data_fetcher(ndbno_fetcher(foodname))
        # Returns newly entered entry which previously did not exist.
        return db.session.query(Food).filter(Food.food_name == foodname).first()


def ndbno_fetcher(food_name):
    """Find the ndbno (USDA assigned food number) based on given food name"""
    # Get the USDA assigned id no using the Search API from USDA
    r = requests.get("https://api.nal.usda.gov/ndb/search/?format=json&q=" + food_name + "&sort=n&max=1&offset=0&api_key=G2ssIQLxbLQmJge4m0S73ps40bvAeIN1BpnW5k7V")

    returned_search = r.json()
    # Return the search as a json which is then parsed in order to extract the id number
    ndbno = returned_search["list"]['item'][0]['ndbno']
    # Return the id number
    return ndbno


def usda_data_fetcher(ndbno):
    """Takes missing food and fetches data from USDA db to put into local db"""

    # Assign basic components of the URL we are building to variables
    # In the event that we add more nutrients to the list that our webapp provides,
    # we are able to modify the URL.
    nutrient_data_url = "https://api.nal.usda.gov/ndb/nutrients/?format=json&api_key=G2ssIQLxbLQmJge4m0S73ps40bvAeIN1BpnW5k7V"
    basic_nutrient_query = "&nutrients="

    # Add the last piece of the URL which is the USDA assigned id number of the
    # food we are referring to
    ndbno_indentifier = "&ndbno=" + str(ndbno)
    # Get all the nutrient id numbers that exist in the database
    all_nutrient_ids = db.session.query(Nutrient.nutri_id).all()

    # For each nutirent id stored tuple in the list of tuples of nutrient ids,
    # concatenate the basic_nutrient_query ("&nutrients=") with that specific
    # id number that is pulled. Then concatenate that to the end of the nutrient_data_url.
    # At the end of it all, return the basic_nutrient_query to be the original value
    for nutri_id in all_nutrient_ids:
        for i in nutri_id:
            basic_nutrient_query += str(i)
            nutrient_data_url += basic_nutrient_query
            basic_nutrient_query = "&nutrients="

    # Append the tail end of the URL to the full version of the URL
    nutrient_data_url += ndbno_indentifier

    # Send a request to the USDA database using the URL just built
    d = requests.get(nutrient_data_url)
    data_fetch = d.json()

    # Unpack the missing values needed by the database

    # Because measurements are sent back as essentially one whole string, we
    # need to run it through a function which unpacks it correctly. Please
    # refer to that specific function.
    complete_measurement = separate_measurement_from_qty(data_fetch['report']['foods'][0]['measure'])
    food_name = data_fetch['report']['foods'][0]['name']

    # Use another function to add it to the database and print a success statement.
    database_info_patch(ndbno, complete_measurement, food_name)

    print "Successful patch of the database!"


def database_info_patch(ndbno, complete_measurement, food_name):
    """Takes the information from the USDA data pull and puts it into the local database"""

    # Take the arguments passed and create a new entry in the foods table
    food_insert = Food(food_id=ndbno,
                       food_name=food_name,
                       food_serving=complete_measurement[0],
                       food_serving_unit=complete_measurement[1])

    db.session.add(food_insert)
    db.session.commit()


def separate_measurement_from_qty(string):
    """Takes the concatination of the measurement and puts them in proper variable form"""

    # Take the string that the measurements are put into, split it by the spaces,
    # separate the integer/float value and the string measurement, and spit back
    # out two new variables in the right format. This works for both one word and
    # two word measurements (ex. 'cup' and 'fl oz'). It will keep two word
    # measurements together.
    split_str = string.split(' ')
    amount = float(split_str[0])
    measurement = (" ".join(split_str[1:]))

    return amount, measurement



if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
