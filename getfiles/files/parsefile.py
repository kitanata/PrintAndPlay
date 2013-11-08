#! /usr/bin/python

from bs4 import BeautifulSoup
from os import listdir, getcwd
from os.path import isfile, join, splitext
from subprocess import call
import hashlib
import json

class BoardGame:

    def parse_title(self, mod):
        title = mod.find(class_="geekitem_title")

        if not title:
            return

        self.link = "http://www.boardgamegeek.com" + title.a["href"]
        self.title = title.a.span.get_text()
        self.year = title.span.get_text()[1:-1]


    def parse_information(self, mod):
        info = mod.find(class_="innermoduletable")

        link = info.find(class_='mt5')
        self.img_collection_link = "http://www.boardgamegeek.com" + link.a["href"]

        self.image = link.link["href"]
        hash_img = hashlib.sha256(self.image).hexdigest()

        name, ext = splitext(self.image)
        hash_img += ext

        #call(["wget", "-O " + hash_img, self.image])

        self.image = hash_img

        items = info.find(class_='geekitem_infotable').find_all('tr')

        for item in items:
            name = item.td.b.get_text().lower().replace(' ', '_')

            if name == "designer":
                el = item.td.next_sibling.next_sibling.div.next_sibling.div.a
                self.process_link(name, el)

            elif name == "publisher":
                el = item.td.next_sibling.next_sibling.div.next_sibling.div.a
                self.process_link(name, el)

            elif name == "#_of_players":
                name = "number_of_players"
                el = item.td.next_sibling.next_sibling
                self.process_a(name, el)

            elif name == "user_suggested_#_of_players":
                name = "user_suggested_number_of_players"
                el = item.td.next_sibling.next_sibling
                self.process_a(name, el)

            elif name == "mfg_suggested_ages":
                name = "manufacturer_suggested_ages"
                el = item.td.next_sibling.next_sibling
                self.process_b(name, el)

            elif name == "playing_time":
                el = item.td.next_sibling.next_sibling
                self.process_b(name, el)

            elif name in ["subdomain", "alternate_names"]:
                continue

            elif name in ["category", "mechanic", "primary_name", "website",
                "language_dependence", "user_suggested_ages", "year_published"]:
                el = item.td.next_sibling.next_sibling
                self.process_a(name, el)

            else:
                print(name)
                print(item.prettify())
                break

    def parse_description(self, mod):
        info = mod.find(class_="innermoduletable")

        self.process_a("description", info)


    def parse_files(self, mod):
        info = mod.find(class_="innermoduletable")

        rows = info.find_all('tr')

        self.files = []
        for r in rows:
            text = '\n'.join(self.strip_out_text(r))
            link = r.td.next_sibling.next_sibling.a["href"]
            self.files.append((text, link))


    def parse_statistics(self, mod):
        info = mod.find(class_="innermoduletable")

        rows = info.tr.td.table.find_all('tr')

        self.stats = []
        for r in rows:
            name = r.td.b.get_text()
            value = r.td.next_sibling.next_sibling.get_text().strip()
            self.stats.append((name, value))


    def strip_out_text(self, el):
        return [x for x in map(lambda x: x.strip(), el.find_all(text=True)) if len(x) > 0]


    def process_a(self, name, el):
        attr = '\n'.join(self.strip_out_text(el))
        #print("Process A: ", name, attr)
        setattr(self, name, attr)


    def process_b(self, name, el):
        attr = ''.join(self.strip_out_text(el)).replace('\t', '')
        #print("Process B: ", name, attr)
        setattr(self, name, attr)


    def process_link(self, name, el):
        link = el["href"]
        text = el.get_text()

        attr = (link, text)
        #print("Process Link: ", name, attr)
        setattr(self, name, (link, text))


def main():
    path = getcwd()
    filenames = [ join(path, f) for f in listdir(path) if isfile(join(path,f)) ]
    filenames = [filenames[0]]

    documents = []
    for name in filenames:
        with open(name) as f:
            documents.append(f.read().replace('\n', ''))

    game = parse_document(documents[0])


def parse_document(doc):
    soup = BeautifulSoup(doc)

    modules = soup.find_all(class_="geekitem_module")

    if len(modules) != 20:
        print("Module length is " + len(modules) + " expected 20")

    new_game = BoardGame()

    for mod in modules:
        title = get_module_title(mod)

        if not title:
            new_game.parse_title(mod)

        elif "information" == title.lower().strip():
            new_game.parse_information(mod)

        elif "description" in title.lower():
            new_game.parse_description(mod)

        elif "files" in title.lower():
            new_game.parse_files(mod)

        elif "statistics" in title.lower():
            new_game.parse_statistics(mod)

    print json.dumps(new_game.__dict__, indent=4, sort_keys=True)

    return new_game


def get_module_title(mod):
    title_el = mod.find(class_="module_title")

    if not title_el:
        try:
            return mod.tbody.tr.td.div.div.a["href"]
        except:
            return None

    return title_el.get_text()


if __name__ == "__main__":
    main()