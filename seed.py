"""File to seed group information about nutritional requirements based on gender and age"""


# from sqlalchemy import func
from model import User, Nutrigroup, Nutrient, Food, Group_Nutrient, Nutrient_Food
from model import connect_to_db, db
from server import app

import csv


def load_groups():
    """Load groups from the group.csv file into the database"""

    print "Loading groups..."

    # Deletes all rows if they exist to avoid duplication
    Nutrigroup.query.delete()

    # Reads the csv and inserts it.
    with open('seed_data/group_type.csv') as csvfile:
        read_line = csv.reader(csvfile, delimiter=',')  # Must read before for loop

        for row in read_line:
            # Skips over the first line of code which has labels on it
            if row[0] == 'ID':
                continue
            else:
                # Assign parameters to the data and change to the correct datatype
                group = Nutrigroup(group_id=int(row[0]),
                                   group_name=row[1],
                                   min_age=int(row[2]),
                                   max_age=int(row[3]),
                                   gender=row[4])

        db.session.add(group)

    db.session.commit()


def load_nutri_no():
    """Load nutrient name and number from the nutrientname_no.csv file into the database"""

    print "Loading nutrients and their numbers..."

    # Deletes all rows if they exist to avoid duplication
    Nutrient.query.delete()

    # Reads the csv and inserts it.
    with open('seed_data/nutrientname_no.csv') as csvfile:
        read_line = csv.reader(csvfile, delimiter=',')  # Must read before for loop

        for row in read_line:
            # Skips over the first line of code which has labels on it
            if row[0] == 'Name':
                continue
            else:
                # Assign parameters to the data and change to the correct datatype
                nutrient = Nutrient(nutrient_id=int(row[0]),
                                    nutri_name=row[1])

        db.session.add(nutrient)

    db.session.commit()





if __name__ == "__main__":
    # If this file is called, connect to the db
    connect_to_db(app)

    # Creates tables if they don't exist, otherwise nothing
    db.create_all()

    # Calls all the db loading functions
    load_groups()
