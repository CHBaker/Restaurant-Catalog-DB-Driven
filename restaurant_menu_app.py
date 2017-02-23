# import flask class from Flask library
from flask import(Flask,
                  render_template,
                  url_for, request,
                  redirect, flash, jsonify,)

# create instance of flask class with name of app as argument
app = Flask(__name__)

# import restuarant db
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# start db session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


@app.route('/', '/restaurants')
def restaurantsHome():


@app.route('/restaurant/new')
def restaurantNew():


@app.route('/restaurant/<int:restaurant_id>/edit')
def restaurantEdit():


@app.route('/restaurant/<int:restaurant_id>/delete')
def restaurantDelete():


@app.route('/restaurant/<int:restaurant_id>/menu',
		  '/restaurant/<int:restaurant_id>')
def restaurantMenu():


@app.route('/restaurant/<int:restaurant_id>/menu/new')
def retaurantMenuNew():


@app.route('''/restaurant/<int:restaurant_id>/menu 
			  /<int:menu_id>/edit''')
def restaurantMenuEdit():


@app.route('''/restaurant/<int:restaurant_id>/menu
			  /<int:menu_id/delete''')
def restaurantMenuDelete():


# main app running is named __main__ all others named __name__
if __name__ == '__main__':
    # reloads page when code changes
    app.debug = True
    # flash uses to create sessions for users, normally hashed pass
    app.secret_key = 'super_secret_key'
    # runs unless this file is imported
    app.run(host = '0.0.0.0', port = 5000)