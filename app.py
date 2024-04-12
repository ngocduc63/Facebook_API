from facebook import create_app
from flask_cors import CORS
from facebook.socketio_instance import socketio

if __name__ == "__main__":
    app = create_app()
    CORS(app, origins='http://localhost:3000', supports_credentials=True)
    socketio.init_app(app)

    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True, log_output=True, use_reloader=False, debug=True)



