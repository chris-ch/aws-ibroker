import json
from typing import Any, Type


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    cls.__str__ = __str__
    return cls


def to_json(obj: Any) -> str:
    return json.dumps(obj.__dict__, default=lambda o: o.__dict__, indent=4)


def from_json(some_class: Type, json_str: str) -> Any:
    as_dict = json.loads(json_str)
    