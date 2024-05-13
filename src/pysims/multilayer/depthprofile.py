import numpy as np
from scipy.signal import find_peaks
from pysims.utils import *
from pysims.datamodel import Crater, processing

class DepthProfiles(Crater) :
    def intensity(self, elem) :
        return self.get_elem_attr(elem, INTENSITY)

    def time(self, elem) :
        return self.get_elem_attr(elem, TIME)

    def depth(self, elem) :
        return self.get_elem_attr(elem, DEPTH)


def calculate_plateau_value(intens, indices):
    return np.asarray(intens[indices[0] : indices[1]]).mean()


def calculate_ecart_type(intens, indices):
    return np.std(intens[indices[0] : indices[1]])


@processing
def get_all_plateaux(data: DepthProfiles):
    plateaux = {}
    for elem in data.elements :
        plateaux[elem] = []
        for indices in data.get("plateaux_indices"):
            plateaux[elem].append(
                calculate_plateau_value(data.intensity(elem), indices)
            )
    return plateaux


@processing
def get_all_ecart_type(data: DepthProfiles):
    ecart_type = {}
    for elem in data.elements :
        ecart_type[elem] = []
        for indices in data.get("plateaux_indices"):
            ecart_type[elem].append(
                calculate_ecart_type(data.intensity(elem), indices)
            )
    return ecart_type


def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    return np.convolve(y, box, mode='same')

@processing
def locate_interfaces(data: DepthProfiles, elem="139La"):
    y = data.intensity(elem)
    smoothed_y = smooth(smooth(y, 5), 5)
    gradient = np.gradient(smoothed_y)
    interfaces = find_peaks(np.abs(gradient), prominence = 0.01)
    return interfaces


@processing
def indices_plateaux(data: DepthProfiles, interface_margin, elem = "139La") :
    interfaces = locate_interfaces(data)
    list_indices =[(interfaces[i] + interface_margin, interfaces[i+1] - interface_margin) for i in range(len(interfaces))]
    list_indices.append((interfaces(len(interfaces)) + interface_margin, len(data.intensity(elem))))
    return list_indices


def plot_plateau_ranges(data: DepthProfiles, list_indices, ax, DEBUG=False, elem = "139La"):
    for indices in list_indices:
        if DEBUG:
            print("indices :", indices)
        ax.axvline(
            int(data.time(elem)[indices[0]]), ls=":", lw=1, color="black"
        )
        ax.axvline(
            int(data.time(elem)[indices[1]]), ls=":", lw=1, color="black"
        )
    return None


def get_interface_indices_in_ideal_profile(data: DepthProfiles,
    interfaces, Tideal, shift=0, elem ="139La"):
    idx_ideal = []
    for interface in interfaces:
        idx = 0
        while Tideal[idx] < data.time(elem)[interface] * (1 + shift):
            idx += 1
        idx_ideal.append(idx)
    return idx_ideal


def get_interface_indices_in_ideal_profile_depth(data: DepthProfiles,
    interfaces, Dideal, shift=0, elem="139La", DEBUG=False
):
    idx_ideal = []
    if DEBUG:
        print(Dideal[0])
        print(data.depth(elem)[26] * (1 + shift)) #
    for interface in interfaces:
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
    ref="139La",
    interface_margin=5,
    cancellation_thresh=1e-3,
):
    # x-axis for ideal profile
    Tideal = np.linspace(
        data.time(elem)[0], data.time[-1], n_ideal
    )
    # set interface locations in ideal x-axis
    interfaces = locate_interfaces(data)
    # get indices of interfaces in Tideal
    idx_ideal = get_interface_indices_in_ideal_profile(data, interfaces, Tideal, shift, elem)
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

    return Tideal, Iideal


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

