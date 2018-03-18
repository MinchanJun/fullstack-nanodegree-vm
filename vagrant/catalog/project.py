from flask import Flask, render_template, request, redirect, url_for, \
                flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem, User

#Imports for login session for 3rd party
from flask import session as login_session
import random, string

#Imports for callback function and gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json','r').read())['web']['client_id']

engine = create_engine('sqlite:///itemcatalogapp_copy.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request forgery.
# Store it in the session for later validation.
@app.route('/login/')
def showLogin():
    state=''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token
    if request.args.get('state') != login_session['state']:
        print login_session['state']
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is  \
        already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
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


    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                picture=login_session['picture'])
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

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for\
        given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


'''
Shows list of categories
'''
@app.route('/')
@app.route('/category/')
def showCategory():
    category = session.query(Category).all()

    if 'username' not in login_session:
        return render_template('public_category.html', category=category)
    else:
        return render_template('show_category.html',category=category)

'''
Create a category
'''
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    # To protect page from unexpected user
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newCategory = Category(name=request.form['name'], user_id= \
                login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash("%s Added" % newCategory.name)
        return redirect(url_for('showCategory'))
    else:
        return render_template('category_new.html')

'''
Edit a category
'''
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    # To protect page from unexpected user
    if 'username' not in login_session:
        return redirect('/login')
    edit_category = session.query(Category).filter_by(id = category_id).one()
    if edit_category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not\
                authorized to edit');}</script>\
                <body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            edit_category.name = request.form['name']
        session.add(edit_category)
        session.commit()
        flash("Coin Edited to %s " % edit_category.name)
        return redirect(url_for('showCategory'))
    else:
        return render_template('edit_category.html',category = edit_category)

'''
Delete a category
'''
@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    # To protect page from unexpected user
    if 'username' not in login_session:
        return redirect('/login')
    delete_category = session.query(Category).filter_by(id=category_id).one()
    if delete_category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
                authorized to edit');}</script>\
                <body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(delete_category)
        session.commit()
        flash("%s Coin Deleted" % delete_category.name)
        return redirect(url_for('showCategory'))
    else:
        return render_template('delete_category.html',category=delete_category)


'''
Shows a list of category items
'''
@app.route('/category/<int:category_id>/')
def categoryItem(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(CategoryItem).filter_by(category_id = category.id)
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_category_item.html', category=category,
                 items=items, creator= creator)
    else:
        return render_template('category_item.html', category=category,
                items=items, creator = creator)


'''
Create a list of category item
'''
@app.route('/category/<int:category_id>/new/', methods=['GET','POST'])
def newCategoryItem(category_id):
    # To protect page from unexpected user
    if 'username' not in login_session:
        return redirect('/login')

    # add this line for user_id
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not \
                authorized to add');}</script>\
                <body onload='myFunction()''>"
    if request.method == 'POST':
        newCategoryItem = CategoryItem(name=request.form['name'],\
                        description=request.form['description'],\
                        category_id=category_id, user_id=category.user_id)
        session.add(newCategoryItem)
        session.commit()
        print newCategoryItem.id
        flash("New Coin Category Added %s" % newCategoryItem.name)
        return redirect(url_for('categoryItem',category_id=category_id))
    else:
        category = session.query(Category).filter_by(id = category_id).one()
        return render_template('category_item_new.html',\
                category_id=category_id, category=category)


'''
Edit a list of category item
'''
@app.route('/category/<int:category_id>/<int:category_item_id>/edit/',\
            methods=['GET','POST'])
def editCategoryItem(category_id,category_item_id):
    # To protect page from unexpected user
    if 'username' not in login_session:
        return redirect('/login')

    category = session.query(Category).filter_by(id=category_id).one()
    edit_category_item = session.query(CategoryItem).filter_by(id = \
                category_item_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not \
                authorized to edit');}</script>\
                <body onload='myFunction()''>"
    if request.method == 'POST':

        if request.form['name']:
            edit_category_item.name = request.form['name']
        if request.form['description']:
            edit_category_item.description = request.form['description']
        session.add(edit_category_item)
        session.commit()
        flash("%s Coin Category Edited" % edit_category_item.name)
        return redirect(url_for('categoryItem',category_id=category_id))
    else:
        #Found bug. If you're editing category item, category_item_id
        #doesn't depend on the category_id when you manually type in the URL.
        #Fixed this issue
        if category_id != edit_category_item.category_id:
            return render_template('error.html')
        else:
            return render_template('edit_category_item.html',\
                category_id=category_id, category_item_id=category_item_id,\
                category_item=edit_category_item)

'''
Delete a list of category item
'''
@app.route('/category/<int:category_id>/<int:category_item_id>/delete/', \
            methods=['GET','POST'])
def deleteCategoryItem(category_id,category_item_id):
    # To protect page from unexpected user
    if 'username' not in login_session:
        return redirect('/login')

    category = session.query(Category).filter_by(id = category_id).one()
    delete_category_item = session.query(CategoryItem).filter_by(id = \
            category_item_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not \
                authorized to delete');}</script>\
                <body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(delete_category_item)
        session.commit()
        flash("%s Coin Category Deleted" % delete_category_item.name)
        return redirect(url_for('categoryItem', category_id=category_id))
    else:
        return render_template('delete_category_item.html',\
                category_id=category_id,\
                category_item=delete_category_item)

@app.route('/category/JSON')
def categoryJSON():
    category = session.query(Category)
    json = jsonify(CategoryList=[r.serialize for r in category])
    return json

@app.route('/category/<int:category_id>/JSON')
def categoryItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    category_item = session.query(CategoryItem).filter_by(category_id=category_id).all()
    json = jsonify(CategoryItemList=[r.serialize for r in category_item])
    return json

@app.route('/category/<int:category_id>/<int:category_item_id>/JSON')
def categoryItemSpecificJSON(category_id,category_item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    category_item = session.query(CategoryItem).filter_by(id=category_item_id).one()
    json = jsonify(CategoryItemListSpecifc =category_item.serialize)
    return json
if __name__ == '__main__':
    app.secret_key = 'super_secret_key' # This is for flash
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
