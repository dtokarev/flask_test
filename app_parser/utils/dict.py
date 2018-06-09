from typing import Union


def get_by_list(d: dict, l: list) -> Union[str, None]:
    for e in l:
        if e in d:
            return d.get(e)
