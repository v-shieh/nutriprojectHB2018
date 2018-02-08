"""This page contains all the magic functions"""

from flask_sqlalchemy import SQLAlchemy
from model import User, Group, Nutrient, Food, Group_Nutrient, Nutrient_Food
from model import connect_to_db, db
from flask import Flask


def get_food_info(foodname):
    """Checks in db for the food, if not there, makes a request to USDA and adds it
    """

    # Check to see if this is in the db to begin with.
    db_check = db.session.query(Food).filter(Food.food_name == foodname).first()

    if db_check != None:
        # If the db_check returns the info on the food, return to the server
        pass
    elif db_check == None:
        # Else if the db_check is none, pass the data to the data fetcher to
        # get data.
        pass

    # If it is not in the db, request the info from USDA which will send
    # a JSON response. The JSON response will then be unpacked by the
    # usda_data_fetcher and put it into the database.


def usda_data_fetcher(foodname):
    """Takes missing food and fetches data from USDA db to put into local db"""

    pass
