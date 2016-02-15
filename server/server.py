from flask import Flask
import database_helper

app = Flask(__name__)

@app.before_request
def before_request():
    database_helper.connect_db()

@app.teardown_request
def teardown_request(exception):
    database_helper.close_db()

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/a")
def a():
    database_helper._create_database_structure()
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)