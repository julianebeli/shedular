from typing import Dict
from pathlib import Path

'''
the regatta dict has a current_file key.
at different satges of the program we need to access different files
so these functions can create the current_file and put it back in the regatta dict.
Then I don't have to keep fumbling over the file name
'''


def make_path(regatta, folder, name) -> Dict:
    file = Path(
        *[
            regatta['folder'],
            "data",
            folder,
            f"{regatta['id']}_{name}_{regatta['current_day']}.{folder.lower()}",
        ]
    )
    regatta.update(dict(current_file=file))
    return regatta


def file_by_day(files, day):
    def day_number(f):
        return f.stem.split(".")[0].split("_")[-1]

    return list(filter(lambda x: day_number(x) == str(day), files))[0]


def addfile(regatta):
    parts = regatta['current_file'].parts
    regatta["data"][parts[-2]].append(parts[-1])
    return regatta
