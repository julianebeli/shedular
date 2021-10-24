import config
from typing import Dict
from inventory_loader import regattas, current_regatta
from constructor import build

from harvester import harvest, probe
from events import process_events
from draw import process_draw
from allocation import do_allocation
from regattas import Regatta
import arrow
from pathlib import Path


def main():
    r = current_regatta()
    date = arrow.get(r['date'], 'DD/M/YYYY')
    r.update(dict(date=date, folder=Path(), data=Path()))
    regatta = Regatta(**r)
    print(regatta)
    build(regatta)
    print(regatta)
    probe(regatta)
    exit()
    regatta: Dict = build(current_regatta())
    probe_data(regatta)
    harvest_data(regatta)

    regatta = build(current_regatta())
    harvest(regatta, "xlsx")
    regatta = build(current_regatta())

    regatta = process_events(regatta, config.source)
    regatta = process_draw(regatta, config.source)
    do_allocation(regatta)


if __name__ == "__main__":
    main()
#     data = []
#     for regatta in regattas():
#         data.append(build(regatta))

#     for row in data:
#         # harvest(row, "html")
#         harvest(row, "xlsx")
#         # print(bool(row['data']['xlsx']))
#         print()
