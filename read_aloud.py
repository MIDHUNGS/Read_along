from distutils.log import debug
import uuid
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/', methods=['POST', 'GET'])
def index():
    global session_id
    session_id = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/epub-read.html', methods=['POST', 'GET'])
def epub_read():
    global session_id
    session_id = str(uuid.uuid4())
    return render_template('epub-read.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
