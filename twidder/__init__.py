import os
from werkzeug import secure_filename
from flask import Flask, request
import json
import database_helper
from flask.ext.cors import CORS

from flask_sockets import Sockets

import helper

UPLOAD_FOLDER = 'videos'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'avi'])

app = Flask(__name__, static_url_path='')
sockets = Sockets(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)

@app.before_request
def before_request():
    database_helper.connect_db()

@app.teardown_request
def teardown_request(exception):
    database_helper.close_db()


@app.route("/", methods=["GET"])
def serve():
    return app.send_static_file('client.html')

@app.route("/sign_up", methods=["POST"])
def sign_up():
    params = request.json
    return json.dumps(database_helper.sign_up_user(params))

@app.route("/sign_in", methods=["POST"])
def sign_in():
    params = request.json
    return json.dumps(database_helper.sign_in_user(params))

@app.route("/sign_out", methods=["POST"])
def sign_out():
    params = request.json
    return json.dumps(database_helper.sign_out_user(params))

@app.route("/change_password", methods=["POST"])
def change_password():
    params = request.json
    return json.dumps(database_helper.change_password(params))

@app.route("/get_user_data_by_email", methods=["GET"])
def get_user_data_by_email():
    params = request.args
    return json.dumps(database_helper.get_user_data_by_email(params))

@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    params = request.args
    return json.dumps(database_helper.get_user_data_by_token(params))

@app.route("/post_message", methods=["POST"])
def post_message():
    params = request.json
    return json.dumps(database_helper.post_message(params))

@app.route("/get_user_messages_by_email", methods=["POST"])
def get_user_messages_by_email():
    params = request.json
    return json.dumps(database_helper.get_user_messages_by_email(params))

@app.route("/get_user_messages_by_token", methods=["POST"])
def get_user_messages_by_token():
    params = request.json
    return json.dumps(database_helper.get_user_messages_by_token(params))
    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'uploaded'
    return 'error'



@app.errorhandler(404)
def another(e):
    return app.send_static_file('client.html')


@sockets.route('/sock')
def sock(ws):
    while True:
        msg = ws.receive()
        if msg is not None:
            email = msg

            if database_helper.socket_pool.is_socket_presented(email):
                old_sock = database_helper.socket_pool.get_socket(email)
                try:
                    old_sock.send('bye')
                    database_helper.socket_pool.change_socket_by_email(email, ws)
                except:
                    pass
            else:
                database_helper.socket_pool.add_socket(email, ws)

            database_helper.notify_all_users()
        else:
            break

    database_helper.notify_all_users()

@sockets.route('/stats')
def stats_sock(ws):
    while True:
        msg = ws.receive()
        if msg is not None:
            token = msg
            database_helper.stats_info.add_entry(token, ws)
            database_helper.notify_all_users()
        else:
            break


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()