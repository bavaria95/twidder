from flask import Flask
import database_helper

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/a")
def a():
    database_helper._create_database_structure()
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)