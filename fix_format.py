import json
import os
from copy import deepcopy
from typing import Dict, Any


def add_multiple_measures(d: Dict[str, Any]) -> Dict[str, Any]:
    new_d = deepcopy(d)
    for task in new_d["tasks"]:
        for x in ["dev", "test"]:
            new_d["tasks"][task][x] = {}
            new_d["tasks"][task][x]["f1"] = None
            if task == "SweWinogender":
                try:
                    new_d["tasks"][task][x]["parity"] = d["tasks"][task][x]["parity"]
                    new_d["tasks"][task][x]["alpha"] = d["tasks"][task][x]["alpha"]
                except TypeError:
                    new_d["tasks"][task][x]["parity"] = None
                    new_d["tasks"][task][x]["alpha"] = None
            else:
                new_d["tasks"][task][x]["alpha"] = d["tasks"][task][x]
    return new_d


def write_to_new_dir(d: Dict[str, Any], dir_name: str, fn: str) -> None:
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    with open(os.path.join(dir_name, fn), "w") as fout:
        json.dump(d, fout, indent=4)
    return


def fix_data_size(d: Dict[str, Any]) -> Dict[str, Any]:
    if d["model"]["data_size"] and type(d["model"]["data_size"]) == str:
        d["model"]["data_size"] = int(d["model"]["data_size"].split("G")[0])
    return d

def main() -> None:
    import sys
    fn_in = sys.argv[1]
    fn_out = fn_in.split("/")[-1]
    new_dir = "copies"
    with open(fn_in) as fin:
        d = json.load(fin)
    new_d = add_multiple_measures(d)
    new_d = fix_data_size(new_d)
    write_to_new_dir(new_d, new_dir, fn_out)
    return


if __name__ == "__main__":
    main()
