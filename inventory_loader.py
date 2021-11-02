from typing import List, Dict
import csv
from config import season


def load_csv(file):
    data = []
    with open(file, encoding="utf8") as f:
        c = csv.DictReader(f)
        for row in c:
            data.append(row)
    return data


def load_db_table(name):
    pass


def regattas() -> List:
    return load_csv(season)


def current_regatta() -> Dict:
    try:
        return list(filter(lambda x: x["complete"].lower() == "n", regattas()))[0]
    except IndexError:
        exit("EXIT: No regatta found ...")


if __name__ == "__main__":
    r = regattas()
    current = list(filter(lambda x: x["complete"].lower() == "n", r))
    print(current)
    print(current_regatta())
