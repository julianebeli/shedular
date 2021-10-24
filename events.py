# from data import read_url
# from regattas import project_name
from typing import Dict
from pathlib import Path
import pandas  # type: ignore[import]
import csv
import re
from soups import file_to_soup
from enums import Cox, Stroke, Seats, Gender, Age_Group
from files import make_path, addfile
from datastructures import event

# event = namedtuple(
#     "event", "event_id,code,name,gender,stroke,seats,cox,age_group,distance".split(",")
# )


age = re.compile(r"Under (\d+)")

age_picker = {
    "13": Age_Group.U13,
    "14": Age_Group.U14,
    "15": Age_Group.U15,
    "16": Age_Group.U16,
}


def enum_events(e):
    gender = Gender.NONE
    stroke = Stroke.NONE
    seats = Seats.NONE
    cox = Cox.NONE
    age_group = Age_Group.NONE

    if e.gender == "Male":
        gender = Gender.MALE
    else:
        gender = Gender.FEMALE

    if "scull" in e.stroke.lower():
        stroke = Stroke.SCULL
    else:
        stroke = Stroke.SWEEP

    if e.seats == 1:
        seats = Seats.ONE
    elif e.seats == 2:
        seats = Seats.TWO
    elif e.seats == 4:
        seats = Seats.FOUR
    else:
        seats = Seats.EIGHT

    if '+' in e.code:
        cox = Cox.COXED
    else:
        cox = Cox.COXLESS

    a = age.search(e.name)
    if a:
        old = a.groups()[0]
        try:
            age_group = age_picker[old]
        except KeyError:
            age_group = Age_Group.OPEN
    else:
        age_group = Age_Group.OPEN

    return event(
        *[e.event_id, e.code, e.name, gender, stroke, seats, cox, age_group, e.distance]
    )


# [
#     '13',
#     'SB U13 1X',
#     'Schoolboys Under 13 Single Scull',
#     '-',
#     'School',
#     'Male',
#     'Scull',
#     '1',
#     '500M',
#     '',
# ]


def sieve(l):
    return dict(
        event_id=l[0],
        code=l[1],
        name=l[2],
        gender=l[5],
        stroke=l[6],
        seats=l[7],
        distance=l[8],
    )


def sieve2(l):
    return [l[0], l[1], l[2], l[5], l[6], l[7], l[8]]


def fix(s):
    w = list(filter(lambda x: x, re.split(r"\s", s)))
    return " ".join(w)


def make_csv(regatta, soup):
    fieldnames = "event_id,code,name,gender,stroke,seats,distance".split(",")
    event_list = []
    container = soup.find_all(id="events_table")[0]
    trs = container.find_all("tr")
    for tr in trs[1:]:
        this_event = []
        for td in tr.find_all("td"):
            this_event.append(fix(" ".join(list(td.strings))))
        this_event = sieve2(this_event)
        if len(list(filter(lambda x: x, this_event))) != 7:
            print("dropping event data")
            print(this_event)
            continue
        event_list.append(this_event)
    # event_map = list(map(sieve, event_list))
    with open(regatta["current_file"], "w", newline="\n", encoding="utf8") as f:
        c = csv.writer(f)
        c.writerow(fieldnames)
        for row in event_list:
            # print(row)
            c.writerow(row)

        # event_df = pandas.DataFrame(
        #     event_list,
        #     columns=[
        #         "event_id",
        #         "code",
        #         "name",
        #         "gender",
        #         "stroke",
        #         "seats",
        #         "distance",
        #     ],
        # )
        # event_df.to_csv(p, index=False)
    return addfile(regatta)


# def get_events(regatta, reload=False):
#     if reload:
#         pass
#     read_url(regatta, "events")
#     make_csv(regatta)
#     return


def load_events(regatta):
    # print(regatta)
    # print()
    # exit()
    # project_path = project_name(regatta)
    # p = project_path / f"raw/{regatta.id}_events.csv"
    p = Path(*[regatta['folder'], "data", "csv", f"{regatta['id']}_events_1.csv"])
    df = pandas.read_csv(p)
    # print(df[33:36])
    return df


def make_csv_from_html(regatta):
    print("making an event csv from html")
    regatta = make_path(regatta, "html", "events")
    soup = file_to_soup(regatta['current_file'])
    regatta = make_path(regatta, "csv", "events")
    # exit()
    # file = list(filter(lambda x: 'events' in x.name, regatta['data']['html']))[0]
    # name = f"{file.stem}.csv"
    # soup = file_to_soup(file)
    # print(soup)
    return make_csv(regatta, soup)


def make_csv_from_html_doc(regatta):
    return regatta


def process_events(regatta: Dict, ext: str):
    '''create and events.csv using ext data'''
    f = globals()[f"make_csv_from_{ext}"]
    return f(regatta)
