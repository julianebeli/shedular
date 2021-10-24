from typing import Dict
import config
from pathlib import Path
from timing import event_day
from regattas import Regatta

project_folder = config.projects_folder
rebuild = config.rebuild


def get_name(regatta: Regatta) -> Path:
    # event_date = event_day(regatta.date)
    ev = regatta.date.format("YYYYMMDD")
    name = regatta.name.replace(" ", "_")
    return Path(f"{project_folder}/{ev}_{name}")


def structure(p: Path) -> None:
    if not p.exists():
        p.mkdir(mode=0o777)
    d = p / "data"
    if not d.exists():
        d.mkdir(mode=0o777)
        (d / "home").mkdir(mode=0o777)
        (d / "events").mkdir(mode=0o777)
        (d / "draw").mkdir(mode=0o777)

    return


def destructure(p: Path) -> None:
    pass


def data_files(p: Path) -> Dict:
    data = dict()
    for P in (p / "data").iterdir():
        k = P.parts[-1]
        files = list((p / "data" / k).glob("*"))
        data.update({k: files})

    return data


def build(regatta: Regatta, rebuild=False) -> None:

    folder: Path = get_name(regatta)
    regatta.folder = folder
    regatta.data = folder / "data"
    if rebuild:
        destructure(folder)
    structure(folder)
    # regatta.update(dict(folder=folder, current_day=1))
    data: Dict = data_files(folder)
    # regatta.update(dict(data=data))
    return regatta
