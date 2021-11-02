from pathlib import Path

rebuild = False
website = "https://rowingmanager.com/regattas/{}/"
inventories = Path("inventories")
regattas = Path("regattas")
boats = inventories / "boats.csv"
season = inventories / "season.csv"
venues = inventories / "venues.csv"
# data_pages = ['events', 'draw']
# data_files = ['draw']
