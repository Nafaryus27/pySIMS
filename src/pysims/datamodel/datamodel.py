import dataclasses
import json

__INTENSITY = "I[cnt/s]"
__DEPTH = "Depth[nm]"
__TIME = "Time[s]"
__MASS = "Mass[a.m.u]"
__ENERGY = "Energy[eV]"


@dataclasses.dataclass
class Crater:
    """Documentation for Data

    """
    __data_dict: dict

    def dump_raw_data(self):
        return self.__data_dict.copy()

    def get_attr(self, elem, attr):
        return self.__data_dict[elem][attr]

    def __str__(self):
        return json.dumps(self.__data_dict)

