#!/usr/bin/env python3
from flask import Flask, jsonify
from flask import request
import json
import logging

# Example request: curl --data '{"name":"curl"}' -X POST -H 'Content-Type: application/json' http://10.42.0.30:5000/new
# Run command: flask --app main run --host=0.0.0.0

app = Flask(__name__)

@app.route("/")
def hello():
    return "<p>Hello, Disobey ;-)</p>"

@app.route('/haralds-scan', methods=['POST'])
def new_device():
    assert request.path == '/haralds-scan'
    assert request.method == 'POST'

    if request.method == 'POST':
        logging.debug(request.json)
        with open('/opt/haralds-head/scans/haralds-scanlog.txt', 'a') as f:
            f.write(request.json)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")

