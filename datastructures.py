'''
create all the data structures in one place so you can change them easily
'''
from typing import Dict, List, NamedTuple
from collections import namedtuple

'''events'''

event: NamedTuple = namedtuple(
    "event", "event_id,code,name,gender,stroke,seats,cox,age_group,distance".split(",")
)
