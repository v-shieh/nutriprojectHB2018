"""Main server file for the nutrition web app"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, jsonify, flash
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db
from function import get_food_info, autocomp_search, pull_autocomplete_food_names, calculate_nutri_amount
import json
import requests
import pprint

app = Flask(__name__)  # Do I need this here?

# Used for the Flask sessions and debug toolbar
app.secret_key = "balloonicornfoodie"

# Used to raise an error in Jinja2 instead of having it silently fail.
# YAY for speaking up Jinja2
app.jinja_env.undefined = StrictUndefined
#############################################################################


@app.route('/')
def index():
    """Super awesome responsive video homepage"""

    return render_template('homepage.html')

@app.route('/search', methods=["GET"])
def show_search():
    """Takes in input and sends it to the function which determines location"""

    pull_autocomplete_food_names(1300)  # "Beef products"
    pull_autocomplete_food_names("0100")  # "Dairy and Egg Products"
    pull_autocomplete_food_names("0900")  # "Fruits and Fruit Juices"
    pull_autocomplete_food_names(1500)  # "Finfish and Shellfish Products"
    pull_autocomplete_food_names(1100)  # "Vegetables and Vegetable Products"
    pull_autocomplete_food_names(1600)  # "Legumes and Legume Products"

    return render_template('search.html', food_info=None, searchlist=autocomp_search)


@app.route('/search', methods=['POST'])
# @app.route('/search_inputted', methods=['POST'])
def take_search():
    """Takes in input and sends it to the function which determines location"""

    # food_name = request.form.get("food-input")  # This was the non AJAX test route
    food_name = request.form.get("input")  # This is the AJAX route

    food_name_only = food_name[:-6]
    # print food_name_only
    food_group = str(food_name[-4:])
    # print food_group
    result = get_food_info(food_name_only, food_group)
    # print result
    if result == '404':
        return '404'
    else:
        return jsonify([result.food_name, result.food_serving, result.food_serving_unit, result.food_id])


@app.route('/display_foods', methods=['POST'])
def calculate_nutrients():
    """
    Takes in a dictionary of food and serving qty from the search and sends it to
    be calculated out with a function.
    """

    food_input = []
    food_qty = []
    id_qty = {}

    num_foods = int(request.form.get("food-num"))
    # print num_foods

    for i in range(1, num_foods+1):
        # print i
        id_num = request.form.get("food-name-" + str(i))
        qty_num = request.form.get("serving-qty-" + str(i))
        if id_num is not None and qty_num is not None:
            food_input.append(id_num)
        # print ("Serving test: serving-qty-" + str(i))
            food_qty.append(qty_num)

    id_qty = dict(zip(food_input, food_qty))
    print id_qty

    results = calculate_nutri_amount(id_qty)
    pprint(results)

    # print request.form
    # print food_input
    # print food_qty
    # print id_qty
    return render_template('displayfood.html',
                           results=results)

#############################################################################
if __name__ == "__main__":


# Allows us to use our DebugToolbarExtension so it'll be true when we invoke it
# ex. in python when we want to set up our server

    app.debug = True

    # Make sure that templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Tell app to use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
