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



# landing page shows all restaurants
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)


@app.route('/restaurant/new')
def newRestaurant():
    return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('editRestaurant.html', restaurant = restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('deleteRestaurant.html', restaurant = restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id = restaurant.id).all()
    return render_template('menu.html', restaurant = restaurant, menu = menu)


@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('newMenu.html', restaurant = restaurant)


@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenu(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    return render_template('editMenu.html', restaurant = restaurant, menu = menuItem)


@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenu(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    return render_template('deleteMenu.html', restaurant = restaurant, menu = menuItem)


# main app running is named __main__ all others named __name__
if __name__ == '__main__':
    # reloads page when code changes
    app.debug = True
    # flash uses to create sessions for users, normally hashed pass
    app.secret_key = 'super_secret_key'
    # runs unless this file is imported
    app.run(host = '0.0.0.0', port = 5000)