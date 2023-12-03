from flask import Flask, request, redirect, url_for, session, abort
from flask_limiter import Limiter

app = Flask(__name__)
app.secret_key = '123'

# This could be any function that verifies the user.
def verify_user(code):
    return code == "1234"

def validate_input(input_string):
    if len(input_string) != 4:
        return False
    for digit in range(10):
        if str(digit) not in input_string:
            return False
    return True


def validate_input(input_string):
    if len(input_string) != 4:
        return False
    return all(char.isdigit() for char in input_string)


@app.before_request
def before_request():

    if request.path == '/internal' and request.is_secure and session.get('authenticated') and request.remote_addr == '127.0.0.1': 
        abort(403)  # Forbidden
    # Content type checking for POST requests
    if request.method == 'POST' and request.content_type != 'application/x-www-form-urlencoded':
        abort(415)  # Unsupported Media Type

@app.route('/')
def externalnetwork():
    session['authenticated'] = False    # Set to True if you want to skip authentication
    return '''
        <h1>External Network</h1>
        <p>Welcome to the external network! You can see this page without authenticating.</p>
        <br>
        <a href="/dmz"><button>Go to DMZ Layer</button></a>
        <br>
        <a href="/internal"><button>Go to Internal Layer</button></a>
    '''

@app.route('/dmz', methods=['GET', 'POST'])
def dmz():
    if request.method == 'POST':
        code = request.form.get('code')
        print(validate_input(code))
        if verify_user(code) and validate_input(code):
            session['authenticated'] = True
            return redirect(url_for('internal'))
        else:
            return redirect(url_for('internal'))
    return '''
        <h1>DMZ Layer</h1>
        <form method="POST">
            Code: <input type="text" name="code">
            <input type="submit" value="Submit">
        </form>
    '''

@app.route('/internal')
def internal():
    if not session.get('authenticated'):
        return redirect(url_for('dmz'))
    else:
        session['authenticated'] = False
    return  '''
            <h1>Internal Page</h1>
            <p>Welcome to the internal system! You can only see this page if you're authenticated.</p>
            '''

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='127.0.0.1' )
