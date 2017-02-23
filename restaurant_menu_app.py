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


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    return "this page will show my restaurants"


@app.route('/restaurant/new')
def newRestaurant():
    return "this page will be for making a new restaurant"

@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    return "this page will be for editing restaurant '%s'" % restaurant_id


@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    return "this page will be for deleting restaurant '%s'" % restaurant_id


@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>')
def showMenu(restaurant_id):
    return "this page will show the menu for the restaurant '%s'" % restaurant_id


@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenu(restaurant_id):
    return "this page will be for adding a new menu item for the restaurant '%s'" % restaurant_id


@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenu(restaurant_id, menu_id):
    return "this page will be for editing menu item '%s'" % menu_id


@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenu(restaurant_id, menu_id):
    return "this page will be for deleting menu item  '%s'" % menu_id


# main app running is named __main__ all others named __name__
if __name__ == '__main__':
    # reloads page when code changes
    app.debug = True
    # flash uses to create sessions for users, normally hashed pass
    app.secret_key = 'super_secret_key'
    # runs unless this file is imported
    app.run(host = '0.0.0.0', port = 5000)