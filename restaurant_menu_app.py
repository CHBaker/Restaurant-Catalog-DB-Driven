# import flask class from Flask library
from flask import(Flask,
                  render_template,
                  url_for, request,
                  redirect, flash, jsonify,)

# import restuarant db
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# create instance of flask class with name of app as argument
app = Flask(__name__)

# start db session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# landing page shows all restaurants
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


# create new restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        # place holder for regex to define form input
        if request.form['name'] != '':
            name = request.form['name']
            newRestaurant = Restaurant(
                name=name)
            session.add(newRestaurant)
            session.commit()
            flash("The Restaurant %s was created!" % name)
            return redirect(url_for('showRestaurants'))

    return render_template('newRestaurant.html')


# edit existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if request.method == 'POST':
        # place holder for regex to define form method
        if request.form['name'] != '':
            restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash("Your restaurant name has been updated to %s!" % restaurant.name)
        return redirect(url_for('showRestaurants'))

    return render_template(
        'editRestaurant.html', restaurant_id=restaurant_id,
        restaurant=restaurant)


# delete existing restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash("Your restaurant %s has been deleted!" % restaurant.name)
        return redirect(url_for('showRestaurants'))
    return render_template('deleteRestaurant.html', restaurant=restaurant)


# show menu for specified restaurant
@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return render_template('menu.html', restaurant=restaurant, menu=menu)


# create new menu item for specified restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if request.method == 'POST':
        # place holder for regex to define form input
        if request.form['name'] != '':
            name = request.form['name']
            menu = MenuItem(name=name, restaurant_id=restaurant_id)
            session.add(menu)
            session.commit()
            flash("%s has been created as a new menu item!" % name)
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    return render_template('newMenu.html', restaurant_id=restaurant_id,
                           restaurant=restaurant)


# edit menu item for specified restaurant
@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
    methods=['GET', 'POST'])
def editMenu(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()

    if request.method == 'POST':
        if request.form['name'] != '':
            name = request.form['name']
            menuItem.name = name
            session.add(menuItem)
            session.commit()
            flash("%s has been added to the menu!" % name)
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    return render_template('editMenu.html', restaurant=restaurant,
                           menu=menuItem)


# delete menu item for specified restaurant
@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
    methods=['GET', 'POST'])
def deleteMenu(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()

    if request.method == 'POST':
        session.delete(menuItem)
        session.commit()
        flash("%s has been deleted from the menu!" % menuItem.name)
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    return render_template('deleteMenu.html', restaurant=restaurant,
                           menu=menuItem)


# main app running is named __main__ all others named __name__
if __name__ == '__main__':
    # reloads page when code changes
    app.debug = True
    # flash uses to create sessions for users, normally hashed pass
    app.secret_key = 'super_secret_key'
    # runs unless this file is imported
    app.run(host='0.0.0.0', port=5000)





