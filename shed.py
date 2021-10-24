"""
create a set of boats with a location
put any boats in the river on the trailer
ask for a boat of type (x) from the trailer
if not, ask for a boat of type (x) from the shed.
    put the boat in the river 

"""
from pathlib import Path
import csv
from dataclasses import dataclass, field
from enums import Location, Cox, Stroke, Seats, Gender, Age_Group
from typing import List
from arrow import Arrow
from bookings import Booking


@dataclass(eq=False)
class Boat:
    name: str = ""
    seats: List[Seats] = field(default_factory=list)  # 1 | 2 | 4 | 8
    cox: List[Cox] = field(default_factory=list)  # COXED | COXLESS
    stroke: List[Stroke] = field(default_factory=list)  # SCULL | SWEEP
    rig: List[Stroke] = field(default_factory=list)
    re_riggable: List[bool] = field(default_factory=list)
    gender: List[Gender] = field(default_factory=list)  # M | W | SB | SG
    age_group: List[Age_Group] = field(default_factory=list)
    location: Location = Location.SHED  # SHED | TRAILER | WATER
    last_used: List[Arrow] = field(default_factory=list)
    booking: List[Booking] = field(default_factory=list)
    history: List[Booking] = field(default_factory=list)

    def re_rig(self, stroke=None):
        if Stroke.NONE not in self.rig:
            self.rig = list(set(self.stroke) - set(self.rig))
            self.booking[0].re_rig = True
        else:
            self.rig = [stroke]


def make_boat(r):

    # ['name', 'seats', 'sweep', 'scull', 'cox', 'age_group', 'gender']
    # print(r)
    [name, seats, sweep, scull, cox, age, gender] = r

    seat_number = [0, 1, 2, 4, 8].index(int(seats)) + 1
    age_groups = list(
        map(
            lambda x: ["", "U13", "U14", "U15", "U16", "O"].index(x) + 1, age.split(",")
        )
    )
    ages = list(map(lambda x: Age_Group(x), age_groups))
    # print("AGs", age, age_groups, ages)

    if int(cox):
        cox = [Cox.COXED]
    else:
        cox = [Cox.COXLESS]
    re_riggable = [False]
    if int(sweep) and int(scull):
        stroke = [Stroke.SWEEP, Stroke.SCULL]
        rig = [Stroke.NONE]
        re_riggable = [True]
    elif int(sweep):
        stroke = [Stroke.SWEEP]
        rig = [Stroke.SWEEP]
    else:
        stroke = [Stroke.SCULL]
        rig = [Stroke.SCULL]

    gender = [Gender.NONE]
    if gender == "SB":
        gender = [Gender.MALE]
    if gender == "SG":
        gender = [Gender.FEMALE]
    if gender == "Mixed":
        gender = [Gender.FEMALE, Gender.MALE]
    if gender == [Gender.NONE]:
        gender = [Gender.FEMALE, Gender.MALE]

    return Boat(
        name=name,
        seats=[Seats(seat_number)],
        cox=cox,
        stroke=stroke,
        age_group=ages,
        gender=gender,
        rig=rig,
        re_riggable=re_riggable,
    )


with open(Path("inventories/boats.csv")) as f:
    data = [x for x in csv.reader(f) if x]

boats = list(map(make_boat, data[1:]))

if __name__ == "__main__":
    # print(B)
    print(boats[-20:-10])

    print(boats[0].rig)

    print(all(map(lambda x: x.location == Location.SHED, boats)))
    print(any(map(lambda x: x.name == "The Outboard", boats)))
    assert all(map(lambda x: x.location == Location.SHED, boats)) == True
    print(boats[0])
    gunn = list(filter(lambda x: x.name == "The Gunn", boats))[0]
    gunn.location = Location.TRAILER
    print(gunn)
    print(boats[0])
    re_riggable_pairs = list(
        filter(lambda x: x.re_riggable and Seats.TWO in x.seats, boats)
    )
    for boat in re_riggable_pairs:
        print(boat.name, boat.seats, boat.re_riggable, boat.rig)
        boat.re_rig(Stroke.SCULL)
        print(boat.name, boat.seats, boat.re_riggable, boat.rig)
        boat.re_rig()
        print(boat.name, boat.seats, boat.re_riggable, boat.rig)
        boat.re_rig()
        print(boat.name, boat.seats, boat.re_riggable, boat.rig)
