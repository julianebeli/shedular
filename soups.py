from bs4 import BeautifulSoup as Soup


def text_to_soup(t):
    return Soup(t, "lxml")


def file_to_soup(f):
    with open(f) as F:
        s = Soup(F.read(), "lxml")
    return s
