# import flask class from Flask library
from flask import(Flask,
                  render_template,
                  url_for, request,
                  redirect, flash, jsonify)

# auth sessions
from flask import session as login_session
import random, string

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


# create a state token to prevent request forgery
# store it in session for later validation
@app.route('/login')
def showLogin():
    #string of random uppercase letters/digits
    state=''.join(random.choice(
        string.ascii_uppercase + \
        string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# API endpoint (GET request) for all restaurant's
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serialize for i in restaurants])


# API endpoint (GET request) for restaurant's full menu
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


# API endpoint (GET request) for restaurant's single menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=[menuItem.serialize])


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


    # place holder for regex to define form input
    def validForm(name, description, price, course):
        if name != '' and description != '' \
           and price != '' and course != '':
            return True
        return False


    if request.method == 'POST':
        if validForm(request.form['name'], request.form['description'],
                     request.form['price'], request.form['course']):
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            course = request.form['course']
            menu = MenuItem(name=name, restaurant_id=restaurant_id,
                            description=description, price=price,
                            course=course)
            session.add(menu)
            session.commit()
            flash("%s has been created as a new menu item!" % name)
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))
        else:
            error = "Oops! you are missing some information"
            return render_template('NewMenu.html', restaurant_id=restaurant_id,
                                   restaurant=restaurant, name=name,
                                   description=description, price=price,
                                   course=course, error=error)

    return render_template('newMenu.html', restaurant_id=restaurant_id,
                           restaurant=restaurant)


# edit menu item for specified restaurant
@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
    methods=['GET', 'POST'])
def editMenu(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()


    def validForm(name, description, price, course):
        if name != '' and description != '' \
           and price != '' and course != '':
            return True
        return False


    if request.method == 'POST':
        if validForm(request.form['name'], request.form['description'],
                     request.form['price'], request.form['course']):
            menuItem.name = request.form['name']
            menuItem.description = request.form['description']
            menuItem.price = request.form['price']
            menuItem.course = request.form['course']
            session.add(menuItem)
            session.commit()
            flash("%s has been added to the menu!" % menuItem.name)
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





