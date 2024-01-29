#Import the required modules
from flask import Flask, request, jsonify, make_response, render_template, session, flash
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# Secret key for encoding and decoding JWT tokens
app.config['SECRET_KEY'] = '8asbddfgbfgdkufghdukffcshkdiwsujd' # In real life will be using env variables to define the secret key


def token_required(func):
    """
    Decorator function to check for the presence and validity of a JWT token in the request.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        # Extract the token from the request parameters
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401 # Unauthorised HTTP status code

        try:
            # Decode and verify the JWT token
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except jwt.ExpiredSignatureError:
            # Token has expired
            return jsonify({'Message': 'Token has expired'}), 403 # Forbidden HTTP status code
        except jwt.InvalidTokenError:
            # Invalid token
            return jsonify({'Message': 'Invalid token'}), 403 # Forbidden HTTP status code

        # Call the original function with the decoded data
        return func(*args, **kwargs)

    return decorated


@app.route('/')
def home():
    """
    Route for the home page. If the user is not logged in, render the login template,
    otherwise, display a message indicating the user is logged in.
    """
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'logged in currently'


@app.route('/public')
def public():
    """
    Public route accessible to everyone.
    """
    return 'For Public'


@app.route('/auth')
@token_required
def auth():
    """
    Protected route that requires a valid JWT token for access.
    """
    return 'JWT is verified. Welcome to your dashboard!'


@app.route('/login', methods=['POST'])
def login():
    """
    Route for user login. If the provided username and password match, create a JWT token
    and return it in the response. Otherwise, return a 403 error.
    """
    if request.form['username'] and request.form['password'] == '123456':
        session['logged_in'] = True

        # Create a JWT token with user information and expiration time
        token = jwt.encode({
            'user': request.form['username'],
            'expiration': str(datetime.utcnow() + timedelta(seconds=60))
        },
            app.config['SECRET_KEY'])

        # Return the token in the response
        return jsonify({'token': token.decode('utf-8')})
    else:
        # Return a 403 error if the username and password are incorrect
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication Failed "'})


@app.route('/logout', methods=['POST'])
def logout():
    """
    Placeholder for a logout route. The actual logout functionality can be implemented here.
    """
    pass
    # your code goes here

if __name__ == "__main__":
    app.run(debug=True)
