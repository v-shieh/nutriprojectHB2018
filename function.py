"""This page contains all the magic functions"""

from flask_sqlalchemy import SQLAlchemy
from model import User, Group, Nutrient, Food, Group_Nutrient, Nutrient_Food
from model import connect_to_db, db
from flask import Flask
import requests


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

    # If it is not in the db, request the info from USDA which will send
    # a JSON response. The JSON response will then be unpacked by the
    # usda_data_fetcher and put it into the database.


def ndbno_fetcher(foodname):
    """Find the ndbno (USDA assigned food number) based on given food name"""

    r = requests.get("https://api.nal.usda.gov/ndb/search/?format=json&q=foodname&sort=n&max=1&offset=0&api_key=G2ssIQLxbLQmJge4m0S73ps40bvAeIN1BpnW5k7V")

    returned_search = r.json()
    ndbno = returned_search['list']['item'][0]['ndbno']

    return ndbno


def usda_data_fetcher(ndbno):
    """Takes missing food and fetches data from USDA db to put into local db"""

    
