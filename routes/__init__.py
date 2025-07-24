from flask import Flask
import secrets

app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(16)

# routes package initialization
# Blueprint registration and database setup moved to app.py

if __name__ == '__main__':
    app.run(debug=True)
