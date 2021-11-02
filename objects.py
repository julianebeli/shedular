# from typing import List, Dict
from pathlib import Path
from dataclasses import dataclass
from arrow import Arrow


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
