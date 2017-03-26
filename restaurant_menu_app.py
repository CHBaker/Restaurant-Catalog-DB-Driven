# import flask class from Flask library
from flask import(Flask,
                  render_template,
                  url_for, request,
                  redirect, flash, 
                  jsonify, make_response)

# auth sessions
from flask import session as login_session
import random, string

# import restuarant db
from database_setup import(Base, Restaurant, 
                           MenuItem, User)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# OAUTH2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# JSON OAUTH
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# create instance of flask class with name of app as argument
app = Flask(__name__)

# start db session
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
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


# auth handler for facebook login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(
            json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=' \
          'fb_exchange_token&client_id=%s&client_secret=' \
          '%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me?fields=name,id,email"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' \
          % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access:%s"% url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session 
    # in order to properly logout, let's strip out the
    # information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?' \
          '%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: ' \
                '300px;border-radius: 150px;-webkit-border-radius: ' \
                '150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# facebook logout
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
          % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# gconnect API OATH2 handler provided by udacity
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(
            json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data

    try:
        # upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps(
                'Failed to upgrade the authorization code.'),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(
            json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps(
                "Token's client ID does not match app's."),
            401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None \
        and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #check if we need to create new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:' \
                '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# google logout
def gdisconnect():
    access_token = login_session['access_token']

    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        login_session.clear()
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# logout based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            login_session.clear()
        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            login_session.clear()
        flash("You have successfully been logged out.")
        return redirect(url_for('showRestaurants'))
        print "success"
    else:
        flash("You were not logged in")
        return redirect(url_for('showRestaurants'))
        print "failed"


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
    restaurants = session.query(Restaurant).order_by(Restaurant.name).all()

    if 'username' not in login_session:
        return render_template('public_restaurants.html', restaurants=restaurants)
    else:
        try:
            creator = login_session['user_id']
        except:
            creator = None

    return render_template('restaurants.html', restaurants=restaurants, 
                           creator=creator, username=login_session['username'],
                           profile_pic=login_session['picture'])


# user's restuarants
@app.route('/myrestaurants')
def myRestaurants():
    if "username" in login_session:
        user_id = login_session['user_id']
        restaurants = session.query(Restaurant).filter_by(
            user_id=user_id).order_by(Restaurant.name).all()
    # authorize user
    elif "username" not in login_session:
        return redirect('/login')
    else:
        for r in restaurants:
            if login_session['user_id'] != r.user_id:
                return make_response(json.dumps(
                    'ERROR 403, <br> ACCESS DENIED'), 403)

    try:
        creator = login_session['user_id']
    except:
        creator = None

    return render_template('myRestaurants.html', restaurants=restaurants,
                           username=login_session['username'],
                           creator=creator, profile_pic=login_session['picture'])


@app.route('/about')
def about():
    if 'username' not in login_session:
        return render_template('about.html')
    else:
        return render_template('about.html', username=login_session['username'],
                               profile_pic=login_session['picture'])


# create new restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if "username" not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        # place holder for regex to define form input
        if request.form['name'] != '':
            name = request.form['name']
            newRestaurant = Restaurant(
                name=name, user_id=login_session['user_id'])
            session.add(newRestaurant)
            session.commit()
            flash("The Restaurant %s was created!" % name)
            return redirect(url_for('showRestaurants'))

    return render_template('newRestaurant.html', 
                           username=login_session['username'],
                           profile_pic=login_session['picture'])


# edit existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if "username" not in login_session:
        return redirect('/login')
    elif login_session['user_id'] != restaurant.user_id:
        return make_response(json.dumps(
            'ERROR 403, <br> ACCESS DENIED'), 403)

    if request.method == 'POST':
        # place holder for regex to define form method
        if request.form['name'] != '':
            restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash("Your restaurant name has been updated to %s!" % restaurant.name)
        return redirect(url_for('showRestaurants'))

    return render_template('editRestaurant.html', restaurant_id=restaurant_id,
                           restaurant=restaurant, username=login_session['username'],
                           profile_pic=login_session['picture'])


# delete existing restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if "username" not in login_session:
        return redirect('/login')
    elif login_session['user_id'] != restaurant.user_id:
        return make_response(json.dumps(
            'ERROR 403, <br> ACCESS DENIED'), 403)

    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash("Your restaurant %s has been deleted!" % restaurant.name)
        return redirect(url_for('showRestaurants'))

    return render_template('deleteRestaurant.html', restaurant=restaurant,
                           username=login_session['username'],
                           profile_pic=login_session['picture'])


# show menu for specified restaurant
@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()

    if "username" not in login_session:
        return render_template('public_menu.html', 
                               restaurant=restaurant, 
                               menu=menu)

    elif restaurant.user_id != login_session['user_id']:
        return render_template('public_menu.html', 
                               restaurant=restaurant, 
                               menu=menu, username=login_session['username'],
                               profile_pic=login_session['picture'])
    else:
        return render_template('menu.html', restaurant=restaurant, 
                               menu=menu, username=login_session['username'],
                               profile_pic=login_session['picture'])


# create new menu item for specified restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if "username" not in login_session:
        return redirect('/login')
    elif login_session['user_id'] != restaurant.user_id:
        return make_response(json.dumps(
            'ERROR 403, <br> ACCESS DENIED'), 403)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        course = request.form['course']
        if name and description and price and course:
            menu = MenuItem(name=name, restaurant_id=restaurant_id,
                            description=description, price=price,
                            course=course, user_id=login_session['user_id'])
            session.add(menu)
            session.commit()
            flash("%s has been created as a new menu item!" % name)
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))
        else:
            error = "Oops! you are missing some information"
            return render_template('NewMenu.html', restaurant_id=restaurant_id,
                                   restaurant=restaurant, error=error,
                                   username=login_session['username'],
                                   profile_pic=login_session['picture'])

    return render_template('newMenu.html', restaurant_id=restaurant_id,
                           restaurant=restaurant, 
                           username=login_session['username'],
                           profile_pic=login_session['picture'])


# edit menu item for specified restaurant
@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
    methods=['GET', 'POST'])
def editMenu(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()

    if "username" not in login_session:
        return redirect('/login')
    elif login_session['user_id'] != restaurant.user_id:
        return make_response(json.dumps(
            'ERROR 403, <br> ACCESS DENIED'), 403)

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
        else:
            error = "Oops! you are missing some information"
            menuItem.name = request.form['name']
            menuItem.description = request.form['description']
            menuItem.price = request.form['price']
            menuItem.course = request.form['course']
            return render_template('NewMenu.html', restaurant_id=restaurant_id,
                                   restaurant=restaurant, name=name,
                                   description=description, price=price,
                                   course=course, error=error,
                                   username=login_session['username'],
                                   profile_pic=login_session['picture'])

    return render_template('editMenu.html', restaurant=restaurant,
                           menu=menuItem, username=login_session['username'],
                           profile_pic=login_session['picture'])


# delete menu item for specified restaurant
@app.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
    methods=['GET', 'POST'])
def deleteMenu(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()

    if "username" not in login_session:
        return redirect('/login')
    elif login_session['user_id'] != restaurant.user_id:
        return make_response(json.dumps(
            'ERROR 403, <br> ACCESS DENIED'), 403)

    if request.method == 'POST':
        session.delete(menuItem)
        session.commit()
        flash("%s has been deleted from the menu!" % menuItem.name)
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    return render_template('deleteMenu.html', restaurant=restaurant,
                           menu=menuItem, username=login_session['username'],
                           profile_pic=login_session['picture'])

# helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], 
        picture=login_session['picture'])
    print 'NEW USER', newUser
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def loggedIn(login_session):
    if login_session:
        return True

# main app running is named __main__ all others named __name__
if __name__ == '__main__':
    # reloads page when code changes
    app.debug = True
    # flash uses to create sessions for users, normally hashed pass
    app.secret_key = 'super_secret_key'
    # runs unless this file is imported
    app.run(host='0.0.0.0', port=5000)





