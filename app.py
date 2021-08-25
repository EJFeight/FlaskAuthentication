# This application is based on the GitHub repo for flask-login:
# https://github.com/maxcountryman/flask-login

# These are the minimum components from flask needed for this demo.
from flask import Flask, request, render_template

# This provides the user authentication framework.
import flask_login

# These components are for generating and comparing password hashes.
from werkzeug.security import generate_password_hash, check_password_hash


# Create the application
app = Flask(__name__)
# A secret key must be set to allow flask_login to access the session dictionary.
app.secret_key = 'use your own cryptic secret here'

# Create and Configure the login manager.
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


# User information is stored in a dictionary for purposes of this example.
# In production this can be replaced by a db query or ORM and the hashed value of the passwords would be stored.
# For purposes of this example I am encrypting teh password inside the dictionary so it is clear what the password
# actually is. For example: user 'foobar' has a password of 'foopassword'
users = {
    'foobar': {'firstname': 'foo', 'lastname': 'bar', 'password': generate_password_hash('foopassword')},
    'barfoo': {'firstname': 'bar', 'lastname': 'foo', 'password': generate_password_hash('barpassword')}
}

# Telling Flask-Login how to load a user requires three things:
# 1) a user object
# 2) a request_loader callback to load a user from a form request
# 3) a user_loader callback to load a user from a cession


# Create a user class that inherits from the UserMixin class.
# You can add to this class if you want, but all that is required is the inheritance.
class User(flask_login.UserMixin):
    pass


# user_loader callback
# This is for users that are already logged in
@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user


# request_loader callback
# This is for a new user login
@login_manager.request_loader
def request_loader(my_request):
    username = my_request.form.get('username')

    if username not in users:
        return

    user = User()
    user.id = username
    return user


# Determine the id of the current user.
# For this example we are using the username from the users dictionary.
# This is set either in the user_loader or the request_loader callback.
def current_user():
    if flask_login.current_user.is_authenticated:
        return flask_login.current_user.id
    else:
        return 'Anonymous'


# Route to home page
@app.route('/')
def index():
    return render_template('index.html', username=current_user())


# The login route gets the user name and password from the login form
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html', username=current_user())

    # This section executes if the request method is POST
    # Get username from form
    username = request.form['username']
    password = request.form['password']

    # check that the user exists and that the password is correct
    if username in users and check_password_hash(users[username]['password'], password):
        user = User()
        user.id = username
        flask_login.login_user(user)
        # Display the successful login page
        return render_template('good_login.html', username=current_user())
    else:
        # Display the failed login page
        return render_template('bad_login.html', username=current_user())


# This route requires authentication
@app.route('/protected')
@flask_login.login_required
def protected():
    return render_template('protected.html', username=current_user())


# This route does not require authentication
@app.route('/public')
def success():
    return render_template('public.html', username=current_user())


# This route will logout the user
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('index.html', username=current_user())


# This route handles unauthorized access attempts
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('denied.html', username=current_user())


# launch the application
if __name__ == '__main__':
    app.run(debug=True)
