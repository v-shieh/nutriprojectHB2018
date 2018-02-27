"""Main server file for the nutrition web app"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, jsonify, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db
from function import get_food_info, autocomp_search, pull_autocomplete_food_names, calculate_nutri_amount, in_db, user_db_patch, user_verification, patch_food_log
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
    food_names = []
    nutrient_info = {}

    num_foods = int(request.form.get("food-num"))
    # print num_foods

    for i in range(1, num_foods+1):
        # print i
        fname = (request.form.get("name-" + str(i)))

        if fname is not None:
            fname = fname.encode().replace('(', '').replace(')', '')

        id_num = request.form.get("food-name-" + str(i))
        qty_num = request.form.get("serving-qty-" + str(i))
        nutrient_info[fname] = {}
        if id_num is not None and qty_num is not None and fname is not None:
            food_input.append(id_num)
            food_qty.append(qty_num)
            food_names.append(fname)

    id_qty = dict(zip(food_input, food_qty))
    # print id_qty, food_names

    result = calculate_nutri_amount(id_qty, food_names)

    patch_food_log(session['user_id'], result)
    print "Food entry added to log"

    return render_template('displayfood.html',
                           result=result)


@app.route('/register')
def user_registration():
    """Allow new users to register"""

    pass

    return render_template('registration.html')


@app.route('/email_check')
def check_email():
    """Checks if email in db"""

    email_input = request.args.get("email")

    email_status = in_db(email_input.lower())

    return email_status


@app.route('/welcome_newbie', methods=['POST'])
def add_user():
    """Adds user to the db"""

    email = request.form.get("reg-email")
    pw = request.form.get("pw")
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    age = request.form.get("age")
    gender = request.form.get("gender")

    user_db_patch(email, pw, fname, lname, age, gender)
    retrieve_new_user = user_verification(email.encode(), pw.encode())

    session['user_id'] = retrieve_new_user[1][0][0]
    session['user_name'] = (retrieve_new_user[1][0][1]).encode()

    return render_template('welcome-newbie.html')


@app.route('/double_check', methods=['POST'])
def dbl_check():
    """
    Allow registered users to be redirected to a profile if their log-in
    information is correct. Otherwise sent back to the homepage form
    """

    log_in_email = request.form.get("email")
    log_in_pw = request.form.get("pw")

    result = user_verification(log_in_email.encode(), log_in_pw.encode())

    if result == '404':
        flash('Email or password did not match. Please try again!')
        return redirect('/')
    elif result[0] == '200':
        session['user_id'] = result[1][0][0]
        session['user_name'] = (result[1][0][1]).encode()
        return redirect('/welcome-back')


@app.route('/welcome-back')
def welcome_back():
    """Welcomes back users"""

    return render_template('welcome-back.html')


#############################################################################
if __name__ == "__main__":


# Allows us to use our DebugToolbarExtension so it'll be true when we invoke it
# ex. in python when we want to set up our server

    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    # Make sure that templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Tell app to use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
