#! /bin/python

import random
import os
from datetime import datetime
from flask import Flask, request, Response, send_file

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps

random.seed(datetime.now())

client = MongoClient()
db = client['printnplay']

app = Flask(__name__)

UPLOAD_DEST = '/Users/raymond/Projects/PrintAndPlay/upload'

@app.route('/api/games')
def games():
    if 'gameId' in request.args:
        gid = request.args.get('gameId')
        game = db.games.find_one({'_id': ObjectId(gid)})
        return Response(response=dumps(game),
            status=200,
            mimetype="application/json")
    elif 'random' in request.args:
        game = db.games.find_one()
        count  = db.games.count()
        offset = random.randrange( 1, count )
        game = db.games.find().skip( offset ).limit(1)[0]
        return Response(response=dumps(game),
            status=200,
            mimetype="application/json")
    else:
        games = db.games.find()
        games = list(games)

        if "limit" in request.args:
            limit = int(request.args.get("limit"))
            games = random.sample(games, limit)

        return Response(response=dumps(games),
            status=200,
            mimetype="application/json")

@app.route('/api/img/<filename>')
def image(filename):
    fn, ext = os.path.splitext(filename)
    return send_file("images/" + filename, mimetype='image/' + ext[1:])

@app.route('/api/download')
def download():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
