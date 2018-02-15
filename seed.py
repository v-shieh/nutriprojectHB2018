"""File to seed group information about nutritional requirements based on gender and age"""


from sqlalchemy import func
from model import User, Group, Nutrient, Food, Group_Nutrient, Nutrient_Food
from model import connect_to_db, db
# from server import app
from flask import Flask
from sqlalchemy.inspection import inspect
from function import pull_autocomplete_food_names

import csv


def load_groups():
    """Load groups from the group.csv file into the database"""

    print "Loading groups..."

    # Reads the csv and inserts it.
    with open('seed_data/group_type.csv') as csvfile:
        read_line = csv.reader(csvfile)  # Must read before for loop

        for row in read_line:
            # Skips over the first line of code which has labels on it
            if row[0] == 'ID':
                continue
            else:
                # Assign parameters to the data and change to the correct datatype
                group = Group(group_id=int(row[0]),
                              group_name=row[1],
                              min_age=int(row[2]),
                              max_age=int(row[3]),
                              gender=row[4])

            db.session.add(group)

    db.session.commit()


def load_nutri_no():
    """Load nutrient name and number from the nutrientname_no.csv file into the database"""

    print "Loading nutrients and their numbers..."

    # Reads the csv and inserts it.
    with open('seed_data/nutrient_info.csv') as csvfile:
        read_line = csv.reader(csvfile, delimiter=',')  # Must read before for loop

        for row in read_line:
            # Skips over the first line of code which has labels on it
            if row[0] == 'Name ':
                continue
            else:
                # Assign parameters to the data and change to the correct datatype
                nutrient = Nutrient(nutri_name=row[0],
                                    nutri_id=int(row[1]),
                                    recom_unit=row[2])
            db.session.add(nutrient)

    db.session.commit()


def load_group_nutrient():
    """Load nutrient requirements for each group from the group_nutrient_req.csv
    file into the database"""

    print "Loading groups and their nutrient requirements..."

    # Reads the csv and inserts it.
    with open('seed_data/group_nutrient_req.csv') as csvfile:
        read_line = csv.reader(csvfile, delimiter=',')  # Must read before for loop

        for row in read_line:
            # Skips over the first line of code which has labels on it
            if row[0] == 'Nutrient no':
                continue
            else:
                # Assign parameters to the data and change to the correct datatype
                # Do I also assign id?
                group_req = Group_Nutrient(nutri_id=int(row[0]),
                                           group_id=int(row[1]),
                                           req_amt=float(row[2]),
                                           upper_lim=row[3])
            db.session.add(group_req)

    db.session.commit()


def update_pkey_seqs():
    """Set primary key for each table to start at one higher than the current
    highest key. Helps when data has been manually seeded."""

    # get a dictionary of {classname: class} for all classes in model.py
    model_classes = db.Model._decl_class_registry

    # loop over the classes
    for class_name in model_classes:

        # the dictionary will include a helper class we don't care about, so
        # skip it
        if class_name == "_sa_module_registry":
            continue
        elif class_name == "Food":
            continue
        elif class_name == "Nutrient":
            continue

        print
        print "-" * 40
        print "Working on class", class_name

        # get the class itself out of the dictionary
        cls = model_classes[class_name]

        # get the name of the table associated with the class and its primary
        # key
        table_name = cls.__tablename__
        pkey_column = inspect(cls).primary_key[0]
        primary_key = pkey_column.name
        print "Table name:", table_name
        print "Primary key:", primary_key

        # check to see if the primary key is an integer (which are
        # autoincrementing by default)
        # if it isn't, skip to the next class
        if (not isinstance(pkey_column.type, db.Integer) or
            pkey_column.autoincrement is not True):
            print "Not an autoincrementing integer key - skipping."
            continue

        # now we know we're dealing with an autoincrementing key, so get the
        # highest id value currently in the table
        result = db.session.query(func.max(getattr(cls, primary_key))).first()

        # if the table is empty, result will be none; only proceed if it's not
        # (we have to index at 0 since the result comes back as a tuple)
        if result[0]:
            # cast the result to an int
            max_id = int(result[0])
            print "highest id:", max_id

            # set the next value to be max + 1
            query = ("SELECT setval('" + table_name + "_" + primary_key +
                     "_seq', :new_id)")
            db.session.execute(query, {'new_id': max_id + 1})
            db.session.commit()
            print "Primary key sequence updated."
        else:
            print "No records found. No update made."

    # we're done!
    print
    print "-" * 40
    print
    print "Primary key sequences updated!"
    print


if __name__ == "__main__":
    # Import os so you don't have to drop and create tables in terminal
    import os
    os.system("dropdb nutrireq")
    os.system("createdb nutrireq")

    # If this file is called, connect to the db
    app = Flask(__name__)
    connect_to_db(app)

    # Creates tables if they don't exist, otherwise nothing; don't need to rerun
    # model.py
    db.create_all()

    # Calls all the db loading functions
    load_groups()
    load_nutri_no()
    load_group_nutrient()
    update_pkey_seqs()
