"""Main server file for the nutrition web app"""

from jinja2 import StrictUndefined
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db

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


@app.route('/search')
def search():
    """Takes in input and sends it to the function which determines location"""

    return render_template('search.html')

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
