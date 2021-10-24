from typing import Dict, Set
import requests
from requests_cache import install_cache  # type: ignore[import]
from regattas import Regatta
from bs4 import BeautifulSoup as soup
import json
import hashlib

cache_time = 60 * 60 * 24
install_cache("html_cache", backend="sqlite", expire_after=cache_time)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
}

urls = {"home": "https://rowingmanager.com/regattas/{}/"}


# https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_file(url, file):
    s = requests.Session()
    # NOTE the stream=True parameter below
    with s.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return file


def get_xlsx_data(regatta: Dict, file: str):
    [name, _] = file.split(".")
    parts = name.split("_")
    name = parts[1]
    if name == "events":
        url = f"https://rowingmanager.com/regattas/{parts[0]}/events?download=true"
    else:
        url = f"https://rowingmanager.com/regattas/{parts[0]}/draw?view=table;download=true;day={parts[2]}"
    print("getting", url)
    download_file(url, regatta['folder'] / "data/xlsx" / file)


def get_html_data(regatta: Dict, file: str):
    [name, _] = file.split(".")
    parts = name.split("_")
    name = parts[1]
    if name == "events":
        url = f"https://rowingmanager.com/regattas/{parts[0]}/events"
    else:
        url = f"https://rowingmanager.com/regattas/{parts[0]}/draw?day={parts[2]}"
    print("getting", url)
    m = requests.get(url, headers=headers)
    with open(regatta['folder'] / "data/html" / file, "w", encoding="utf8") as f:
        f.write(m.text)


def required_files(regatta: Dict, ext: str) -> Set:
    events_file = f"{regatta['id']}_events_1.{ext}"
    draw_files = list(
        map(
            lambda x: f"{regatta['id']}_draw_{x}.{ext}",
            range(1, int(regatta['days']) + 1),
        )
    )
    return set([events_file] + draw_files)


def harvest(regatta: Dict, ext: str) -> None:
    required = required_files(regatta, ext)
    files = regatta['data'][ext]
    names = set(map(lambda x: x.parts[-1], files))
    files_to_get = required - names
    print("files_to_get", files_to_get)
    f = globals()[f"get_{ext}_data"]
    for file in files_to_get:
        f(regatta, file)
    return


def clean_string(s):
    return s.strip().replace('\xa0', '')


def get_page_links(s):
    return list(filter(lambda x: x, map(clean_string, s)))


def get_regatta_data(s):
    s = list(filter(lambda x: x, map(clean_string, s)))
    keys = "Regatta:,Date:,Venue:".split(",")
    indexes = list(map(lambda x: s.index(x), keys))
    name = s[indexes[0] + 1]
    venue = s[indexes[-1] + 1]
    date = ""
    x = indexes[1] + 1
    while x <= indexes[-1] - 1:
        date += s[x]
        x += 1
    d = dict(name=name, venue=venue, date=date)

    return d


def get_doc_data(s):
    return list(filter(lambda x: x and x != 'Documents', map(clean_string, s)))


def probe(regatta: Regatta):
    '''
    find what files are available, and what aren't
    necessary are the event list and the draw.
    there are several versions of the files.
    the regatta has an events tab and a draw tab
    the urls will respond even if there is no data
    then there is the landing page. It has a list of documents
    There is also an xlsx version of the events and draw.
    so get events page, events xlsx, get draw page and draw.xlsx
    get document draw_html, pdf
    '''
    with open("data_files.json") as f:
        files = json.loads(f.read())

    if not files['home_page']['url']:
        files['home_page']['url'] = urls['home'].format(regatta.id)
    url = files['home_page']['url']
    print("getting", f"{url}")
    m = requests.get(url, headers=headers)

    with open("file.html", "w", encoding="utf8") as f:
        f.write(m.text)
    checksum = hashlib.md5(m.text.encode('utf8')).hexdigest()
    print("check", checksum)
    if checksum != files['home_page']['checksum']:
        files['home_page']['checksum'] = checksum

    s = soup(m.text, "lxml")
    tables = s.find_all('table')
    # print(tables[1].tr)
    [links, data, docs] = list(
        filter(lambda x: not isinstance(x, str), tables[1].tr.children)
    )
    # [links, data, docs] = tables[1].tr.children

    # links = tables[1].tr.td[0]
    print("links", get_page_links(links.strings))
    print(">" * 48)
    # data = tables[1].tr.td[1]
    print("data", get_regatta_data(data.strings))
    print(">" * 48)
    # docs = tables[1].tr.td[2]
    print("docs", get_doc_data(docs.strings))
    print(">" * 48)


# for t in s.find_all('table'):
#     print(t)
#     print(list(t.strings))


# for res in s.find_all("tr"):
#     print(res)
#     print("*" * 48)


# docs = []

# for res in s.find_all("a"):
#     # print(res)
#     try:
#         c = res['class']
#     except:
#         c = []
#     S = list(filter(lambda x: "draw" in x.lower(), res.strings))
#     print(S)
#     if S:
#         docs.append([res['href'], c, list(res.strings)])

#     print(res['href'], c, list(res.strings))
#     print("*" * 48)
# print(docs)


# with open(regatta.data / "home.html", "w", encoding="utf8") as f:
#     f.write(m.text)


if __name__ == "__main__":
    pass

    data_files = {
        "event_page": {"url": "http://", "exists": False, "checksum": 0},
        "event_page_xlsx": {"url": "http://", "exists": False, "checksum": 0},
        "draw_page": {"url": "http://", "exists": False, "checksum": 0},
        "draw_page_xlsx": {"url": "http://", "exists": False, "checksum": 0},
        "documents": [
            {"url": "http://", 'title': "document", "type": "html", "checksum": 0},
            {"url": "http://", 'title': "document", "type": "pdf", "checksum": 0},
        ],
    }
    with open("data_files.json", "w", encoding="utf8") as f:
        f.write(json.dumps(data_files, indent=4))
