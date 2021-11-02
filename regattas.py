# from typing import List, Dict
from pathlib import Path
from dataclasses import dataclass  # , field
from arrow import Arrow

# from inventory_loader import current_regatta


@dataclass
class Regatta:
    id: str
    name: str
    date: Arrow
    days: str
    venue: str
    complete: bool
    organisation: str
    folder: Path


# @dataclass
# class regatta:
#     id: str
#     date: str
#     days: str
#     name: str
#     venue: str
#     type: str
#     complete: str
#     current_day: str = "1"
#     current_path: Path = Path()
#     folder: Path = Path()
#     events: List[Path] = field(default_factory=list)
#     draws: List[Path] = field(default_factory=list)
#     entries: List[Path] = field(default_factory=list)

#     def make_path(self, name: Path, ext: str):
#         self.new_attr: int = 4


if __name__ == "__main__":
    r = current_regatta()
    print(r)
    # 13/3/2021
    date = arrow.get(r['date'], 'DD/M/YYYY')
    # r.update(dict(events=[], draws=[], entries=[]))
    r.update(dict(date=date, folder=Path(), data=Path()))
    R = Regatta(**r)
    print(R.complete)
    # R.make_path(Path("html"), "html")
    # print(R.new_attr)
    print(vars(R))
    R.added_attr = 7
    print(vars(R))
