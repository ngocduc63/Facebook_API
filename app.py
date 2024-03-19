from facebook import create_app
from flask_cors import CORS
from facebook.socketio_instance import socketio

if __name__ == "__main__":
    app = create_app()
    CORS(app, supports_credentials=True)
    socketio.init_app(app)

    socketio.run(app, allow_unsafe_werkzeug=True, log_output=True, use_reloader=False, debug=True)



