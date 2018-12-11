from flask import Flask
from flask_sslify import SSLify 

app = Flask(__name__)
sslify = SSLify(app)

@app.route('/')
def index():
	return('<h1>This is a server app for Dissonance telegram bot</h1>')

if __name__ == '__main__':
	app.run()