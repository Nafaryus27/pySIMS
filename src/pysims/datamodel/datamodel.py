from json import dumps
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict
from .semantic import Semantic
from .sims_parser import Parser

# Type Aliases
Data_t = Dict[str, list | Dict[str, list]]


@dataclass
class Record:
    """
    Helper class to store the results of processings along with the arguments.
    """
    args: list
    kwargs: dict
    result: Any

    
class Crater:
    """
    This is the generic data model class, which is inherited by
    DepthProfiles, MassSpectrum and EnergySpectrum.  It is used to
    hold the raw data and metadata along with the results of
    processings applied on data.

    :param path: path to data file (must be in the CAMECA .ms,.dp or
        .nrj ascii file format)
    :type path: str

    .. note::
    This class is not meant to be used directly.
    """
    def __init__(self, path: str):
        with open(path, "r", encoding="latin1") as f:
            raw = f.read()

        parser = Parser(semantics = Semantic())
        extract = parser.parse(raw)

        self._raw_data: Data_t = extract["data"]
        self._raw_metadata: Data_t = extract["metadata"]
        self._properties: Dict[str, Record] = {}

    def __str__(self):
        return dumps(self._data)

    @property
    def data(self) -> Data_t:
        return self._raw_data.copy()

    @property
    def properties(self) -> Dict[str, Record]:
        return self._properties.copy()

    def _get_attr(self, attr) -> Any:
        return self._raw_data[attr]
    
    def _get_elem_attr(self, elem, attr) -> Any:
        return self._raw_data[elem][attr]
        
    def _update_property(self, name: str, record: Record):
        self._properties[name] = record

    def get_result(self, name: str) -> Any:
        return self._properties[name].result


def processing(func):
    """
    Decorator function used to automatically store the results of a
    processing as a property in the Crater instance.  The decorated
    processing function must take data (ie.  DepthProfiles,
    MassSpectrum, EnergySpectrum), as first argument, as it will store
    the result of the processing.

    :param func: the processing function to decorate
    :type func: function

        .. note::

        The decorated function will still return the result of the
        initial function.
    """
    
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        result = func(data, *args, **kwargs)

        record = Record(args, kwargs, result)
        data.update_property(func.__name__, record)
        
        return result
    return wrapper
