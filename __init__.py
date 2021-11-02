import json
import os

# import sys
from pathlib import Path


def flatten(L):
    return [item for sublist in L for item in sublist]


def pp(s):
    print(json.dumps(s, indent=4))


def read_json(fn):
    with open(fn, encoding="utf8") as f:
        return json.loads(f.read())


def write_json(fn, s):
    with open(fn, "w") as f:
        f.write(json.dumps(s, indent=4))


def path_compose(l):
    return os.sep.join(l)


def root_dir(f):
    p = os.path.realpath(f).split(os.sep)
    return os.sep.join(p[: p.index("canvas") + 1])


def root(f):
    p = Path(f).resolve().parts
    s = p[: p.index("canvas") + 1]
    return Path("/".join(s))
    # return os.sep.join(p[:p.index('canvas') + 1])


# canvas = root(__file__)
# canvas_tools = canvas / "tools"

# sys.path.append(str(canvas_tools))

# here = os.path.split(os.path.realpath(__file__))[0]
# staging = os.path.join(here, "staging")
# warehouse = os.path.join(here, "tasc_data")

if __name__ == "__main__":
    pass
# print(canvas)
# print(canvas_tools)
# print(sys.path)
