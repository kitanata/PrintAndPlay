#! /usr/bin/python
import argparse
import json
from bs4 import BeautifulSoup

from os import listdir
from os.path import isfile, join


def main(path):
    lines = []
    filenames = [ join(path, f) for f in listdir(path) if isfile(join(path,f)) ]

    title_tuples = []
    for f in filenames:
        title_tuples = title_tuples + parse_file(f)

    with open(join(path, 'filelist.json'), "wo") as f:
        f.write(json.dumps(dict(title_tuples)))


def parse_file(filename):

    with open(filename, "r") as f:
        lines = f.readlines()

    html_doc = reduce(lambda x, y: x + y, lines)

    soup = BeautifulSoup(html_doc) 

    main_content = soup.find(id="main_content")

    if not main_content:
        return []

    game_list = main_content.find_all(class_='mb5')

    game_tuples = []
    for game in game_list:
        game_tuples.append(parse_game(game))

    return game_tuples


def parse_game(game):
    title_el = game.div.dl.div.div.find_all('a')

    if len(title_el) == 3:
        title_el = title_el[1]
    elif len(title_el) == 2:
        title_el = title_el[1]
    elif len(title_el) >= 4:
        print(title_el)
    else:
        return (None, None)

    title = title_el.get_text()
    title_link = title_el['href']

    return (title, title_link)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="The direcotry of the files to parse.")

    args = parser.parse_args()

    main(args.dir)