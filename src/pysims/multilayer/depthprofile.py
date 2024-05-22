#====================================================================#
#                                                                    #
# This file contains the code for multilayer depth profiles analysis #
#                                                                    #
#====================================================================#

import numpy as np
import scipy.signal as sig
from scipy.ndimage import uniform_filter1d

from pysims.utils import *
from pysims.datamodel import Crater


class DepthProfiles(Crater) :
    """
    Main class used for multilayer analysis, contains the raw data and
    the results of the processings applied on data.
    """
    def __init__(self, path):
        super().__init__(path)
        self._properties = {
            "plateaux indices" : {},
            "plateaux" : {},
            "standard deviation" : {},
            "interfaces" : {}
        }
    
    def intensity(self, elem: str) -> list:
        """
        Getter method to acces the intensities of an element's
        profile

        :param elem: the element
        :type elem: str

        :rtype: list
        """
        return self._get_elem_attr(elem, INTENSITY)

    def time(self, elem: str) -> list:
        """
        Getter method to acces the times of an element's profile

        :param elem: the element
        :type elem: str

        :rtype: list
        """
        return self._get_elem_attr(elem, TIME)

    def depth(self, elem: str) -> list:
        """
        Getter method to acces the depths of an element's profile

        :param elem: the element
        :type elem: str

        :rtype: list
        """
        return self._get_elem_attr(elem, DEPTH)    

    def locate_interfaces(self, elem: str, noise_filter_size=5, prominence=0.5) -> list:
        """
        Detects interfaces between plateaux.  The method used is to
        filter the noise, calculate the gradient of the filtered
        intensity and detect it's peaks.

        :param elem: the element which interfaces we want to locate
        :type elem: str

        :param noise_filter_size: the size of the filter applied for
            noise reduction
        :type noise_filter_size: int

        :param prominence: prominence value to select the peaks to
            detect.  Must be between 0 and 1.
        :type prominence: float
        """
        y = self.intensity(elem)
        smoothed_y = uniform_filter1d(y, size=noise_filter_size)
        gradient = normalize(np.abs(np.gradient(smoothed_y)))
        interfaces = list(sig.find_peaks(gradient, prominence=prominence)[0])
        
        self.properties["interfaces"][elem] = interfaces
        return interfaces
    
    def get_plateaux_indices(self, elem: str, interfaces_margin: int) -> list:
        """
        Returns the indices of the limits of all plateaux for the
        given element, minus the interfaces_margin.  The results is a
        list of tuples of the indices of each plateau.

        :param elem: the element
        :type elem: str

        :param interfaces_margin: the margin the apply to the detected
            interfaces
        :type interfaces_margin: int

        :rtype: list
        """
        interfaces = self.locate_interfaces(elem)
        interfaces.append(len(self.intensity(elem)) - 1)
        list_indices = [
            (interfaces[i] + interfaces_margin, interfaces[i+1] - interfaces_margin)
            for i in range(len(interfaces)-1)
        ]           
        
        self.properties["plateaux indices"][elem] = list_indices
        return list_indices

    def get_plateaux(self, elem: str, interfaces_margin: int):
        """
        Calculate the values of all the plateaux for the given element

        :param elem: the element
        :type elem: str

        :param interfaces_margin: the margin to apply to the detected
            plateaux
        :type interfaces_margin: int
        """
        plateaux = []
        for indices in self.get_plateaux_indices(elem, interfaces_margin):
            plateaux.append(
                calculate_plateau_value(self.intensity(elem), indices)
            )
        self.properties["plateaux"][elem] = plateaux
        return plateaux

    def get_plateaux_std(self, elem: str, interfaces_margin: int):
        std = []
        for indices in self.get_plateaux_indices(elem, interfaces_margin):
            std.append(
                calculate_std(self.intensity(elem), indices)
            )
        self.properties["standard deviation"][elem] = std
        return std

   

#======================== calculus functions ========================#

def normalize(array: np.ndarray) -> np.ndarray:
    """
    normalize a numpy array

    :param array: array to be normalized
    :type array: np.ndarray

    :rtype: np.ndarray
    """
    m = np.min(array)
    M = np.max(array)
    return (array - m)/(M - m)

def calculate_plateau_value(intens: list, indices: list) -> float:
    """
    Calculate the mean of the intensity between the given indices

    :param intens: the intensity list
    :type intens: list

    :param indices: the indices of the plateaux
    :type indices: list

    :rtype: float
    """
    return np.asarray(intens[indices[0] : indices[1]]).mean()

def calculate_std(intens, indices):
    """
    Calculate the standard deviation of the intensity between the given indices

    :param intens: the intensity list
    :type intens: list

    :param indices: the indices of the plateaux
    :type indices: list

    :rtype: float
    """
    return np.std(intens[indices[0] : indices[1]])



#====================================================================#
#                                                                    #
#                     Ideal Profiles Generation                      #
#                                                                    #
#====================================================================#


def get_interface_indices_in_ideal_profile(
    data: DepthProfiles,
    elem: str,
    Tideal: list,
    shift: float = 0
):
    idx_ideal = []
    for interface in data.locate_interfaces(elem):
        idx = 0
        while Tideal[idx] < data.time(elem)[interface] * (1 + shift):
            idx += 1
        idx_ideal.append(idx)
    return idx_ideal


def get_interface_indices_in_ideal_profile_depth(
    data: DepthProfiles,
    elem: str,
    Dideal: list,
    shift=0,
):
    
    idx_ideal = []
    for interface in data.locate_interfaces(elem):
        idx = 0
        while Dideal[idx] < data.depth(elem)[interface] * (1 + shift):
            idx += 1
        idx_ideal.append(idx)
    return idx_ideal


def generate_ideal_profile(
    data : DepthProfiles,
    n_ideal,
    elem,
    shift=0,
    interface_margin=5,
    cancellation_thresh=1e-3,
):
    # x-axis for ideal profile
    exp_time = data.time(elem)
    Tideal = np.linspace(exp_time[0], exp_time[-1], n_ideal )
    
    # get indices of interfaces in Tideal
    idx_ideal = data.get_interface_indices_in_ideal_profile(data, elem, Tideal, shift)
    
    # get profiles plateaux values
    list_indices = data.indices_plateaux(elem, interface_margin)
    plateaux = data.get_plateaux(elem)
    
    # define y-axis array
    Iideal = np.ones(n_ideal)
    if plateaux[0] > cancellation_thresh:
        Iideal[0 : idx_ideal[0]] *= plateaux[0]
    if plateaux[1] > cancellation_thresh:
        Iideal[idx_ideal[0] : idx_ideal[1]] *= plateaux[1]
    if plateaux[2] > cancellation_thresh:
        Iideal[idx_ideal[1] :] *= plateaux[elem][2]

    return Tideal, Iideal


def calculate_profile_depth(time, vitesses, idx_interfaces):
    depth = (0,)

    for i in range(1, idx_interfaces[0]):
        depth += (depth[-1] + vitesses[0] * (time[i] - time[i - 1]),)

    for inter in range(1, len(idx_interfaces)):
        for i in range(idx_interfaces[inter - 1], idx_interfaces[inter]):
            depth += (depth[-1] + vitesses[inter] * (time[i] - time[i - 1]),)

    for i in range(idx_interfaces[-1], len(time)):
        depth += (depth[-1] + vitesses[-1] * (time[i] - time[i - 1]),)
    return depth

def generate_ideal_profile_depth(
    data: DepthProfiles,
    n_ideal,
    elem,
    ref,
    interface_margin,
    shift=0,
    cancellation_thresh=1e-3,
    DEBUG=False,
):
    # x-axis for ideal profile
    Dideal = np.linspace(
        data.depth(elem)[0], data.depth(elem)[-1], n_ideal
    )
    # set interface locations in ideal x-axis
    interfaces = locate_interfaces(data, ref)
    
    # get indices of interfaces in Tideal
    idx_ideal = get_interface_indices_in_ideal_profile_depth(data,
        interfaces, Dideal, elem=elem, shift=shift, DEBUG=DEBUG
    )
    # get profiles plateaux values
    list_indices = indices_plateaux(data, interface_margin, elem)
    plateaux = get_all_plateaux(data, list_indices, elem)
    
    # define y-axis array
    Iideal = np.ones(n_ideal)
    if plateaux[elem][0] > cancellation_thresh:
        Iideal[0 : idx_ideal[0]] *= plateaux[elem][0]
    if plateaux[elem][1] > cancellation_thresh:
        Iideal[idx_ideal[0] : idx_ideal[1]] *= plateaux[elem][1]
    if plateaux[elem][2] > cancellation_thresh:
        Iideal[idx_ideal[1] :] *= plateaux[elem][2]

    return Dideal, Iideal


