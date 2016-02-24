from twidder import app
from flask_sockets import Sockets

sockets = Sockets(app)

@sockets.route('/sock')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        print(message)
        ws.send(message)


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

# app.run(debug=True)
