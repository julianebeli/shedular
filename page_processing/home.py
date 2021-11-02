from bs4 import BeautifulSoup as Soup  # type: ignore[import]

'''this code operates on the text in the div.rm_content'''


def clean_string(s):
    return s.strip().replace('\xa0', '')


def get_page_links(s):
    links = []
    anchors = s.find_all("a")
    for a in anchors:
        string = list(map(clean_string, a.strings))
        string.append(a["href"])
        links.append(string)
    return list(filter(lambda x: len(x) > 1 and (x[1].split("/")[-1] in ["events", "draw"]), links))


def get_doc_data(s):
    return list(filter(lambda x: x and x != 'Documents', map(clean_string, s)))


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


def home_page_processor(s: str):
    soup = Soup(s, "lxml")
    content = soup.find(class_="rm_content")

    tables = content.find_all('table')
    [links, data, docs] = list(
        filter(lambda x: not isinstance(x, str), tables[1].tr.children)
    )
    return [
        get_page_links(links),
        get_regatta_data(data.strings),
        get_doc_data(docs.strings),
    ]
