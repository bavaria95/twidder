from flask import Flask, request
import json
import database_helper

app = Flask(__name__)

@app.before_request
def before_request():
    database_helper.connect_db()

@app.teardown_request
def teardown_request(exception):
    database_helper.close_db()

@app.route("/sign_up", methods=["POST"])
def sign_up():
    params = request.form
    return json.dumps(database_helper.sign_up_user(params))

@app.route("/sign_in", methods=["POST"])
def sign_in():
    params = request.form
    return json.dumps(database_helper.sign_in_user(params))

@app.route("/sign_out", methods=["POST"])
def sign_out():
    params = request.form
    return json.dumps(database_helper.sign_out_user(params))

@app.route("/change_password", methods=["POST"])
def change_password():
    params = request.form
    return json.dumps(database_helper.change_password(params))

@app.route("/get_user_data_by_email", methods=["GET"])
def get_user_data_by_email():
    params = request.args
    return json.dumps(database_helper.get_user_data_by_email(params))

@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    params = request.args
    return json.dumps(database_helper.get_user_data_by_token(params))


if __name__ == "__main__":
    app.run(debug=True)