# Requirements
This project was created with the following dependencies, but could run fine with other versions of python3 and compatible libraries  
`python=3.4`  
`flask=0.12.2`  
`sqlalchemy=1.1.11`  
`oauth2client=4.1.2`  

This project is deployed on amazon lightsail. The server is not kept up continuously.  

# Setup

Run the following commands to setup the database:  
-`python3 database_setup.py` -- Creates the database and sqlalchemy orm mapping. WARNING, DELETES EXISTING DATABASE OF THE SAME NAME (sqlite:///user_item_catalog.db) BEFORE CREATING  

-`python3 add_test_user.py` -- Adds test_user to the database, which can be accessed at any time by accessing the localhost:8080/test after running the server. test_user's id is `"TEST"` and username is `"test_user"`.  

# Usage

Run the following command to start the server:  

`python3 item_catalog_server.py`  
The server can be reached at localhost:8080
  

# Debugging  

The database can be directly queried by running"
`python3 -i query_database.py`  

# API

The following routes can be used to access a JSON api. 
You must be authenticated (login with google) in order to interact with the api. Or you can login to the test_user at localhost:8080/test. Again, test_user's user_id is `"TEST"`  

- User Catalog: localhost:8080/user/<string:user_id>/JSON
- Get Item: localhost:8080/user/<string:user_id>/<int:item_id>/get/JSON
- Add Item: localhost:8080/user/<string:user_id>/new/JSON/
- Edit Item: localhost:8080/user/<string:user_id>/<int:item_id>/edit/JSON
- Delete Item: localhost:8080/user/<string:user_id>/<int:item_id>/delete/JSON