from flask import Flask
from flask_sslify import SSLify 

app = Flask(__name__)

if __name__ == '__main__':
	app.run()