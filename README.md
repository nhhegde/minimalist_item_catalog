# Requirements
This project was created with the following dependencies, but could run fine with other versions of python3 and compatible libraries  
`python=3.4`  
`flask=0.12.2`  
`sqlalchemy=1.1.11`  
`oauth2client=4.1.2`  
`postgresql=9.6`  
`psycopg2=2.7.3`  

The use of a virtual environment is recommended for installation. 


## Access the web app
Open a web browser and navigate to:  
http://34.208.64.45.xip.io
This project is deployed on amazon lightsail. The server is not kept up continuously. xip.io provides wildcard DNS for any IP address, and was necessary because google oauth requires a non-ip domain name and I do not have one set up for this site at the moment. 

WARNING: THIS SITE CANNOT BE ACCESSED OVER HTTPS AND USES GOOGLE OAUTH FOR AUTHENTICATION. IF YOU DON'T WANT TO RISK LEAKING YOUR GOOGLE+ ID I RECOMMEND USING A NEW ACCOUNT THAT YOU DON'T CARE ABOUT.  

# Setup

- Install postgresql, make sure the psql server is running on port 5432.
- Create the database `user_item_catalog`
- Add the current user to the psql server (give the current user permission to use the database). 
- Update the database url used by sqlalchemy. See database_setup.py for details. The url should be stored in an import but is not at the moment. You will need to change every python file with the url. 

Run the following commands to setup the database:  
-`python3 database_setup.py` -- Creates sqlalchemy orm mapping. WARNING, DELETES EXISTING TABLES OF THE SAME NAME AND THEN RE-CREATES THOSE TABLES. 

-`python3 add_test_user.py` -- Adds test_user to the database, which can be accessed at any time by accessing the localhost:8080/test after running the server. test_user's id is `"TEST"` and username is `"test_user"`.  

# Usage

Run the following command to start the server:  

`python3 item_catalog_server.py`  
The server can be reached at localhost:8080
  

# Debugging  

The database can be directly queried by running  
`python3 -i query_database.py`  

# API

The following routes can be used to access a JSON api. 
You must be authenticated (login with google) in order to interact with the api. Or you can login to the test_user at localhost:8080/test. Again, test_user's user_id is `"TEST"`  

- User Catalog: localhost:8080/user/<string:user_id>/JSON
- Get Item: localhost:8080/user/<string:user_id>/<int:item_id>/get/JSON
- Add Item: localhost:8080/user/<string:user_id>/new/JSON/
- Edit Item: localhost:8080/user/<string:user_id>/<int:item_id>/edit/JSON
- Delete Item: localhost:8080/user/<string:user_id>/<int:item_id>/delete/JSON