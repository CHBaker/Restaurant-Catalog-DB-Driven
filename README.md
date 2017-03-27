# Restaurant Catalog 
    Database Driven Restaurant/Menu app in 
    Flask, Python, sqlAlchemy
    
# DOCUMENTATION
    Full documentation viewable at 
    https://github.com/CHBaker/Restaurant-Catalog-DB-Driven
    
# INSTALLATION
    1] Download or clone full GitHub repo
    2] Download python to your command line
    3] Download Vagrant
    4] Download Virtual Box
    
# CONFIGURATION
    1] Make sure the project is located within the vagrant directory
    2] Get Vagrant and Virtual Box up and running
    3] Navigate to the vagrant directory, then to the project directory
    4] Inside the project directory, run ```python restaurantmenuwithuser.db```
       to initialize the database
    5] Inside the project directory, run ```python lotsofmenususers.py```
       to populate the database with restaurants created by users
    6] Inside the project directory, run ```python restaurant_menu_app.py```
    7] This will get the local host up and running, visit the configured local host
       address (default is port 5000)
       
# OPERATING INSTRUCTIONS
    This app is easy to use, login using a Google/Facebook 
    account, and create your restaurants and menu items. 
    You may also view current restaurants publicly with out 
    being able to modify them.
    
# FILE MANIFEST
    
    catalog-final/static/images/floral.jpg
                                profile.jpg
                                
    catalog-final/static/js/bootstrap.min.js
    
    catalog-final/static/bootstrap.min.css
                         bootstrap.min.css.map
                         side.css
                         
    catalog-final/templates/about.html
                            base.html
                            deleteMenu.html
                            deleteRestaurant.html
                            editMenu.html
                            editRestaurant.html
                            login.html
                            main.html
                            menu.html
                            myRestaurants.html
                            newMenu.html
                            newRestaurant.html
                            public_menu.html
                            public_restaurants.html
                            restaurants.html
                            
    catalog-final/client_secrets.json
                  database_setup.py
                  database_setup.pyc
                  fb_client_secrets.json
                  lotsofmenus.py
                  lotsofmenususers.py
                  restaurant_menu_app.py
                  restaurantmenu.db
                  restaurantmenuwithuser.db
