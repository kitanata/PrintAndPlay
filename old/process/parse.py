#!/usr/bin/python

import json

canon = ""
free = ""
play = ""

files = ['canon.json', 'play.json', 'free.json']
parsed = []

for filename in files:
    with open(filename) as f:
        parsed.append(json.loads(f.read().replace('\n', '')))

things = reduce(lambda x, y: x + y, [x.items() for x in parsed])

print(len(things))

with open('result.json', "wo") as f:
    f.write(json.dumps(dict(things)))