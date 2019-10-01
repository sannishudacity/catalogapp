from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client import client
#from oauth2client import flow_from_clientsecrets
#from oauth2client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
#from flask import Flask
app = Flask(__name__)

# Get CLIENTID from clients_secrets.json file
CLIENT_ID = json.loads(
    open('/var/www/catalogdir/catalogapp/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"


# Connect to Database and create database session
#engine = create_engine('sqlite:///applicationwithuser.db')
DATABASE_URI = 'postgres+psycopg2://postgres:mypassword@127.0.0.1:5432/catalogdb'
engine = create_engine(DATABASE_URI)
Base.metadata.bind = engine

# Open a session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all Categories and items
#@app.route('/')
#@app.route('/category/')
#def showCategory():
#    categories = session.query(Category).order_by(asc(Category.name))
#    allItems = session.query(Item).order_by(desc(Item.id))
##   if not logged in then show only view
#    if 'username' not in login_session:
#        return render_template('categoryview.html',
#                               categories=categories, items=allItems)
#    else:
#        return render_template('category.html',
#                               categories=categories, items=allItems)
##@app.route("/")
##def hello():
##    return "Hello, everyone!"
#if __name__ == "__main__":
#    app.run()



## Sannish
app = Flask(__name__)


# Login routine - Create anti-forgery state token
@app.route('/login')
def showLogin():
    '''
        Login

        Create anti-forgery state token to ensure authenticity of client
    '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Logout routine
@app.route('/logout')
def showLogout():
    '''
        Logout

        Log out of session with googleplus or facebook and make sure
        all session variables are deleted.
    '''
    if login_session['provider'] == 'facebook':
        response = fbdisconnect()
        flash(response)
        return redirect(url_for('showCategoryView'))
    elif login_session['provider'] == 'google':
        retstat, response = gdisconnect()
        flash(response)
        if retstat == 2:
            return redirect(url_for('showCategory'))
        else:
            return redirect(url_for('showCategoryView'))
    else:
        return "Thank you!"


# Connect using Facebook Authentication
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    '''
        Facebook connect

        Use API provided by Facebook for authentication
    '''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('/var/www/catalogdir/catalogapp/fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('/var/www/catalogdir/catalogapp/fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type='
    url += 'fb_exchange_token&'
    url += 'client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

#   Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we
        have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?'
    url += 'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

#   The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?'
    url += 'access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

#   see if user exists
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# Disconnect from Facebook Account
@app.route('/fbdisconnect')
def fbdisconnect():
    '''
        Facebook disconnect

        Disconnect from facebook login
    '''
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/'
    url += '%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['provider']
    del login_session['username']
    del login_session['email']
    del login_session['access_token']
    del login_session['facebook_id']
    del login_session['picture']
    del login_session['user_id']
    response = 'You have successfully Logged Out.'
    return response


# Server get one time login from client, sends it to googleplus to authorize
@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''
        Googleplus connect

        Use API provided by Googleplus for authentication
    '''
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
#   Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        #oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow = flow_from_clientsecrets('/var/www/catalogdir/catalogapp/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
#   Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
#   If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

#   Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

#   Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
#        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

#   Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

#   Check if user already exist in local user table. If not create one
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    '''
        Googleplus disconnect

        Disconnect from Googleplus session
    '''
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
                                 'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?'
    url += 'token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = 'You have successfully Logged Out.'
        return 1, response
    else:
        response = 'Failed to revoke token for given user.'
        return 2, response


# Show all Categories and items
@app.route('/')
@app.route('/category/')
def showCategory():
    categories = session.query(Category).order_by(asc(Category.name))
    allItems = session.query(Item).order_by(desc(Item.id))
#   if not logged in then show only view
    if 'username' not in login_session:
        return render_template('categoryview.html',
                               categories=categories, items=allItems)
    else:
        return render_template('category.html',
                               categories=categories, items=allItems)


# View Only Category and Items Pages
@app.route('/categoryview/')
def showCategoryView():
    categories = session.query(Category).order_by(asc(Category.name))
    allItems = session.query(Item).order_by(desc(Item.id))
    return render_template('categoryview.html',
                           categories=categories, items=allItems)


# Create a new Category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():

    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('newCategory.html')


# Edit a Category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if editedCategory.user_id != login_session['user_id']:
        errmsg = ''
        errmsg += 'You are not authorized to edit this category. '
        errmsg += 'You can only edit categories you have created.'
        flash(errmsg)
        return redirect(url_for('showCategory'))
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            editedCategory.user_id = login_session['user_id']
            flash('Category Successfully Edited %s' % editedCategory.name)
            session.add(editedCategory)
            session.commit()
            return redirect(url_for('showCategory'))
        else:
            flash('Category name cannot be blank')
            return redirect(url_for('showCategory'))
    else:
        return render_template('editCategory.html', category=editedCategory)


# Delete a Category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if categoryToDelete.user_id != login_session['user_id']:
        errmsg = ''
        errmsg += 'You are not authorized to delete this category. '
        errmsg += 'You can only delete categories you have created.'
        flash(errmsg)
        return redirect(url_for('showCategory'))
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)


# Show all Items for a selected Category
@app.route('/category/<int:category_id>/items')
def showCategoryItems(category_id):
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).filter_by(category_id=category_id).all()
    if 'username' not in login_session:
        return render_template('categoryview.html',
                               categories=categories,
                               items=items)
    else:
        return render_template('category.html',
                               categories=categories,
                               items=items)


# Add New Item
@app.route('/category/item/new/', methods=['GET', 'POST'])
def newItem():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category_name = request.form['category_name']
        category = session.query(Category).filter_by(
                                        name=category_name).one()
        category_id = category.id
        user_id = login_session['user_id']
        newItem = Item(name=name,
                       description=description,
                       category_id=category_id,
                       user_id=user_id)
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.name)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        categoryList = session.query(Category).order_by(asc(Category.name))
        return render_template('newItem.html', categoryList=categoryList)


# Edit Item
@app.route('/category/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if editedItem.user_id != login_session['user_id']:
        errmsg = ''
        errmsg += 'You are not authorized to edit this item. '
        errmsg += 'You can only edit items you have created.'
        flash(errmsg)
        return redirect(url_for('showCategory'))
    if request.method == 'POST':
        editedItem.name = request.form['name']
        editedItem.description = request.form['description']
        category_name = request.form['category_name']
        category = session.query(Category).filter_by(
                                            name=category_name).one()
        editedItem.category_id = category.id
        editedItem.user_id = login_session['user_id']
        session.add(editedItem)
        flash('Item %s Successfully Edited' % editedItem.name)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        categoryList = session.query(Category).order_by(asc(Category.name))
        return render_template('editItem.html', item=editedItem,
                               categoryList=categoryList)


# Delete Item
@app.route('/category/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    deletedItem = session.query(Item).filter_by(id=item_id).one()
    if deletedItem.user_id != login_session['user_id']:
        errmsg = ''
        errmsg += 'You are not authorized to delete this item. '
        errmsg += 'You can only item categories you have created.'
        flash(errmsg)
        return redirect(url_for('showCategory'))
    if request.method == 'POST':
        session.delete(deletedItem)
        flash('%s Successfully Deleted' % deletedItem.name)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('deleteItem.html', item=deletedItem)


# Show description of an Item
@app.route('/category/item/<int:item_id>/description/',
           methods=['GET', 'POST'])
def showItemDescription(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('itemdescription.html', item=item)


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
