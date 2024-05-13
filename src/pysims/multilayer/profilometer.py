import numpy as np
from scipy.signal import find_peaks

#create_profilo_dico_data?

#ptet la mettre dans datamodel
def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    return np.convolve(y, box, mode='same')

def locate_profilo_interfaces(data: Profilometer):

    y = data.glouglou
    y_smoothed = smooth(smooth(y, 5), 5)
    gradient = list(np.gradient(y))
    interfaces = find_peaks(np.abs(gradient), prominence = 0.01)
    return interfaces

def process_crater(path2profilo, crater, thick_Au=50, max_tangente_offset=350):
    # process depth and surface roughness from a list of profilometer profiles
    # input : list of profilometer files
    # output : crater information stored in a crater dictionary
    crater_dict = {}
    mean_crater = []
    sigm_crater = []
    sigm_surface = []
    skipleft = 1000
    for i in range(len(crater)):
        file = path2profilo + crater[i]
        data = create_profilo_dico_data(file)

        c = np.ones(200)
        yc = scipy.signal.convolve(data["Height [nm]"], c, mode="same") / np.sum(c)
        yp = list(np.gradient(yc[skipleft:5000]))

        yp_max = yp.index(np.array(yp).max())
        yp_min = yp.index(np.array(yp).min())

        X = data["X position [µm]"][
            yp_min
            + skipleft
            + max_tangente_offset : yp_max
            + skipleft
            - max_tangente_offset
        ]
        Z = data["Height [nm]"][
            yp_min
            + skipleft
            + max_tangente_offset : yp_max
            + skipleft
            - max_tangente_offset
        ]
        Z_surface = data["Height [nm]"][yp_max + skipleft :]
        mean_crater.append(np.asarray(Z).mean())

        crater_dict["crater_depth_" + str(i)] = np.asarray(Z).mean()
        crater_dict["crater_roughness_" + str(i)] = np.std(Z)
        crater_dict["surface_roughness_" + str(i)] = np.std(Z_surface)

        mean_crater.append(crater_dict["crater_depth_" + str(i)])
        sigm_crater.append(crater_dict["crater_roughness_" + str(i)])
        sigm_surface.append(crater_dict["surface_roughness_" + str(i)])

    crater_dict["Crater depth [nm]"] = -np.asarray(mean_crater).mean() - thick_Au
    crater_dict["Crater roughness profilo [nm]"] = np.asarray(sigm_crater).mean()
    crater_dict["Surface roughness profilo [nm]"] = np.asarray(sigm_surface).mean()

    return crater_dict