import config
from pathlib import Path
from regattas import Regatta
from distutils.dir_util import copy_tree


def get_name(regatta: Regatta) -> Path:
    id = regatta.id
    ev = regatta.date.format("YYYYMMDD")
    name = regatta.name.replace(" ", "_")
    return Path(f"{config.regattas}/{id}_{ev}_{name}")


def structure(regatta: Regatta) -> None:
    if not regatta.folder.is_dir():
        regatta.folder.mkdir(exist_ok=True)
        copy_tree("./template", f"./{regatta.folder}")
    else:
        print(f"Resources available in {regatta.folder}")
    return


def destructure(regatta: Regatta) -> None:
    pass


def build(regatta: Regatta, rebuild=False) -> None:
    folder: Path = get_name(regatta)
    regatta.folder = folder
    if rebuild:
        destructure(regatta)
    structure(regatta)
    return regatta
