"""Model and database for nutrireq db"""
# Boiler plate code to import SQLALchemy and make the idea of the db. The db = SQLAlchemy() allows us to
# use the db.commit/db.add commands

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

######################################Table Creation############################################

class User(db.Model):
    """User model"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        primary_key=True,
                        autoincrement=True)**
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
    "nutri_group_id = dbColumn" **

    def __repr__(self):
        """Show user information"""

        return "<User id={id_no} | name={first} {last} | email={email} | group id = {g_id}>".format(id_no=self.user_id,
                                                                                                    first=self.fname,
                                                                                                    last=self.lname,
                                                                                                    email=self.email,
                                                                                                    g_id=self.nutri_group_id)


class Nutrigroup(db.Model):
    """Group model"""

    __tablename__ = "nutrigroups"

    group_id = db.Column(db.Integer,
                         primary_key=True,
                         autoincrement=True)**
    age_range = db.Column(db.Integer,
                          nullable=False)
    gender = dbColumn(db.String(1),
                      nullable=False)

    def __repr__(self):
        """Show info about nutrient groups based on gender and age group"""

        return "<Nutrigroup id={group_id} | range={age} | gender={gender}>".format(group_id=self.group_id,
                                                                                   age=self.age_range,
                                                                                   gender=self.gender)


class Nutrient(db.Model):
    """Nutrient model"""

    __tablename__ = "nutrients"

    nutrient_id = db.Column(db.Integer,
                            primary_key=True,
                            autoincrement=True)**
    nutri_name = db.Column(db.String(20),
                           unique=True,
                           nullable=False)
    nutri_serving = db.Column(db.Integer,
                              nullable=False)
    recom_unit = db.Column(db.String)**

    def __repr__(self):
        """Show info about specific nutrient"""

        return "<Nutrient id={nutri_id} | name={name} | unit={unit}>".format(nutri_id=self.nutrient_id,
                                                                             name=self.nutri_name
                                                                             unit=self.recom_unit)





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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///animals'
    app.config['SQLALCHEMY_ECHO'] = True  # Marked 'True' for now for better debugging
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)  # Now app and db know about eachother!

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
