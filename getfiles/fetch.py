#! /usr/bin/python

import os
import json
from subprocess import call

filelist = {}

with open('filelist.json') as f:
    text = f.read().replace('\n', '')
    filelist = json.loads(text)

i = 0
for name, path in filelist.iteritems():
    if name and path:
        true_path = "http://www.boardgamegeek.com" + path
        #print ("wget -O {0:04d}.html " + true_path).format(i)
        call(['wget', "-O {0:04d}.html".format(i), true_path])
        i += 1
