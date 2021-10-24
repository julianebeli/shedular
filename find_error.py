from typing import Dict, Set, Any
from enums import Location, Cox, Seats, Stroke, Age_Group, Gender
from shed import boats
from functools import reduce

# from events import load_events, enum_events
# from inventory_loader import regattas


def get_boat_here(boats, k, v, l):
    def get_at(x):
        a = getattr(x, k)
        if isinstance(a, list):
            return v in a
        else:
            return v == a

    return list(
        map(
            lambda y: [y.name, y.seats, y.cox, y.stroke, y.rig, y.gender, y.age_group],
            (filter(lambda x: (x.location == l) and get_at(x), boats)),
        )
    )


def show_boats(b):
    for x in b:
        print(x)


def find_error(boats, event):
    e = event._asdict()
    # print(e)

    for k in "gender,stroke,seats,cox,age_group".split(","):
        print("searching attribute:", k, e[k])
        # print(e[k])
        for loc in [Location.SHED, Location.TRAILER]:
            print(loc)
            # print(boats[0])
            # print(getattr(boats[0], k))
            b = get_boat_here(boats, k, e[k], loc)
            show_boats(b)


# def boat_set_value(key: str, value: Any, boat) -> Set:
#     return


# def boat_set_values(key: str, value: Any) -> Set:
#     return set(filter(lambda x: value in getattr(x, key), boats))


def boat_set(value, this_boat_set: Set = None) -> Set:

    if this_boat_set == set():
        return this_boat_set

    if not this_boat_set:
        this_boat_set = set(boats)

    key = value.__class__.__name__.lower()  # get the name of the enum
    print(f"filtering boats: {key} = {value}")

    if key in ['cox', 'location', 'rig', 'seats']:
        return set(filter(lambda x: getattr(x, key) == value, this_boat_set))

    else:
        return set(filter(lambda x: value in getattr(x, key), this_boat_set))


def intersect(set1, attr1) -> Set:
    print(len(set1))
    return boat_set(attr1, set1)
    # return set1 & set2


if __name__ == "__main__":

    results = reduce(
        intersect,
        [Seats.EIGHT, Gender.FEMALE, Age_Group.U16, Location.SHED],
        boat_set(Stroke.SWEEP),
    )
    print(results)
