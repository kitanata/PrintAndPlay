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


    def parse_information(self, mod):
        info = mod.find(class_="innermoduletable")

        link = info.find(class_='mt5')

        if link.a:
            self.img_collection_link = "http://www.boardgamegeek.com" + link.a["href"]

        if link.link:
            self.image = link.link["href"]
            hash_img = hashlib.sha256(self.image).hexdigest()

            name, ext = splitext(self.image)
            hash_img += ext

            call(["wget", "-O " + hash_img, self.image])

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
                "language_dependence", "user_suggested_ages", "year_published", 
                "family", "reimplements", "artist", "honors", "expansion",
                "reimplemented_by", "expands", "contained_in"]:
                el = item.td.next_sibling.next_sibling
                self.process_a(name, el)

            else:
                print(name)
                print(item.prettify())
                raise StopIteration

    def parse_description(self, mod):
        info = mod.find(class_="innermoduletable")

        self.process_a("description", info)


    def parse_files(self, mod):
        info = mod.find(class_="innermoduletable")

        data = info.find_all('td')

        rows = [data[i:i+5] for i in range(0, len(data), 5)]

        self.files = []
        for r in rows:
            text = []
            for td in r:
                text.append(' '.join(self.strip_out_text(td)))
            try:
                link = r[1].a["href"]
            except Exception as e:
                return False

            self.files.append((text, link))

        return True


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


    def post_process(self):
        if hasattr(self, "category"):
            self.category = self.category.split('\n')

        self.description = ' '.join(self.description.split('\n')[1:-1])
        self.language_dependence = ' '.join(self.language_dependence.split('\n')[:-3])

        if hasattr(self, 'mechanic'):
            self.mechanic = self.mechanic.split('\n')

        self.number_of_players = self.number_of_players.replace(u'\u00a0\u2212\u00a0', ' - ')
        self.user_suggested_ages = ' '.join(self.user_suggested_ages.split('\n')[:-3])
        self.user_suggested_number_of_players = ' '.join(self.user_suggested_number_of_players.split('\n')[:-3])

        for stat, val in self.stats:
            stat = stat.replace(':', ''
                ).replace('.', ''
                ).replace(u'\u00a0', ' '
                ).replace(' ', '_').lower()
            setattr(self, 'stat_' + stat, val)

        delattr(self, 'stats')

        attr_to_del = []
        for attr, val in self.__dict__.iteritems():
            if val == "(no votes yet)":
                attr_to_del.append(attr)

        for attr in attr_to_del:
            delattr(self, attr)


def main():
    path = getcwd()
    filenames = [ join(path, f) for f in listdir(path) if isfile(join(path,f)) ]
    filenames = [f for f in filenames if ".html" in f]

    documents = []
    for name in filenames:
        with open(name) as f:
            documents.append(f.read().replace('\n', ''))

    json_doc = []
    for doc in documents:
        game = parse_document(doc)
        if game:
            json_doc.append(game.__dict__)

    with open('filedata.json', 'wo') as f:
        f.write(json.dumps(json_doc, indent=4, sort_keys=True))

    print("DONE!")


def parse_document(doc):
    soup = BeautifulSoup(doc)

    modules = soup.find_all(class_="geekitem_module")

    if len(modules) != 20:
        print("Module length is " + str(len(modules)) + " expected 20")
        return None

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
            if not new_game.parse_files(mod):
                return None

        elif "statistics" in title.lower():
            new_game.parse_statistics(mod)

    new_game.post_process()

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