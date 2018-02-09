"""This page contains all the magic functions"""

from flask_sqlalchemy import SQLAlchemy
from model import User, Group, Nutrient, Food, Group_Nutrient, Nutrient_Food
from model import connect_to_db, db
from flask import Flask
import requests
from pprint import pprint


def get_food_info(foodname):
    """Checks in db for the food, if not there, makes a request to USDA and adds it
    """

    # Check to see if this is in the db to begin with.
    db_check = db.session.query(Food).filter(Food.food_name == foodname).first()

    if db_check != None:
        return db_check
    elif db_check == None:
        # Else if the db_check is none, pass the data to the data fetcher to
        # get data.
        usda_data_fetcher(ndbno_fetcher(foodname))
        return db.session.query(Food).filter(Food.food_name == foodname).first()

    # If it is not in the db, request the info from USDA which will send
    # a JSON response. The JSON response will then be unpacked by the
    # usda_data_fetcher and put it into the database.


def ndbno_fetcher(food_name):
    """Find the ndbno (USDA assigned food number) based on given food name"""

    r = requests.get("https://api.nal.usda.gov/ndb/search/?format=json&q=" + food_name + "&sort=n&max=1&offset=0&api_key=G2ssIQLxbLQmJge4m0S73ps40bvAeIN1BpnW5k7V")

    returned_search = r.json()
    ndbno = returned_search["list"]['item'][0]['ndbno']
    # print ndbno
    return ndbno


def usda_data_fetcher(ndbno):
    """Takes missing food and fetches data from USDA db to put into local db"""

    nutrient_data_url = "https://api.nal.usda.gov/ndb/nutrients/?format=json&api_key=G2ssIQLxbLQmJge4m0S73ps40bvAeIN1BpnW5k7V"
    basic_nutrient_query = "&nutrients="
    # print ndbno
    ndbno_indentifier = "&ndbno=" + str(ndbno)
    all_nutrient_ids = db.session.query(Nutrient.nutri_id).all()

    for nutri_id in all_nutrient_ids:
        for i in nutri_id:
            basic_nutrient_query += str(i)
            nutrient_data_url += basic_nutrient_query
            basic_nutrient_query = "&nutrients="

    nutrient_data_url += ndbno_indentifier
    # print nutrient_data_url

    d = requests.get(nutrient_data_url)
    data_fetch = d.json()

    complete_measurement = separate_measurement_from_qty(data_fetch['report']['foods'][0]['measure'])
    food_name = data_fetch['report']['foods'][0]['name']

    database_info_patch(ndbno, complete_measurement, food_name)

    print "Successful patch of the database!"


def database_info_patch(ndbno, complete_measurement, food_name):
    """Takes the information from the USDA data pull and puts it into the local database"""

    food_insert = Food(food_id=ndbno,
                       food_name=food_name,
                       food_serving=complete_measurement[0],
                       food_serving_unit=complete_measurement[1])

    db.session.add(food_insert)
    db.session.commit()


def separate_measurement_from_qty(string):
    """Takes the concatination of the measurement and puts them in proper variable form"""

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
