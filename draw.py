from typing import List, Dict
from pathlib import Path

# from data import read_url
# from regattas import project_name
from soups import file_to_soup
from timing import race_start, event_day
from events import load_events
import re
import pandas
from functools import partial
from files import make_path, file_by_day, addfile
import arrow

# from __init__ import pp


def get_draw(regatta, day=1):
    read_url(regatta, "draw", day)
    make_csv(regatta, day)
    return


def unpack(l):
    if l:
        if len(l) > 1:
            l = [" ".join(l)]
        return l[0].replace("\xa0", "")
    else:
        return ""


def mark(s):
    f = re.findall(r"[a-z]\d", s, re.IGNORECASE)
    if f:
        return 1
    else:
        return 0


def mark2(s):
    f = re.findall(r"\d+\.", s, re.IGNORECASE)
    if f:
        return 1
    else:
        return 0


def has_id(tag):
    if tag.has_attr('id'):
        return tag['id'].startswith('R')
    else:
        return False


def club_crew(s):
    if not s:
        return ["", ""]
    # print(f"s >{s}<")
    clubs = set(
        "Sandy Bay,St Virgils,TUBC,Friends,Bucks,DMCRC,North"
        " Esk,Tamar,Ulverstone,Huon,URC/KRC,Mersey,LINDF/URC,New"
        " Norfolk,Kentish,BRC/HUON,TFNDS/BRC,Lindisfarne"
        " Comp.,URC/LINDF,BRC/KRC,Lindisfarne,BRC/URC,BRC/TFNDS,BRC/NWNFK,HUON/NWNFK,BRC/NESK"
        .split(",")
    )
    club = list(filter(lambda x: x in s, clubs))
    # print("club", club)
    if club:
        crew = list(filter(lambda x: x, s.split(club[0] + " ")))
        return [club[0], "[" + crew[0] + "]"]
    else:
        if s:
            print("no club for", s)
    return ["", ""]


def eventfinder(event_data: pandas.DataFrame, code):
    # print(code)
    s = event_data[event_data["code"] == code]
    S = s.to_dict(orient='list')
    return S


def create_doc_data(regatta, draw_soup):
    event_data = load_events(regatta)
    extractor = partial(eventfinder, event_data)
    columns = (
        "Race,Event,Div,Time,Dis,A,Lane1,Lane2,Lane3,Lane4,Lane5,Lane6,Lane7,Lane8"
        .split(",")
    )
    # new_cols = "date,day,race,event,div,time,distance,alpha,lane,club,crew".split(",")
    # new_cols = "race,time,event_id,event_name,event_code,seats,alpha,lane,heat,distance,school,crew,cox,coach".split(
    #     ","
    # )
    row_size = len(columns)
    rows = []
    print(row_size, columns)
    trs = draw_soup.find_all('tr')
    for tr in trs:
        rows.append(
            list(map(unpack, (map(lambda x: list(x.strings), tr.find_all("td")))))
        )
    new_data = []
    day = 0
    date = ""
    last_event = ""
    for row in rows:

        try:
            a = arrow.get(row[0], 'D MMMM YYYY')
            print(a)
            if a:
                day += 1
                date = row[0]
        except:
            pass
        if len(row) == row_size:
            # print(row)
            if not row[0].isnumeric():
                continue
            if row[1]:
                last_event = row[1]
                this_event = extractor(last_event)
                # print(last_event)
            for i, j in enumerate(range(8)):
                # 1:20 PM
                club, crew = club_crew(row[j + 6])
                time = date + " " + row[3]
                # print(f"time>{time}<")
                b = arrow.get(time, 'D MMMM YYYY h:mm A')
                print(b)
                # exit()
                d = dict(
                    day=day,
                    race=row[0],
                    start=b,
                    event_id=this_event['event_id'][0],
                    event_name=this_event['name'][0],
                    event_code=this_event['code'][0],
                    seats=this_event['seats'][0],
                    alpha=row[5],
                    lane=i + 1,
                    heat=row[2],
                    distance=row[4],
                    school=club,
                    crew=crew,
                    cox=[],
                    coach=[],
                )
                # d = [row[0]] + [row[3]] + row[2:6] + [i + 1] + club_crew(row[j + 6])
                if crew:
                    # print(d)
                    new_data.append(d)

    # for row in new_data:
    #     print(row)
    days = sorted(list(set(map(lambda x: x['day'], new_data))))
    for day in days:
        races = list(filter(lambda x: x['day'] == day, new_data))
        entrants_df = pandas.DataFrame(races)
        file = regatta['folder'] / "data" / "csv" / f"{regatta['id']}_entries_{day}.csv"
        entrants_df.to_csv(file, index=False)
    return new_data


def create_data(draw_soup):
    print("In create data")

    # project_path = project_name(regatta)
    # draw_soup = file_to_soup(f"{project_path}/raw/html/{regatta.id}_draw_{day}.html")
    id_list = []
    # print("L", len(list(draw_soup.body.children)))
    id_list = draw_soup.find_all(has_id, recursive=True)
    id_list = list(map(lambda x: x['id'], id_list))
    # print(id_list)

    race_data = []
    # for id in id_list[-5:]:
    for id in id_list:
        # the race data is in chunks of a,table,table
        i = []
        # print("ID", id)
        a = draw_soup.find(id=id)
        # info.append(a)
        while len(i) != 2:
            a = a.next_sibling
            if hasattr(a, "table"):
                i.append(a)

        data = []
        for t in i:
            data.append(
                # list(map(lambda x: list(x.strings), t.find_all("td")))
                list(map(unpack, (map(lambda x: list(x.strings), t.find_all("td")))))
            )

        mask = list(map(mark, data[1]))
        lanes = []
        for i, j in enumerate(mask):
            if j == 1:
                lanes.append(data[1][i : i + 5])

        race_data.append([data[0], lanes])
    return race_data


def race_no(s):
    return int(s.split(" ")[-1])


def event_details(event_data: pandas.DataFrame, s):
    print("decoding", s)
    events = []
    dots = list(filter(lambda x: x, re.split(r"(\d+\.)", s)))
    print(dots)
    dotmask = list(map(mark2, dots))
    print(dotmask)
    for i, j in enumerate(dotmask):
        if j:
            event_no = dots[i][:-1]
            # df[df['Sales'] > 300]
            seats = event_data[event_data["event_id"] == int(event_no)]["seats"].values[
                0
            ]
            d = list(map(lambda x: x.strip(), dots[i + 1].split(":")))
            description = d[1]
            code = d[0]
            events.append([event_no, code, description, seats])

    return events


def clean(s):
    return list(
        filter(
            lambda y: y,
            map(lambda x: x.strip().encode("ascii", "ignore").decode(), s.split(",")),
        )
    )


def clean_distance(s):
    return int(s[:-1])


def get_people(p):
    # p = " ".join(p)
    # print(p)
    crew = []
    cox = []
    coach = []
    splits = []
    roles = ["crew"]
    has_cox = re.search("Cox:", p)
    has_coach = re.search("Coach:", p)
    has_coaches = re.search("Coaches:", p)
    if has_cox:
        splits.extend(has_cox.span())
        roles.append("cox")
    if has_coach:
        splits.extend(has_coach.span())
        roles.append("coach")
    if has_coaches:
        splits.extend(has_coaches.span())
        roles.append("coach")
    # print(splits)
    # print(roles)

    for role in roles:
        if role == "crew":
            try:
                crew = p[: splits[0]]
            except:
                crew = p
            crew = clean(crew)
        if role == "cox":
            try:
                cox = p[splits[1] : splits[2]]
            except IndexError:
                cox = p[splits[1] :]
            cox = clean(cox)
        if role == "coach":
            coach = p[splits[-1] :]
            coach = clean(coach)
    return dict(crew=crew, cox=cox, coach=coach)


def entries_file(csv_file):
    parts = list(csv_file.parts)
    name = parts[-1]
    name = name.replace("draw", "entries")
    print(name)
    parts[-1] = name
    return Path(*parts)


def make_entrants(csv_file, data):
    entrants = []
    for e in data:
        race_id = e["race"]
        start = e["start"]
        event = e["event"][0]
        # print(event)
        event_id = event[0]
        event_name = event[2]
        event_code = event[1]
        event_seats = event[3]
        alpha = e["alpha"]
        heat = e["heat"]
        distance = e["distance"]
        for f in e["field"]:
            lane = f['lane']
            school = f['school']
            crew = f["crew"]["crew"]
            cox = f["crew"]["cox"]
            coach = f["crew"]["coach"]
            entrants.append(
                dict(
                    race=race_id,
                    start=start,
                    event_id=event_id,
                    event_name=event_name,
                    event_code=event_code,
                    seats=event_seats,
                    alpha=alpha,
                    lane=lane,
                    heat=heat,
                    distance=distance,
                    school=school,
                    crew=crew,
                    cox=cox,
                    coach=coach,
                )
            )
    entrants_df = pandas.DataFrame(entrants)
    entrants_df.to_csv(entries_file(csv_file), index=False)


def get_day(name):
    # last digit before the file extension
    return name.stem.split(".")[0].split("_")[-1]


def extract(event_data, regatta_day, day, data):
    # print(data)
    [race, event, heat, nothing, start, distance] = data[0]
    if heat.lower() == "non-event":
        return None
    events = event_details(event_data, event)
    alpha = data[1][0][0][0]
    distance = clean_distance(distance)
    field = []

    for team in data[1]:
        lane = team[0][1]
        field.append(dict(lane=lane, school=team[2], crew=get_people(team[4])))
    return dict(
        race=race_no(race),
        event=events,
        heat=heat,
        start=str(race_start(regatta_day, day, start)),
        distance=distance,
        alpha=alpha,
        field=field,
    )


def make_csv(regatta, soup):
    day = regatta['current_day']
    race_data = create_data(soup)
    event_data = load_events(regatta)
    extractor = partial(extract, event_data, event_day(regatta['date']), day)
    new_race_data = list(map(extractor, race_data))
    new_race_data = list(filter(lambda x: x, new_race_data))
    make_entrants(regatta['current_file'], new_race_data)
    draw_df = pandas.DataFrame(new_race_data)
    draw_df.to_csv(regatta['current_file'], index=False)

    # file = regatta['folder'] / "data/csv" / name

    # if not file.exists():
    #     race_data = create_data(soup)
    #     print(race_data)

    #     event_data = load_events(regatta)
    #     extractor = partial(extract, event_data, event_day(regatta.date), day)
    #     new_race_data = list(map(extractor, race_data))
    #     make_entrants(regatta, day, new_race_data)
    #     draw_df = pandas.DataFrame(new_race_data)
    #     draw_df.to_csv(p, index=False)
    # else:
    #     pass
    return addfile(regatta)


def load_draw(regatta, day):
    project_path = project_name(regatta)
    p = project_path / f"{regatta.id}_draw_{day}.csv"
    df = pandas.read_csv(p)
    # print(df[33:36])
    return df


# def load_events(regatta):
#     project_path = project_name(regatta)
#     p = project_path / f"{regatta.id}_events.csv"


def make_csv_from_html(regatta):
    print("making an draw csv from html")

    files: List[Path] = list(
        filter(lambda x: 'draw' in x.name, regatta['data']['html'])
    )
    print(files)
    for i in range(len(files)):
        i += 1
        print(i)
        regatta['current_day'] = i
        file = file_by_day(files, i)
        soup = file_to_soup(file)
        regatta = make_path(regatta, "csv", "draw")
        make_csv(regatta, soup)
    return regatta


def make_csv_from_html_doc(regatta):
    print("making an draw csv from html")
    file = regatta['folder'] / "data" / "html" / f"{regatta['id']}_draw_doc.html"
    soup = file_to_soup(file)
    race_data = create_doc_data(regatta, soup)  # made entries
    days = sorted(list(set(map(lambda x: x['day'], race_data))))
    for day in days:
        regatta['current_day'] = day
        races = list(filter(lambda x: x['day'] == day, race_data))
        regatta = make_path(regatta, "csv", "draw")
        draw_df = pandas.DataFrame(races)
        draw_df.to_csv(regatta['current_file'], index=False)

    # event_data = load_events(regatta)
    # extractor = partial(event_details, event_data)
    # new_race_data = list(map(extractor, race_data))
    # print(new_race_data)
    return regatta


def process_draw(regatta, ext):
    f = globals()[f"make_csv_from_{ext}"]
    return f(regatta)
