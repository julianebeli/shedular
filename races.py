# from regattas import project_name
import csv


def load_entries(regatta):
    # project_path = project_name(regatta)
    # p = project_path / f"raw/{regatta.id}_entries_{day}.csv"
    races = []
    with open(regatta['current_file'], "r", encoding="utf-8-sig", newline="\n") as f:
        f = [x for x in csv.DictReader(f) if "friends" in x["school"].lower()]
        for row in f:
            races.append(dict(**row))
    return races


# regattas = live_regattas()
# print(regattas)
# # [regatta(id='5354', date='13/3/2021', days='2', name='SATIS Head of the River', venue='Lake Barrington', type='School', complete='0')]
# regatta = regattas[0]

# project_path = project_name(regatta)
# p = project_path / f"{regatta.id}_draw_{day}.csv"
