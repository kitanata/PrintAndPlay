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

archives = UploadSet('archives', ARCHIVES)

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


@app.route('/review2761313')
def review_hits():
    conn = MTurkConnection(
        "AKIAJNZIIGQNIFH5PC2A", 
        "S5mCHfsnu88ph0X4kQTbMVPhtVVQpWx2yHsg1T/n")

    hits = conn.get_reviewable_hits()

    test_lines = []
    for hit in hits:
        assignments = conn.get_assignments(hit.HITId)

        for assignment in assignments:
            for question_form_answer in assignment.answers[0]:
                for key, value in question_form_answer.fields:
                    test_lines.append("Answer: %s: %s" % (key,value))

                #Look at the question's answer look up mongo entry
                #test that the value is correct.

                #if False:
                #    conn.approve_assignment(assignment.AssignmentId)
                #else:
                #    conn.reject_assignment(assignment.AssignmentId)

    return '\n'.join(test_lines)


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