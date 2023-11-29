from flask import Flask, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = '123'

# This could be any function that verifies the user.
def verify_user(code):
    return code == "1234"

@app.before_request
def before_request():
    # Enforce HTTPS for the internal page
    if request.path == '/internal' and not request.is_secure and not request.headers.get('X-Forwarded-Proto', '').startswith('https') and not session.get('authenticated'):
        abort(403)  # Forbidden
    # IP address filtering
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden
    # Content type checking for POST requests
    if request.method == 'POST' and request.content_type != 'application/x-www-form-urlencoded':
        abort(415)  # Unsupported Media Type

@app.route('/')
def externalnetwork():
    session['authenticated'] = False    # Set to True if you want to skip authentication
    return '''
        Welcome to the homepage! You can access this page without authentication.
        <br>
        <a href="/server"><button>Go to Server Page</button></a>
        <br>
        <a href="/internal"><button>Go to Internal Page</button></a>
    '''

@app.route('/server', methods=['GET', 'POST'])
def server():
    if request.method == 'POST':
        code = request.form.get('code')
        if verify_user(code):
            session['authenticated'] = True
            return redirect(url_for('internal'))
        else:
            return redirect(url_for('internal'))
    return '''
        <form method="POST">
            Code: <input type="text" name="code">
            <input type="submit" value="Submit">
        </form>
    '''

@app.route('/internal')
def internal():
    if not session.get('authenticated'):
        return redirect(url_for('server'))
    return "Welcome to the internal system! You can only see this page if you're authenticated."

if __name__ == '__main__':
    app.run()
