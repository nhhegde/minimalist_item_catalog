## Server Currently Paused, not accepting new connections. 

## How to Login to [ubuntu]
`./ssh_login`

Which runs:

`ssh [ubuntu]@34.208.64.45 -i user_key -p 2200`
### Password: "thebest[ubuntu]ever" to run sudo. Note: this does require a private key to authenticate. Password authentication has been disabled.

## Query the database
How to query the sqlite database using sqlalchemy.

1. login to [ubuntu]
2. cd to ~/app/a2/minimalist_item_catalog/Item_Catalog
3. run python3 -i query_database.py

I recommend starting with:
`test_user = session.query(User).filter_by(id="TEST").one()`
`items = session.query(Item).filter_by(user_id=test_user.id).all()`
`items[0].name`

## Access the web app
Open a web browser and navigate to: 
http://34.208.64.45.xip.io
(I had to use xip.io because Google oauth requres a non-ip hostname, http://34.208.64.45 will not work for logging in, the redirect will break)

WARNING: THIS APP CANNOT BE ACCESSED OVER HTTPS AND USES GOOGLE OAUTH FOR AUTHENTICATION. IF YOU DON'T WANT TO RISK LEAKING YOUR GOOGLE+ ID I RECOMMEND USING A NEW ACCOUNT THAT YOU DON'T CARE ABOUT. 

# Server info

nginx + gunicorn. 

#### Create user: [ubuntu], password: thebest[ubuntu]ever
sudo adduser [ubuntu]
sudo usermod -aG sudo [ubuntu]
sudo login [ubuntu]


######## ssh-keygen
*don't use sudo, permissions aren't the right ones*
mkdir .ssh
touch .ssh/authorized_keys
nano .ssh/authorized_keys
copy [ubuntu]_key to /home/.ssh/authorized_keys
*This step caused problems on lightsail, although it was recommended: chmod 700 .ssh*
sudo chmod 644 .ssh/authorized_keys
#try logging in




#### Ports
sudo nano /etc/ssh/sshd_config
# Set Port 2200, PermitRootLogin no, PasswordAuthentication is already no
# Set custom tcp port 2200 on lightsail

sudo service ssh status
sudo service ssh restart

#### firewalls
`sudo ufw status
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 2200/tcp
sudo ufw allow www
sudo ufw allow ntp

sudo ufw allow from {your-ip-address}
sudo ufw enable`
check if everything still works from a different ip

`sudo ufw delete allow from {your-ip-address}.`









# setup server
`sudo apt-get update
sudo apt-get upgrade
sudo apt-get install nginx
pip3 install gunicorn
pip3 install flask sqlalchemy requests oauth2client`

xip.io was setup because I used google for authentication and 

# Reconfigure timezone
sudo dpkg-reconfigure tzdata
To switch to UTC, execute sudo dpkg-reconfigure tzdata , scroll to the bottom of the Continents list and select Etc or None of the above ; in the second list, select UTC


# download and setup project



`mkdir ~/app/a2
cd ~/app/a2
git clone git://github.com/nhhegde/minimalist_item_catalog.git`

nginx config in /etc/nginx/sites-available/default
`cd minimalist_item_catalog
sudo cp default /etc/nginx/sites-available/default
sudo service nginx start
sudo service nginx status`

Run gunicorn
`cd ~/app/a2/minimalist_item_catalog/Item_Catalog
gunicorn -w 4 item_catalog_server:app & --daemon`
Note this is already running. (gunicorn -w 4 item_catalog_server:app)


Resources 

Why I decided not to use Apache2:

- http://devmartin.com/blog/2015/02/how-to-deploy-a-python3-wsgi-application-with-apache2-and-debian/
- https://unix.stackexchange.com/questions/257590/ssh-key-permissions-chmod-settings
- http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/
- https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
- http://terokarvinen.com/2016/deploy-flask-python3-on-apache2-ubuntu
https://modwsgi.readthedocs.io/en/develop/

gunicorn: 

- https://stackoverflow.com/questions/13654688/what-is-the-correct-way-to-leave-gunicorn-running
- http://docs.gunicorn.org/en/stable/

https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&ved=0ahUKEwjN7tHPkr7VAhVlHGMKHZ24B7kQFggrMAE&url=https%3A%2F%2Faskubuntu.com%2Fquestions%2F138423%2Fhow-do-i-change-my-timezone-to-utc-gmt&usg=AFQjCNEY08eOopOoscoXSgMXodGlr7bgFA
