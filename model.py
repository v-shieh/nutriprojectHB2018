"""Model and database for nutrireq db"""
# Boiler plate code to import SQLALchemy and make the idea of the db. The db = SQLAlchemy() allows us to
# use the db.commit/db.add commands

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

######################################Table Creation############################################


class User(db.Model):
    """User model"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        primary_key=True,
                        autoincrement=True)
    fname = db.Column(db.String(20),
                      nullable=False)
    lname = db.Column(db.String(20),
                      nullable=False)
    email = db.Column(db.String(60),
                      nullable=False,
                      unique=True)
    pw = db.Column(db.String(60),
                   nullable=False)
    gender_at_birth = db.Column(db.String(1),
                                nullable=False)
    age = db.Column(db.Integer,
                    nullable=False)
    group_id = db.Column(db.Integer,
                         db.ForeignKey('groups.group_id'))

    group = db.relationship('Group')
    food_eaten = db.relationship('Food_Eaten')

    # Connected to: Group
    # This has a User-Group double relationship

    def __repr__(self):
        """Show user information"""

        return "<User id={id_no} | name={first} {last} | email={email} | group id = {g_id}>".format(id_no=self.user_id,
                                                                                                    first=self.fname,
                                                                                                    last=self.lname,
                                                                                                    email=self.email,
                                                                                                    g_id=self.nutri_group_id)


class Group(db.Model):
    """Group model which gives nutritional requirements about a specific age/gender group"""

    __tablename__ = "groups"

    group_id = db.Column(db.Integer,
                         primary_key=True,
                         autoincrement=True)
    group_name = db.Column(db.String(50),
                           nullable=False)
    min_age = db.Column(db.Integer,
                        nullable=False)
    max_age = db.Column(db.Integer,
                        nullable=False)
    gender = db.Column(db.String(1),
                       nullable=False)

    user = db.relationship('User')

    # Connected to: Groups
    # This has a User-Group double relationship

    def __repr__(self):
        """Show info about nutrient groups based on gender and age group"""

        return "<Group id={id} | range={min}-{max} | gender={gender}>".format(id=self.group_id,
                                                                              min=self.min_age,
                                                                              max=self.max_age,
                                                                              gender=self.gender)


class Nutrient(db.Model):
    """Nutrient model"""

    __tablename__ = "nutrients"

    nutri_id = db.Column(db.Integer,
                         primary_key=True)
    nutri_name = db.Column(db.String(256),
                           unique=True,
                           nullable=False)
    # Some nutrients may be nonexistant for a specific food
    recom_unit = db.Column(db.String(256),
                           nullable=False)

    # Connected to: Nutrient-Food, Nutrient-Group
    # This has a single relationshop in the association tables found above
    # Only has home parameters being id and name because it is separate from foods and connected to Nutrient-Food

    def __repr__(self):
        """Show info about specific nutrient"""

        return "<Nutrient id={id} | name={name} | unit={unit}>".format(id=self.nutri_id,
                                                                       name=self.nutri_name,
                                                                       unit=self.recom_unit)


class Food(db.Model):
    """Food model"""

    __tablename__ = "foods"

    food_id = db.Column(db.String(256),
                        nullable=False,
                        primary_key=True,
                        unique=True)
    food_name = db.Column(db.String(256),
                          nullable=False,
                          unique=True)
    food_serving = db.Column(db.Float,
                             nullable=False)
    food_serving_unit = db.Column(db.String(256),
                                  nullable=False)
    # food_desc = db.Column(db.String(256),
    #                       nullable=True)

    # Connected to: Nutrient-Food
    # This has a single relationshop in the association tables found above

    def __repr__(self):
        """Show info about a specific food"""

        return "<Food id={id} | name={name} | serving={serving} | unit={unit}>".format(id=self.food_id,
                                                                                       name=self.food_name,
                                                                                       serving=self.food_serving,
                                                                                       unit=self.food_serving_unit)


class Group_Nutrient(db.Model):
    """Association table linking the groups and nutrients tables"""

    __tablename__ = "group_nutrients"

    nutrigroup_link_id = db.Column(db.Integer,
                                   primary_key=True,
                                   autoincrement=True)
    nutri_id = db.Column(db.Integer,
                         db.ForeignKey('nutrients.nutri_id'))
    group_id = db.Column(db.Integer,
                         db.ForeignKey('groups.group_id'))
    req_amt = db.Column(db.Integer,
                        nullable=False)
    # recom_unit = db.Column(db.String(256),
    #                        nullable=False)
    upper_lim = db.Column(db.String(1),
                          default='f')

    nutrient = db.relationship('Nutrient', backref='group_nutrients')
    group = db.relationship('Group', backref='group_nutrients')

    # Lesson 1: You do need repr-s for everything, even association tables

    def __repr__(self):
        """Show info about nutrient requirements in relation to their groups"""

        return "<Group id={id} | Nutrient={n_id} | Amt: {amt} {unit}>".format(id=self.group_id,
                                                                              n_id=self.nutrient.nutri_name,
                                                                              amt=self.req_amt,
                                                                              unit=self.recom_unit)
# can i request the nutrient name here?


class Nutrient_Food(db.Model):
    """Association table linking the foods and nutrients tables"""

    __tablename__ = "nutrient_food"

    nutrifood_link_id = db.Column(db.Integer,
                                  primary_key=True,
                                  autoincrement=True)
    nutri_id = db.Column(db.Integer,
                         db.ForeignKey('nutrients.nutri_id'))
    # nutri_name = db.Column(db.String(256),
    #                        db.ForeignKey('nutrients.nutri_name'))
    food_id = db.Column(db.String(20),
                        db.ForeignKey('foods.food_id'))
    amt_nutri_in_food = db.Column(db.Float(20))

    nutrient = db.relationship('Nutrient', backref='nutrient_food')
    food = db.relationship('Food', backref='nutrient_food')

    def __repr__(self):
        """Show info about foods and their nutrients"""

        return "<Food={foodname} | Nutrient={nutriname}>".format(foodname=self.food.food_name,
                                                                 nutriname=self.nutrient.nutri_name)


class Food_Eaten(db.Model):
    """
    Table that holds JSONified foods that a specific user(id) has eaten along with
    a date stamp
    """

    __tablename__ = "food_logs"

    entry_id = db.Column(db.Integer,
                         primary_key=True,
                         unique=True)
    # date_entered = db.Column(db.DateTime,
    #                          nullable=False,
    #                          default="ISO, DMY")
    date_entered = db.Column(db.String(8),
                             nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'))
    entry = db.Column(db.String(10000),
                      nullable=False)

    user = db.relationship('User')

    def __repr__(self):
        """Show info about food entries"""

        return "<Date Entered={date} | User={id}>".format(date=self.date_entered,
                                                          nutriname=self.user.user_id)

################################################################################################
def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///nutrireq'
    app.config['SQLALCHEMY_ECHO'] = False  # Marked 'True' for now for better debugging
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)  # Now app and db know about eachother!

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.

    connect_to_db(app)
    print "Connected to DB."
