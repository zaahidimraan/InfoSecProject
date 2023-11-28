from flask import Flask, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with your own secret key

# This could be any function that verifies the user.
def verify_user(code):
    return code == "1234"

@app.before_request
def before_request():
    # Enforce HTTPS
    if not request.is_secure:
        return "Please use HTTPS."

@app.route('/')
def homepage():
    return '''
        Welcome to the homepage! You can access this page without authentication.
        <br>
        <a href="/verify"><button>Go to Verification Page</button></a>
        <br>
        <a href="/internal"><button>Go to Internal Page</button></a>
    '''

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code = request.form.get('code')
        if verify_user(code):
            session['authenticated'] = True
            return redirect(url_for('internal'))
        else:
            return "Invalid code, please try again."
    return '''
        <form method="POST">
            Code: <input type="text" name="code">
            <input type="submit" value="Submit">
        </form>
    '''

@app.route('/internal')
def internal():
    if not session.get('authenticated'):
        return redirect(url_for('verify'))
    return "Welcome to the internal system! You can only see this page if you're authenticated."

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
