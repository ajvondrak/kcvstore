from flask import Flask
from flask import json
from flask import make_response
from flask import request
from kcvstore import KeyColumnValueStore

app = Flask(__name__)

store = KeyColumnValueStore(path='kcvstore.pickle')

@app.route('/')
def get_keys():
    return json.jsonify(keys=list(store.get_keys()))

@app.route('/', methods=['POST'])
def set_new():
    key = request.form.get('key')
    col = request.form.get('col')
    val = request.form.get('val')
    return make_response(json.jsonify(result=store.set(key, col, val)), 201)

@app.route('/<key>')
def get_key_or_slice(key):
    # Since get_slice(key, None, None) == get_key(key), we can do both with
    # just get_slice.
    start = request.args.get('start')
    stop = request.args.get('stop')
    return json.jsonify(columns=store.get_slice(key, start, stop))

@app.route('/<key>', methods=['DELETE'])
def delete_key(key):
    return json.jsonify(result=store.delete_key(key))

@app.route('/<key>/<col>')
def get(key, col):
    return json.jsonify(value=store.get(key, col))

@app.route('/<key>/<col>', methods=['DELETE'])
def delete(key, col):
    return json.jsonify(result=store.delete(key, col))

@app.route('/<key>/<col>', methods=['PUT'])
def overwrite(key, col):
    val = request.form.get('val')
    return make_response(json.jsonify(result=store.set(key, col, val)), 301)

if __name__ == '__main__':
    app.run()
