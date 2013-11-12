#! /bin/python

import pymongo
import os
import hashlib
from boto.mturk.connection import MTurkConnection
from flask import Flask, render_template, request
from bson.objectid import ObjectId
from flaskext.uploads import UploadSet, UploadNotAllowed, configure_uploads, patch_request_class, ARCHIVES

from pymongo import MongoClient
client = MongoClient()
db = client['printnplay']

app = Flask(__name__)

UPLOAD_DEST = '/Users/raymond/Projects/PrintAndPlay/upload'
app.config["UPLOADED_FILES_DEST"] = UPLOAD_DEST
app.config["UPLOADS_DEFAULT_DEST"] = UPLOAD_DEST


archives = UploadSet('archives', ('gz', 'bz2', 'zip', 'tar', '7z', 'rar'))

configure_uploads(app, (archives, ))

patch_request_class(app, 256 * 1024 * 1024)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/csv2761313')
def getcsv():
    data = db.games.find(fields=('_id', 'title', 'link'))

    games = []
    for row in data:
        games.append(','.join([row['title'], row['link'], str(row['_id'])]))

    return '\n'.join(games)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'key' not in request.form:
            return render_template('upload_failed_key.html')

        if 'archive' in request.files:
            #try to find the game
            key = request.form["key"]
            objKey = ObjectId(key)
            game = db.games.find({'_id': objKey})

            if game:
                try:
                    filename = archives.save(request.files['archive'])
                    filename = os.path.join(UPLOAD_DEST, 'archives', filename)
                    filesize = os.path.getsize(filename)

                    confirm = ""
                    with open(filename, 'rb') as f:
                        confirm = hashlib.sha1("blob " + str(filesize) + "\0" + f.read()).hexdigest()

                    if confirm == "":
                        return render_template('upload_failed.html')

                    db.games.update({"_id": objKey}, {
                        "$push": {
                            "uploaded_filenames": {
                                "name": filename, "hash": confirm
                            }
                        }
                    })

                    return render_template('upload_successful.html', confirm=confirm)
                except UploadNotAllowed as e:
                    return render_template('upload_failed.html')
            else:
                return render_template('upload_failed_key.html')
        else:
            return render_template('upload_failed.html')

    return render_template('upload.html')

if __name__ == '__main__':
    app.run()
