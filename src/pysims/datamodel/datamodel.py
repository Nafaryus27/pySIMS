import dataclasses
import json
import functools
from typing import Any, Dict

from .semantic import Semantic
from .sims_parser import Parser


_INTENSITY = "I[cnt/s]"
_DEPTH = "Depth[nm]"
_TIME = "Time[s]"
_MASS = "Mass[a.m.u]"
_ENERGY = "Energy[eV]"

Data_t = Dict[str, list | Dict[str, list]]

@dataclasses.dataclass
class Record(object):
    args: list
    kwargs: dict
    result: Any

class Crater(object):
    """Documentation for Data
    
    """
    def __init__(self, path: str):
        with open(path, "r", encoding="latin1") as f:
            raw = f.read()

        parser = Parser(semantics = Semantic())
        extract = parser.parse(raw)

        self._raw_data:     Data_t = extract["data"]
        self._raw_metadata: Data_t = extract["metadata"]

        self._properties: Dict[str, Record] = {}
    
    def __str__(self):
        return json.dumps(self._data)

    @property
    def data(self) -> Data_t:
        return self._raw_data.copy()

    @property
    def properties(self) -> Dict[str, Record]:
        return self._properties.copy()

    def get_attr(self, attr) -> Any:
        return self._raw_data[attr]
    
    def get_elem_attr(self, elem, attr) -> Any:
        return self._raw_data[elem][attr]
        
    def update_property(self, procesing: str, record: Record):
        self._properties[processing] = record

    def get_result(self, processing: str) -> Any:
        return self._properties[name].result

    
def processing(func):
    @functools.wraps(func)
    def wrapper(data, *args, **kwargs):
        result = func(data, *args, **kwargs)

        record = Record(args, kwargs, result)
        data.update_processing(func.__name__, record)
        
        return result
    return wrapper
