from facebook import create_app
from flask_socketio import SocketIO
from facebook.chat.controller import socket_handel

if __name__ == "__main__":
    app = create_app()
    socketio = SocketIO(app)
    socket_handel(socketio)

    socketio.run(app, allow_unsafe_werkzeug=True, log_output=True, use_reloader=False, debug=True)



