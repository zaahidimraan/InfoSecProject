from flask import Flask, request, redirect, url_for, session, abort,render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import logging

app = Flask(__name__)
app.secret_key = '123'
csrf = CSRFProtect(app)

class CodeForm(FlaskForm):
    code = StringField('Code')
    submit = SubmitField('Submit')



# Set Content Security Policy (CSP) header
csp_header = {
    "default-src": "'self'",
    "style-src": "'self' 'unsafe-inline'",
    "script-src": "'self'",
}

app.config.update(
    CSP_HEADER=csp_header,  # Content Security Policy to prevent XSS
                            # HTTP Strict Transport Security to force client to use HTTPS
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PREFERRED_URL_SCHEME='https',
    
    X_FRAME_OPTIONS='DENY',  # X-Frame-Options to prevent Clickjacking
)

# Remove X-Powered-By header to hide server software information
@app.after_request
def remove_x_powered_by(response):
    response.headers.pop('X-Powered-By', None)
    return response

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Custom error handler to handle HTTP 404 errors
@app.errorhandler(404)
def page_not_found(e):
    app.logger.error('Page not found: %s', request.url)
    return render_template('404.html'), 404

# Custom error handler to handle HTTP 500 errors
@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error('Internal server error: %s', str(e))
    return render_template('500.html'), 500

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

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

    return render_template('external.html')

    # return '''
    #     <h1>External Network</h1>
    #     <p>Welcome to the external network! You can see this page without authenticating.</p>
    #     <br>
    #     <a href="/dmz"><button>Go to DMZ Layer</button></a>
    #     <br>
    #     <a href="/internal"><button>Go to Internal Layer</button></a>
    # '''


@app.route('/dmz', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def dmz():
    form = CodeForm()
    if form.validate_on_submit():
        code = form.code.data
        #print(validate_input(code))
        if verify_user(code) and validate_input(code):
            session['authenticated'] = True
            return redirect(url_for('internal'))
        else:
            print("Invalid code. Unable to enter DMZ.")
            app.logger.warning('Invalid code entered: %s', code)
            return '''
                <h1>DMZ Page</h1>
                <p> Invalid code. Unable to enter Internal Area</p>
                <script>
                    setTimeout(function(){
                        window.location.href = "/dmz";
                    }, 2000);
                </script>
                '''
    return render_template('dmz.html', form=form)

@app.route('/internal')
@limiter.limit("5 per minute")
def internal():
    if not session.get('authenticated'):
        return redirect(url_for('dmz'))
    else:
        session['authenticated'] = False
        return  render_template('internal.html')
                

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='127.0.0.1' )
