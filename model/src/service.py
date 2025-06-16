from flask import Flask
from flask_cors import CORS

from src.apis.speech import speech_blueprint

from waitress import serve

app = Flask(__name__)
            
app.register_blueprint(speech_blueprint, url_prefix='/api')

CORS(app)
port = 20025


def run():
    serve(
        app,
        host='0.0.0.0',
        port=port
    )


if __name__ == '__main__':
    run()
