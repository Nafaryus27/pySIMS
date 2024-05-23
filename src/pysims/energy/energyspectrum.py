#====================================================================#
#                                                                    #
#      This file contains the code for energy spectrum analysis      #
#                                                                    #
#====================================================================#

from pysims.datamodel import Crater
from pysims.utils import * 

from .isotopes import *

class EnergySpectrum(Crater):
    """
    Main class used for energy analysis, contains the raw data and the
    results of the processings applied on data.

    :param path: the path of the depthprofile ascii file
    :type path: str
    """
    
    @property
    def energy(self) :
        return self._get_attr(ENERGY)
    
    @property
    def intensity(self) :
        return self._get_attr(INTENSITY)
