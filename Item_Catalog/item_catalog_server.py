#! usr/bin/python3
# TODO: Set up mypy, pep8 linting, extra linters,
#       sublime-linter-annotations, possibly more.
# TODO: refactor code based on code review. 
# TODO: Learn how to properly secure a web application.
#       There's a list of things you'll likely need
#       to learn in your software engineering learning
#       journal
# TODO: Add tests to make it look professional. 
# TODO: Can you think of anything else? I can't...
# TODO: Maybe verify if you oauth2 setup actually
#       uses the state variable. Maybe find a way to
#       use it.
# TODO: Add local authentication. 
# TODO: Add a setup script
# Estimate: Probably another week's worth of work. 
from flask import Flask, redirect, render_template
from flask import request, url_for, flash, jsonify  # because of pep8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, User
# login imports
from flask import session as login_session
import random
import string
# login imports for /gconnect and /gdisconnect routes
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)
app.secret_key = 'super_secret_key'
engine = create_engine('sqlite:///user_item_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

@app.route('/')
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if login_session.get('credentials') is not None and \
       stored_gplus_id is not None:  # Because this is what pep8 wants
        print('Current User is already logged in')
        response = make_response(json.dumps(
            'Current user is already connected/logged in.'), 200)
        response.headers['content-type'] = 'application/json'
        return response
    # I think the following check is pointless.
    # Lorenzo didn't implement the auth pattern properly
    # in the google oauth lesson
    # and I'm not sure how to do it myself.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'applicatiofn/json'
        return reponse
    login_session_code = request.data
    print(login_session_code)
    try:
        # uses auth code to get a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        #oauth_flow.redirect_uri = '34.208.64.45.xip.io/postLogin'
        credentials = oauth_flow.step2_exchange(login_session_code)
        access_token = credentials.access_token
        # print(access_token)
        # print(credentials)
        # print(oauth_flow)
    except FlowExchangeError as e:
        print('FlowExchangeError: {}'.format(e))
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # verify the access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
           .format(access_token))  # b/c pep8
    result = requests.get(url).json()
    print(result)
    if result.get('error') is not None:
        print('some error with the access token request.')
        response = make_response(json.dumps(result.get('error'), 500))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access_token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        print('user_id: {} != gplus_id: {} is true'.format(
            result['user_id'], gplus_id))
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        print("Token's [app_]Client_ID does not match this app's client_id")
        print('issued_to: {} != CLIENT_ID {}'.format(
            result['issued_to'], CLIENT_ID))
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # print(type(json.loads(credentials.to_json())),
    #       json.loads(credentials.to_json()))
    login_session['credentials'] = json.loads(credentials.to_json())
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['access_token'] = access_token
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    flash("You are now logged in as {}.".format(login_session['username']))
    return render_template('logged_in_flash_message.html',
                           login_session=login_session)


@app.route("/postLogin")
def post_login():
    user_id = login_session['gplus_id']

    # if user is new
    if session.query(User).filter_by(id=user_id).all() == []:
        print('no existing user, adding user to database')
        user_row = User(
            username=login_session['username'], id=user_id, password=None)
        session.add(user_row)
        session.commit()
        flash('Welcome new user!')
    return redirect(url_for('user_catalog', user_id=user_id))


def logout():
    login_session.pop('access_token', None)
    login_session.pop('gplus_id', None)
    login_session.pop('username', None)
    login_session.pop('email', None)
    login_session.pop('picture', None)


@app.route("/gdisconnect")
def gdisconnect():

    if login_session['gplus_id'] == 'TEST':
        logout()
        return make_response(json.dumps('Successfully logged out', 200))

    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps(
            'Current user not connected.', 401))
        response.headers['content-type'] = 'application/json'
        return response
    # HTTP GET request to revoke current access_token
    access_token = credentials.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Access_token is None.', 401))
        response.headers['content-type'] = 'application/json'
        logout()
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
        access_token)
    result = requests.get(url)  # .json()
    print('Get Request for revoking an access token resulted in: {}'
          .format(result))
    if result is not None:

        if result.ok:
            logout()
            response = make_response(json.dumps(
                'Successfully logged out', 200))
        else:
            logout()
            response = make_response(json.dumps(
                ('Some Error occured so I logged you'
                 'out anyways. Status code: {}.'
                 ).format(result.status_code), 200))

    else:
        print('something unexpected happened here, when trying to revoke your',
              "session's access_token the response object was None")
        print('result: {}. \n access_token: {}'.format(result, access_token))
        logout()
        response = make_response(json.dumps(
            'no idea what happened, logged you out just to be safe', 200))

    response.headers['content-type'] = 'application/json'
    return response


@app.route('/test')
def test():
    gdisconnect()
    login_session['gplus_id'] = 'TEST'
    return redirect(url_for('user_catalog', user_id='TEST'))

# @app.route('/')


@app.route('/user/<string:user_id>/')
def user_catalog(user_id):
    if user_id is None:
        return redirect(url_for('invalid_user_id'))
    if user_id != 'TEST' and \
       (
        login_session.get('gplus_id') is None or
        user_id != login_session['gplus_id']
       ):
        return redirect(url_for('invalid_user_id'))

    print("{} accessed their item catalog".format(user_id))
    # Some test code to see all users in the database
    print(session.query(User).filter_by(id=str(user_id)))
    q = session.query(User).all()
    print('All users: \n')
    for u in q:
        print('u: {}, id: {}'.format(u.username, u.id))

    # Sanity Check, user is in the database.
    # And in case I refactor the database so
    # that the gplus_id is no longer the user_id
    user = session.query(User).filter_by(id=user_id).one()
    items = session.query(Item).filter_by(user_id=user.id)
    categories = session.query(
        Item.category.distinct()).filter_by(user_id=user_id).all()
    count = session.query(Item).filter_by(user_id=user_id).count()
    categories = [c[0] for c in categories]  # unpacking column tuples
    return render_template('user_catalog.html',
                           user=user,
                           items=items,
                           categories=categories,
                           count=count
                           )


@app.route('/sneakysneaky')
def invalid_user_id():
    return "403 Access Forbidden", 403


@app.route('/user/<string:user_id>/new', methods=['GET', 'POST'])
def newItem(user_id):
    if user_id != login_session['gplus_id']:
        return redirect(url_for('invalid_user_id'))
    if request.method == 'POST':
        new_item = Item(name=request.form['name'],
                        category=request.form['category'],
                        description=request.form['description'],
                        user_id=user_id)
        session.add(new_item)
        session.commit()
        flash('New Item {} created!'.format(new_item.name))
        return redirect(url_for('user_catalog', user_id=user_id))
    else:
        return render_template('new_item.html', user_id=user_id)


@app.route('/user/<string:user_id>/<int:item_id>/view')
def viewItem(user_id, item_id):
    if user_id != login_session['gplus_id']:
        return redirect(url_for('invalid_user_id'))
    q = session.query(Item).filter_by(id=item_id)
    if q == []:
        flash('Item does not exist')
        return redirect(url_for('user_catalog', user_id=user_id))
    item = q.one()
    return render_template('view_item.html', user_id=user_id, item=item)


@app.route('/user/<string:user_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(user_id, item_id):
    print(login_session['gplus_id'])
    if user_id != login_session['gplus_id']:
        return redirect(url_for('invalid_user_id'))
    q = session.query(Item).filter_by(id=item_id)
    if q == []:
        flash('Item does not exist')
        return redirect(url_for('user_catalog', user_id=user_id))
    edit_item = q.one()
    if edit_item.user_id != login_session['gplus_id']:
        return redirect(url_for('invalid_user_id'))
    if request.method == 'POST':
        if request.form['name']:
            edit_item.name = request.form['name']
        if request.form['category']:
            edit_item.category = request.form['category']
        if request.form['description']:
            edit_item.description = request.form['description']
        session.add(edit_item)
        session.commit()
        return redirect(url_for('viewItem', user_id=user_id, item_id=item_id))
    else:
        return render_template('edit_item.html', user_id=user_id,
                               item_id=item_id, i=edit_item)


@app.route('/user/<string:user_id>/<int:item_id>/delete')
def deleteItem(user_id, item_id):
    q = session.query(Item).filter_by(id=item_id)
    if q == []:
        flash('Item does not exist')
        return redirect(url_for('user_catalog', user_id=user_id))
    item = q.one()
    if item.user_id != login_session['gplus_id']:
        return redirect(url_for('invalid_user_id'))
    name = item.name
    session.delete(item)
    session.commit()
    flash('Successfully deleted {}.'.format(name))
    return redirect(url_for('user_catalog', user_id=user_id))

# JSON ENDPOINT ######
# Requires that you log in through the browser first...


def serialize_sqlalchemy_object(o):
    return {key: value for key, value in o.__dict__.items()
            if not key.startswith('_')  # ignore "private" keys
            }


@app.route('/user/<string:user_id>/JSON')
def user_catalog_JSON(user_id):
    if user_id is None:
        return redirect(url_for('invalid_user_id'))
    if user_id != 'TEST' and (login_session.get('gplus_id') is None or
       user_id != login_session['gplus_id']):
        return redirect(url_for('invalid_user_id'))

    print("{} accessed their item catalog".format(user_id))
    # Some test code to see all users in the database
    # print(session.query(User).filter_by(id=str(user_id)))
    # q = session.query(User).all()
    # print('All users: \n')
    # for u in q:
    #     print('u: {}, id: {}'.format(u.username, u.id))

    # Sanity Check, user is in the database.
    # And in case I refactor the database
    # so that the gplus_id is no longer the user_id
    user = session.query(User).filter_by(id=user_id).one()
    items = session.query(Item).filter_by(user_id=user.id).all()
    categories = session.query(
        Item.category.distinct()).filter_by(user_id=user_id).all()
    categories = [c[0] for c in categories]
    return jsonify(user=serialize_sqlalchemy_object(user),
                   items=[serialize_sqlalchemy_object(item) for item in items],
                   categories=categories)  # , items=dict(items))


@app.route('/sneakysneaky/JSON')
def invalid_user_id_JSON():
    return jsonify(message="403 Access Forbidden", status_code=403)


@app.route('/user/<string:user_id>/<int:item_id>/get/JSON')
def getItem_JSON(user_id, item_id):
    if user_id != login_session['gplus_id']:
        return invalid_user_id_JSON()
    q = session.query(Item).filter_by(id=item_id)
    if q == []:
        return jsonify(error='error')

    item = q.one()
    if item.user_id != login_session['gplus_id']:
        return invalid_user_id_JSON()
    return jsonify(serialize_sqlalchemy_object(item))


@app.route('/user/<string:user_id>/new/JSON/', methods=['POST'])
def newItem_JSON(user_id):
    if user_id != login_session['gplus_id']:
        return invalid_user_id_JSON()

    params = request.args
    new_item = Item(name=params.get('name'),
                    category=params.get('category'),
                    description=params.get('description'),
                    user_id=user_id)
    session.add(new_item)
    session.commit()
    flash('New Item {} created!'.format(new_item.name))
    return redirect(url_for('user_catalog_JSON', user_id=user_id))


@app.route('/user/<string:user_id>/<int:item_id>/edit/JSON', methods=['POST'])
def editItem_JSON(user_id, item_id):
    if user_id != login_session['gplus_id']:
        return invalid_user_id_JSON()
    q = session.query(Item).filter_by(id=item_id)
    if q == []:
        return jsonify(error='error')
    edit_item = q.one()
    if edit_item.user_id != login_session['gplus_id']:
        return invalid_user_id_JSON()
    params = request.args
    if params.get('name'):
        edit_item.name = params.get('name')
    if params.get('category'):
        edit_item.category = params.get('category')
    if params.get('description'):
        edit_item.description = params.get('description')
    session.add(edit_item)
    session.commit()
    return jsonify(success='success')


@app.route('/user/<string:user_id>/<int:item_id>/delete/JSON')
def deleteItem_JSON(user_id, item_id):
    if user_id != login_session['gplus_id']:
        return invalid_user_id_JSON()
    q = session.query(Item).filter_by(id=item_id)
    if q == []:
        return jsonify(error='error')
    item = q.one()

    if item.user_id != user_id:
        return invalid_user_id_JSON()
    name = item.name
    session.delete(item)
    session.commit()
    return jsonify(success='success')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    # secret = "HNZSvRcMuomKUkhL_geXR3Sf"
    # client_id =
    # "614145770670-41hh95tvp1370nntpb9v758i5be9dfqb.apps.googleusercontent.com"
    CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']
    APPLICATION_NAME = "Minimalist Catalog"
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
