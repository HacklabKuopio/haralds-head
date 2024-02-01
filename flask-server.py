from flask import Flask, jsonify
from flask import request
import json

# Example request: curl --data '{"name":"curl"}' -X POST -H 'Content-Type: application/json' http://10.42.0.30:5000/new
# Run command: flask --app main run --host=0.0.0.0

app = Flask(__name__)

@app.route("/")
def hello():
    return "<p>Hello, World!</p>"

@app.route('/new', methods=['POST'])
def new_device():
    assert request.path == '/new'
    assert request.method == 'POST'

    if request.method == 'POST':
        print(request.json)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
