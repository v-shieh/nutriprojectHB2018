"""This page contains all the magic functions on this webapp."""

from flask_sqlalchemy import SQLAlchemy
from model import User, Group, Nutrient, Food, Group_Nutrient, Nutrient_Food, Food_Eaten
from model import connect_to_db, db
from flask import Flask, jsonify
import requests
from pprint import pprint
import json
import datetime
# from jinja2 import jinja2.ext.loopcontrols

# Put here as a global component.
autocomp_search = []
in_search = []

def get_food_info(foodname, food_group):
    """Checks in db for the food, if not there, makes a request to USDA and adds it
    """

    # Check to see if this is in the db to begin with.
    db_check = db.session.query(Food).filter(Food.food_name == foodname).first()
    print db_check
    if db_check is not None:
        return db_check
    elif db_check is None:
        # Else if the db_check is none, pass the data to the usda_data_fetcher to
        # get data. In order to retrieve this data, we need the food id no that the
        # USDA assigns to its foods which is where ndbno_fetcher comes in. Please
        # go to that function to see how this works.

        # if usda_data_fetcher(ndbno_fetcher(foodname, food_group)) == "404":
        #     return "Error"
        # else:
        result = usda_data_fetcher(ndbno_fetcher(foodname, food_group))

        print result
        if result == '404':
            return '404'
        else:
        # Returns newly entered entry which previously did not exist.
            return db.session.query(Food).filter(Food.food_name == foodname).first()


def ndbno_fetcher(food_name, food_group):
    """Find the ndbno (USDA assigned food number) based on given food name"""
    # Get the USDA assigned id no using the Search API from USDA
    found = False
    idx = 0

    r = requests.get("https://api.nal.usda.gov/ndb/search/?format=json&q=" + food_name + "&sort=n&fg=" + str(food_group) + "&max=1500&offset=0&api_key=G2ssIQLxbLQmJge4m0S73ps40bvAeIN1BpnW5k7V")

    returned_search = r.json()
    pprint(returned_search)

    # Return the search as a json which is then parsed in order to extract the id number
    # Because the API is annoying and doesn't give me the exact keyword, we have
    # to loop through until WE find the exact match
    while found is False:
        # print idx
    # This try/except statement will catch all the API calls that return KeyErrors
    # and will cause the modal to show to the user
        while True:
            try:
                if returned_search["list"]['item'][idx]['name'] == food_name:
                    found = True
                    ndbno = returned_search["list"]['item'][idx]['ndbno']
                    return ndbno
                else:
                    idx += 1
            except KeyError:
                return "404"


    # Return the id number
    # return ndbno


def usda_data_fetcher(ndbno):
    """Takes missing food and fetches data from USDA db to put into local db"""
    if ndbno == '404':
        return '404'
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
    # print nutrient_data_url
    # Send a request to the USDA database using the URL just built
    d = requests.get(nutrient_data_url)
    data_fetch = d.json()
    pprint(data_fetch)

    # Unpack the missing values needed by the database

    # Because measurements are sent back as essentially one whole string, we
    # need to run it through a function which unpacks it correctly. Please
    # refer to that specific function.

    # This try/except statement will catch all the API calls that return IndexErrors
    # and will cause the modal to show to the user
    while True:
        try:
            complete_measurement = separate_measurement_from_qty(data_fetch['report']['foods'][0]['measure'])
            food_name = data_fetch['report']['foods'][0]['name']
            break
        except IndexError:
            return "404"

    # Use first db patch function to add the basic serving info of the food
    # to the database and print a success statement.

    database_info_patch(ndbno, complete_measurement, food_name)

    # Second db patch function which puts the amount, food_id, and nutrient_id
    # of a nutrient from the data in the nutrient_food table

    food_nutrient_patch(ndbno, data_fetch)

    print "Successful patch of the foods database!"
    # else:
    #     return "404"


def database_info_patch(ndbno, complete_measurement, food_name):
    """Takes the information from the USDA data pull and puts it into the local database"""

    # Take the arguments passed and create a new entry in the foods table
    food_insert = Food(food_id=ndbno,
                       food_name=food_name,
                       food_serving=complete_measurement[0],
                       food_serving_unit=complete_measurement[1])

    db.session.add(food_insert)
    db.session.commit()

def food_nutrient_patch(ndbno, data_fetch):
    """Takes in ndbno and data and patches the Nutrient_Food class table"""

    # Clean up the data so you can just get the nutrients part of the data table
    nutri_list = data_fetch['report']['foods'][0]['nutrients']

    # Go through the list and start storing the values into the database

    for i in range(len(nutri_list)):

        # Get each nutri_id from data everytime you loop around
        USDA_nutri_id = nutri_list[i]['nutrient_id']

        # Some nutrients are nonexistant for foods. This formats the data into a float
        # even if it does not exist
        if nutri_list[i]['value'] == "--":
            amount = 0.0
        else:
            amount = float(nutri_list[i]['value'])

        # Link the info to the columns of the table, add it to a variable, commit it.
        nutrients_of_food = Nutrient_Food(amt_nutri_in_food=amount,
                                          food_id=ndbno,
                                          nutri_id=int(USDA_nutri_id))
        db.session.add(nutrients_of_food)
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


def pull_autocomplete_food_names(groupno):
    """
    Uses USDA API to requests all names of foods of a given food group and places them in a list.
    Keeps track by keeping the name of the query in a separate list.
    """
    idx_count = 0

    if groupno in in_search:
        print "ALREADY IN LIST!"
        # Pull the results from the json_merge fxn
    else:
        in_search.append(groupno)
        results = json_merge(groupno)

        # Keep loop going as long as the idx_count is less than the total number of results,
        # append the names that we got into the autocomp_search list and increment by 1
        while idx_count < results[1]:
            # autocomp_search.append(results[0][idx_count]['name'])
            autocomp_search.append(results[0][idx_count]['name'] + ", " + results[2])
            idx_count += 1

        print "Complete"

# MAKE ANOTHER FUNCTION THAT DOES THE FUNCTION PULLING AND FACTOR INPUTTING


def json_merge(query):
    """Takes several pages of json dicts and merges them together"""
    # Make URL with desired query keyword which will be used to find all the foods matching that
    # ALSO the API_KEY will be the same
    first_basic_url = "https://api.nal.usda.gov/ndb/search/?format=json&sort=n"
    last_api_key = "&api_key=G2ssIQLxbLQmJge4m0S73ps40bvAeIN1BpnW5k7V"

    # The variables below change
    second_food_group = "&fg="
    third_offset = "&max=1500&offset="

    # Append the query arg and set the initial offset to 0
    second_food_group += str(query)
    third_var_offset = third_offset + "0"

    # Make the initial request to find the total amount of entries for that specific query
    d = requests.get(first_basic_url + second_food_group + third_var_offset + last_api_key)
    data = d.json()
    data_filter = data['list']['item']

    third_var_offset = third_offset

    # Store the total amount in the variable query_total
    query_total = int(data['list']['total'])
    group_no = str(data['list']['group'])
    # print query_total

    # Set the offset count to be 1500 (the 'next page' of the USDA API response)
    offset_count = 1500

    # Keep this process happening while the offset_count < the total results in the repsonse
    # returned. Keep pulling responses out and merge them together with the existing
    # json.

    while offset_count < query_total:
        third_var_offset += str(offset_count)

        # Uncomment to check URL:
        # print first_basic_url + second_food_group + third_var_offset + last_api_key

        r = requests.get(first_basic_url + second_food_group + third_var_offset + last_api_key)
        request_in_progress = r.json()
        request_filter = request_in_progress['list']['item']

        # Merge the json dictionaries
        data_filter += request_filter
        offset_count += 1500
        third_var_offset = third_offset

    return data_filter, query_total, group_no


def delete_autocomplete():
    """Used to completely delete the autocomplete list"""

    del autocomp_search[:]
    del in_search[:]

    print "SUCCESS: Autocomplete list has been cleared!"


def calculate_nutri_amount(dict, food_names):
    """Used to make simple nutrient calculations"""

    nutrients_in_food = {}

    iter_dict = dict.iteritems()
    name_nutri = {}  # This is the only dictionary out of the loop because it needs to be accessible out here

    # Iterate through the newly iterable dictionary and make first item in the tuple
    # the key of nutrients_in_food. The value is just the information needed from Nutrient_Food
    # LEARNING POINT: This is where relationships come into play. You get to link this table

    for k, v in iter_dict:
        nutrients_in_food[k] = db.session.query(Nutrient_Food.food_id, Nutrient_Food.nutri_id, Nutrient_Food.amt_nutri_in_food, Nutrient.recom_unit, Food.food_name).join(Nutrient).join(Food).filter(Nutrient_Food.food_id == k).all()

    # pprint(nutrients_in_food)

    for entry in nutrients_in_food:  # Entry = food_id
        nutri_calc = {}  # In loop so each entry has its only nutri_calc dictionary

        nutri_calc['id'] = entry

        nutrient_info = []  # Clears out during every iteration of the loop
        for i in range(len(nutrients_in_food[entry])):
            # For each tuple in nutrients in food, enumerate the index and run until the end
            # Assign this variable the nutrient id
            nutri_num = nutrients_in_food[entry][i][1]
            # Assign this variable the amount inputted by the user by the amount of a given nutrient
            # for a specific food
            nutri_qty = nutrients_in_food[entry][i][2] * float(dict[entry])
            # Assign this variable the unit of the given nutrient
            nutri_amt = nutrients_in_food[entry][i][3]
            # Append all this info formatted into a tuple into the nutrient_info list
            nutrient_info.append((nutri_num, nutri_num_to_name(nutri_num), nutri_qty, nutri_amt))
        # Make a key for nutri_calc titled 'nutrients' and have the value be that list of tuples
        nutri_calc['nutrients'] = nutrient_info
        # Nest nutri_calc dictionary inside of the name_nutri dict with the key being the name of
        # the food
        name_nutri[(nutrients_in_food[entry][0][4]).encode()] = nutri_calc

    pprint(name_nutri)

    return name_nutri


def nutri_num_to_name(id_num):
    """Decodes the id number of the nutrient and returns the name"""
    num_to_name = {}

    # Query db for all the ids and names in the nutrients table
    nutri_name = db.session.query(Nutrient.nutri_id, Nutrient.nutri_name).all()

    # Make a dictionary with these values
    for k, v in nutri_name:
        num_to_name[k] = v

    # Return the name of the nutrient from the id
    return num_to_name[id_num]


def patch_food_log(user_id, json_result):
    """Puts the user_id and the jsonified data into the database"""

    #  Need to get datetime date here and jsonify data
    today = datetime.date.today().strftime("%m%d%Y")
    json_data = json.dumps(json_result)

    log = Food_Eaten(date_entered=today,
                     user_id=user_id,
                     entry=json_data)

    db.session.add(log)
    db.session.commit()


def in_db(email):
    """Checks if emails are already in the database"""

    db_results = db.session.query(User).filter(User.email == email).all()

    if db_results:
        return "200"

    return "Clear"


def user_db_patch(email, pw, fname, lname, age, gender):
    """Adds the newbie to the database"""

    g = db.session.query(Group.group_id).filter(Group.min_age < age, Group.max_age > age, Group.gender == gender).all()
    g_id = g[0][0]

    newbie = User(email=email,
                  pw=pw,
                  fname=fname,
                  lname=lname,
                  age=age,
                  gender_at_birth=gender,
                  group_id=g_id)

    db.session.add(newbie)
    db.session.commit()


def user_verification(email, pw):
    """Takes in email, password and checks if the log-in info is correct"""

    data = db.session.query(User.user_id, User.fname).filter(User.email == email, User.pw == pw).all()

    if data == []:
        return '404'

    return '200', data


def pull_daily_requirements(user_id):
    """Pulls the daily requirements for user's specifc group"""

    # Query for the group_id assigned to the user at registation
    user_group = db.session.query(User.group_id).filter(User.user_id == user_id).all()

    # Query for the nutrients with minimums (no upper limits)
    nutri_no_upper = db.session.query(Nutrient.nutri_name, Group_Nutrient.nutri_id, Group_Nutrient.req_amt, Nutrient.recom_unit).join(Group_Nutrient).filter(Group_Nutrient.group_id == user_group[0][0], Group_Nutrient.upper_lim == 'f').all()
    no_upper = {}

    # Query for the nutrients with upper limits
    nutri_upper = db.session.query(Nutrient.nutri_name, Group_Nutrient.nutri_id, Group_Nutrient.req_amt, Nutrient.recom_unit).join(Group_Nutrient).filter(Group_Nutrient.group_id == user_group[0][0], Group_Nutrient.upper_lim == 't').all()
    upper = {}

    # Iterate through the list of tuples, make a dict with the nutrient_id as the key
    # and the requirement amount, unit, name as values
    for i in nutri_no_upper:
        no_upper[i[1]] = i[2], i[3], i[0]

    for i in nutri_upper:
        upper[i[1]] = i[2], i[3], i[0]

    return user_group, nutri_no_upper, nutri_upper, no_upper, upper


def pull_foods_on_date(date, user_id, option):
    """Pulls foods eaten on specified date by user"""

    amt_eaten = {}

    # Query the db for all the entries entered by a user at a given date
    d = db.session.query(Food_Eaten.entry).filter(Food_Eaten.user_id == user_id, Food_Eaten.date_entered == date).all()
    pprint(d)
    if option == 1:
        if len(d) == 0:
            return 'none'
        else:
            items = {"food": d}
            return items
    elif option == 2:
        dict_string = d[0][0].encode()  # Change into string from unicode

        data = json.loads(dict_string.encode())  # Load the string into a dict
        data_keys = data.keys()  # Get all the keys

        # For every key (food name), go through all the lists of nutrients. Add the nutrient id
        # to the new amt_eaten. Use the get method to see if that key exists already. If not
        # make the value 0 and--irregardless of the value--add the amount from the entry.
        for key in data_keys:
            for i in data[key]['nutrients']:
                amt_eaten[i[0]] = amt_eaten.get(i[0], 0) + i[2]

        return amt_eaten


def calculate_deficiency(entry, reqs):
    """
    Calculates how many more nutrients are needed based on the user's daily requirement
    and the amount they have already consumed
    """

    deficiency = {}

    # Go through the requirement dict and use the nutri ids as the key for the deficiency
    # dict. Make the value the amt from the requirements minus the amount in the entries of that
    # day. Also add the units and name of the nutrient
    for r in reqs:
        deficiency[r] = reqs[r][0] - entry[r], reqs[r][1], reqs[r][2]

    return deficiency


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
