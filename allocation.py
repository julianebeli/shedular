from typing import List, Dict, Set
from pathlib import Path
from functools import reduce
import csv

# from regattas import live_regattas
from collections import namedtuple, Counter
from enums import Location, Stroke  # Cox, Seats, Gender, Age_Group
from shed import boats
from races import load_entries
import arrow
from events import load_events, enum_events
from random import choice
from files import make_path
from find_error import find_error


metric = namedtuple("metric", ["location", "distance", "lead_in", "race_time", "lead_out"])  # type: ignore[misc]
event = namedtuple(  # type: ignore[misc]
    "event", "event_id,code,name,gender,stroke,seats,distance".split(",")
)
venues = Path("inventories/venue.csv")
with open(venues) as f:
    metrics = [metric(*x) for x in csv.reader(f) if x][1:]


def print_time(s):
    return arrow.get(s).format('hh:mm a')


def get_events(regatta) -> List[Dict]:
    event_data = load_events(regatta)
    event_list = []
    for row in event_data.iloc():
        x = enum_events(event(*dict(row).values()))
        event_list.append(x)
    return event_list


def get_time_frame(local_metrics, entry):

    # print(local_metrics)

    this_metric = list(
        filter(lambda x: x.distance == entry["distance"], local_metrics)
    )[0]
    base_time = arrow.get(entry["start"])
    lead_in = base_time.shift(minutes=(int(this_metric.lead_in) * -1))
    lead_out = base_time.shift(
        minutes=(int(this_metric.race_time) + int(this_metric.lead_out))
    )
    return [lead_in, base_time, lead_out]


def rerack_boats(local_metrics, entry):
    [lead_in, race_time, lead_out] = get_time_frame(local_metrics, entry)
    # [<Arrow [2021-03-06T17:29:00+00:00]>, <Arrow [2021-03-06T17:54:00+00:00]>, <Arrow [2021-03-06T18:17:00+00:00]>]
    # This is the clock tick
    # boats can go from the water to the trailer if they are
    #     on the water
    #     the lead_out time is < the lead_in time of the event.
    # booking = dict(race=1,leadin=2,race_time=3,leadout=4)
    water_boats = list(filter(lambda x: x.location == Location.WATER, boats))

    for boat in water_boats:
        if boat.booking:
            # print(f"race {entry['race']}: lead_in {lead_in}")
            # print("booking lead out in boat", boat.booking[0])
            # print(boat.booking[0]["lead_out"] < lead_in)
            if boat.booking[0]["lead_out"] < lead_in:
                boat.last_used = [boat.booking[0]["lead_out"]]
                boat.booked.append(boat.booking[0])
                boat.booking = []
                boat.location = Location.TRAILER
                print(f"putting {boat.name} on the trailer")
                # print(boat)
                # print("*" * 48)

    return


def boat_set(filter_attr, this_boat_set: Set = None) -> Set:

    if this_boat_set == set():
        return this_boat_set

    if not this_boat_set:
        this_boat_set = set(boats)

    key = filter_attr.__class__.__name__.lower()  # get the name of the enum
    print(f"filtering boats: {key} = {filter_attr}")

    if key in ['cox', 'location', 'rig', 'seats']:
        return set(filter(lambda x: getattr(x, key) == filter_attr, this_boat_set))

    else:
        return set(filter(lambda x: filter_attr in getattr(x, key), this_boat_set))


def intersect(set1, attr1) -> Set:
    print(len(set1))
    return boat_set(attr1, set1)


def choose_boat(vessels):
    # pick the boat which has been idle the longest.
    # if not vessels:
    #     print("no boats to pick from ...")
    #     for b in boats:
    #         print(b)
    #     exit()
    print("choosing", "-" * 48)
    print(list(map(lambda x: [x.name, x.last_used], vessels)))
    used_boats = list(filter(lambda x: x.last_used, vessels))
    # print("used", used_boats)
    if not used_boats:
        return choice(vessels)
    else:
        print("sorting", "." * 48)
        sorted_vessels = sorted(used_boats, key=lambda x: x.last_used)
        print(list(map(lambda x: [x.name, x.last_used], sorted_vessels)))
        print("sorting", "-" * 48)
        return sorted_vessels[0]


def get_boat(regatta, local_metrics, events, entry, day):
    [lead_in, race_time, lead_out] = get_time_frame(local_metrics, entry)

    def find_boats2(this_event, location):
        selected_boats = reduce(
            intersect,
            [this_event.cox, this_event.seats, this_event.gender, this_event.age_group],
            boat_set(this_event.stroke),
        )
        rigged_boats = set(
            filter(lambda x: x.rig in [Stroke.NONE, this_event.stroke], selected_boats)
        )
        if rigged_boats:
            selected_boats = rigged_boats
        else:
            print("I couldn't find the boat with the right rig ...")
        located_boats = boat_set(location, selected_boats)
        if located_boats:
            return located_boats
        else:
            print("I couldn't find the boat I need on the trailer ...")
            return selected_boats

    # def find_boats(this_event, location):
    #     # print(">", this_event)
    #     rigged = list(
    #         filter(
    #             lambda x: (this_event.stroke in x.stroke)
    #             and (x.seats == this_event.seats)
    #             and (x.rig in [Stroke.NONE, this_event.stroke])
    #             and (this_event.gender in x.gender)
    #             and (this_event.age_group in x.age_group)
    #             and (this_event.cox == x.cox)
    #             and (x.location == location),
    #             boats,
    #         )
    #     )
    #     # print(location, ">>>>>>>rigged", rigged)
    #     if not rigged:
    #         # print(
    #         #     "did not find a boat with the right rigging at"
    #         #     f" {location}.>>>>>>>>>>>>>>>"
    #         # )
    #         rigged = list(
    #             filter(
    #                 lambda x: (this_event.stroke in x.stroke)
    #                 and (x.seats == this_event.seats)
    #                 # and (x.rig in [Stroke.NONE, this_event.stroke])
    #                 and (this_event.gender in x.gender)
    #                 and (this_event.age_group in x.age_group)
    #                 and (this_event.cox == x.cox)
    #                 and (x.location == location),
    #                 boats,
    #             )
    #         )
    #         # print()
    #         # print(location, "rigged<<<<<<<", rigged)
    #     # print()
    #     return rigged

    # to do:
    #     put used boats in trailer
    #     look for next boat on the trailer
    #     look in shed

    # print(entry)
    # print(boats[0])
    # need event info to find the right boat for the job
    this_event = list(filter(lambda x: x.event_id == int(entry["event_id"]), events))[0]
    print("this event is:", this_event)
    print(f"day={day}")

    suitable_boats = list(find_boats2(this_event, Location.TRAILER))
    # if not suitable_boats and day == day:
    #     print("I couldn't find the boat I need on the trailer ...")
    #     suitable_boats = find_boats(this_event, Location.SHED)
    if not suitable_boats:
        print(f"Can't find a boat for {this_event}")
        find_error(boats, this_event)

        return
    # print(suitable_boats)

    #     print("X" * 48)
    #     return
    # for thing in these_boats:
    #     print("I found", thing)
    # age_group_boats = list(
    #     filter(lambda x: this_event.age_group in x.age_group, suitable_boats)
    # )

    # if age_group_boats:
    #     print("age group boats", age_group_boats)
    #     print("V" * 48)
    #     suitable_boats = age_group_boats
    # else:
    #     print(suitable_boats)
    this_boat = choose_boat(suitable_boats)

    # this_boat = choice(suitable_boats)
    print("I chose this boat:", this_boat.name)

    re_rig = ""
    if this_boat.rig in [Stroke.NONE, this_event.stroke]:
        this_boat.rig = this_event.stroke
        re_rig = False
    else:
        this_boat.rig = this_event.stroke
        re_rig = True
    print("re-rig required?", re_rig)
    this_boat.location = Location.WATER
    this_boat.booking.append(
        dict(
            race=entry["race"],
            lead_in=lead_in,
            race_time=race_time,
            lead_out=lead_out,
            re_rig=re_rig,
        )
    )

    print("UPDATED", this_boat)
    return this_boat


def prepare_for_publication(entries):
    print("publishing >>>>", entries[0])

    def sieve(e):
        time = print_time(e['start'])
        crew = "".join(filter(lambda x: x != "'", e['crew'][1:-1]))
        cox = "".join(filter(lambda x: x != "'", e['cox'][1:-1]))
        event = e['event_id'] + ". " + e['event_name'] + ". " + e['event_code']
        rerig = ""
        boat = ""
        try:
            if e['rerig']:
                rerig = "rerig"
            else:
                rerig = ""
            boat = e['boat']
        except KeyError:
            print(e)

        if "/" in e['school']:
            composite = e['school']
        else:
            composite = ""

        return dict(
            race=e['race'],
            start=time,
            event=event,
            bow_board=e['alpha'],
            lane=e['lane'],
            boat=boat,
            rerig=rerig,
            composite=composite,
            crew=crew,
            cox=cox,
        )

    return list(map(sieve, entries))


def save_entries(regatta, entries):
    entries = prepare_for_publication(entries)
    with open(regatta['current_file'], "w", newline="\n", encoding="utf") as f:
        c = csv.DictWriter(f, fieldnames=entries[0].keys())
        c.writeheader()
        for row in entries:
            c.writerow(row)


# print(boats[0].location)
# print(">>", boats[0].location == Location.SHED)

# # print(boats[0].location.name == Location.SHED.name)
# print("8 seats", boats[0].seats == Seats.EIGHT)
# # print(Location.SHED.value)


def do_allocation(regatta):
    for boat in boats:
        print(boat)
    print(len(boats))
    events = get_events(regatta)

    no_boat = []
    local_metrics = list(filter(lambda x: x.location == regatta['venue'], metrics))

    for day in [x + 1 for x in range(int(regatta['days']))]:
        regatta['current_day'] = day
        regatta = make_path(regatta, "csv", "entries")
        entries = load_entries(regatta)
        # print(entries)
        for entry in entries:
            if "boat" not in entry.keys():
                print(entry)

                print("reracking")
                rerack_boats(local_metrics, entry)

                the_boat = get_boat(regatta, local_metrics, events, entry, day)
                if not the_boat:
                    no_boat.append(entry)
                    continue
                print("edit entry with", the_boat)
                entry["boat"] = the_boat.name
                entry["rerig"] = the_boat.booking[0]["re_rig"]
                entry["launch_time"] = the_boat.booking[0]["lead_in"]
                entry["dock_by"] = the_boat.booking[0]["lead_out"]
                print(Counter(list(map(lambda x: x.location, boats))))
                print()
        regatta = make_path(regatta, "csv", "allocation")
        save_entries(regatta, entries)

    sheded = list(filter(lambda x: x.location == Location.SHED, boats))

    def trailer_boat(b):
        if b.booking:
            b.booked.append(b.booking[0])
        b.location = Location.TRAILER
        return

    watered = list(filter(lambda x: x.location == Location.WATER, boats))
    list(map(trailer_boat, watered))
    trailered = list(filter(lambda x: x.location == Location.TRAILER, boats))
    watered = list(filter(lambda x: x.location == Location.WATER, boats))
    print("Boats in the shed")
    data = []
    seat_map = [0, 0, 1, 2, 4, 8]
    for boat in sheded:
        print(boat.name, boat.seats, boat.gender, boat.age_group)
        data.append(
            dict(
                name=boat.name,
                seats=seat_map[boat.seats.value],
                race="",
                time="",
                launch="",
                dock="",
                re_rig="",
            )
        )
    print()
    print("Boats on the trailer")

    for boat in trailered:
        print(boat.name, boat.seats, boat.gender, boat.age_group)
        # print(boat.booking)
        for l in boat.booked:
            if l['re_rig']:
                rerig = 're_rig'
            else:
                rerig = ""
            data.append(
                dict(
                    name=boat.name,
                    seats=seat_map[boat.seats.value],
                    race=l['race'],
                    launch=print_time(l["lead_in"]),
                    time=print_time(l['race_time']),
                    dock=print_time(l["lead_out"]),
                    re_rig=rerig,
                )
            )

    regatta = make_path(regatta, "csv", "boat_schedule")
    with open(regatta['current_file'], "w", newline="\n", encoding="utf8") as f:
        c = csv.DictWriter(f, fieldnames=data[0].keys())
        c.writeheader()
        for row in data:
            c.writerow(row)
    print()
    print("Boats on the water")
    for boat in watered:
        print(boat.name, boat.seats, boat.gender, boat.age_group)
        # print(boat.booking)
        for line in boat.booked:
            print(line)
        print()

    print("No boat for:")
    for e in no_boat:
        print(e)
