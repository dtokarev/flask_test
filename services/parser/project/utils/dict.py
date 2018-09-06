from typing import Union


def get_by_list(d: dict, l: list) -> Union[str, None]:
    for e in l:
        if e in d:
            return d.get(e)


def model_to_dict(obj):
    from sqlalchemy import inspect
    from datetime import datetime, date
    import enum

    def convert(exp):
        if isinstance(exp, (datetime, date)):
            return exp.isoformat()
        elif isinstance(exp, enum.Enum):
            return exp.value
        return exp

    return {c.key: convert(getattr(obj, c.key))
            for c in inspect(obj).mapper.column_attrs}