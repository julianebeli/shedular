from dataclasses import dataclass
from arrow import Arrow


@dataclass
class Booking:
    launch: Arrow
    race: Arrow
    dock: Arrow
    re_rig: bool = False
