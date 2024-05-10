from facebook import create_app
from flask_cors import CORS
from facebook.socketio_instance import socketio
from flask import render_template


if __name__ == "__main__":
    app = create_app()
    CORS(app,
         origins=['http://localhost:3000',
                  'https://my-fb-demo.netlify.app/',
                  'https://my-fb-demo.000webhostapp.com/'],
         supports_credentials=True)
    socketio.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, debug=True)
