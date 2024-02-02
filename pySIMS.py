import numpy as np
import ast
import matplotlib.pyplot as plt
import scipy.signal
import csv


colors = {
        'H' : 'gainsboro',
        '1H' : 'gainsboro',
        '1H133Cs2' : 'gainsboro',
        '16O1H133Cs2' : 'gainsboro',
        'O' : 'black',
        '12C': 'olive',
        '16O' : 'red',
        '18O' : 'red',
        '16O133Cs2' : 'red',
        '40Ca' : 'wheat',	
        '40Ca16O' : 'wheat',	
        '40Ca133Cs' : 'wheat',
        'Ti' : 'green',
        '48Ti' : 'green',
        '46Ti' : 'green',
        'Ni' : 'dimgray',
        '58Ni' : 'dimgray',
        '58Ni133Cs' : 'dimgray',
        '60Ni' : 'dimgray',
        'Sr' : 'crimson',
        '86Sr' : 'crimson',
        '88Sr' : 'crimson',
        'Cs' : 'springgreen',
        '133Cs' : 'springgreen',
        '133Cs2' : 'springgreen',
        'Ba' : 'mediumblue',
        '134Ba' : 'mediumblue',
        '138Ba' : 'mediumblue',
        'La' : 'orange',
        '139La' : 'orange',
        '48Ti16O' : 'green',
        '88Sr16O' : 'crimson',
        '142Nd' : 'mediumslateblue',
        '142Nd16O' : 'mediumslateblue',
        '142Nd133Cs' : 'mediumslateblue'
        }

gaussian_fit_color = 'C0'
w_fit_color = 'C2'

class CRATER ():
    def __init__(self, path, cratername):
        self.name = cratername
        self.path = path
        self.properties = {}
    
    def load_profiles (self, profiles):
        self.profiles = profiles
        self.refs = list (profiles.keys ())
        return None

    def load_property (self, property_name, property_value):
        self.properties [property_name] = property_value
        return None

    
    def load_dSRSC_values (self, areas=(150e-6**2,100e-6**2), margin = 0):
        dSRSC_values = {}
        dSRSC_values ['areas'] = areas
        for ref in self.profiles.keys () :
            ref_int_mass, elem = read_isotope_reference (ref)        
            intens = np.array (self.profiles[ref]['I[cnt/s]'])
            # get profiles plateaux values
            margin = 0
            grad = np.gradient (intens)
            step_idx = list (grad).index (max (grad))
            mean1 = intens [:step_idx - margin].mean ()
            mean2 = intens [step_idx + margin:].mean ()
            dSRSC_values [ref] = (mean1, mean2)
        # declare CRATER object and store data in it
        self.load_property ('dSRSC values', dSRSC_values)
        return None
    
    def calculate_dSRSC_output (self, ref):
        A1, A2 = self.properties ['dSRSC values']['areas']
        mean1, mean2 = self.properties ['dSRSC values'][ref]
        K = (mean2 - mean1) * A1 * A2 / (A1 - A2)
        atmos = mean1 - K / A1
        return K, atmos
            
    
def read_ms_file (file, sample) :
    filin = open(file,"r", encoding ='ISO-8859-9')
    lignes = filin.read ().split ('\n')
    return lignes
  
###############################################################################

def get_ms_datafile_index (lignes, sample)     :
    
    titres = ["*** DATA FILES ***",
              "*** DATA START ***",
              "*** DATA END ***",
              "*** ANALYSIS POSITION ***",
              "*** ANALYSIS RECIPE ***",
              "*** ACQUISITION PARAMETERS ***",
              "*** MEASUREMENT CONDITIONS, "+sample+".ms ***",
              "*** MAIN ANALYTICAL PARAMETERS (MAP) ***",
              "*** OPTIONAL INSTRUMENTAL PARAMETERS (OIP) ***",
              "*** ION DETECTOR PARAMETERS ***",
              "*** OTHERS ***"]
    index = []
    compteur = -1
    
    for titre in titres:
        for ligne in lignes:
            compteur += 1  
            if titre in ligne:
                index.append(compteur)
                compteur = 0
                break
    return index

###############################################################################

def get_dp_datafile_index (lignes, sample)     :
    
    titres = ["*** DATA FILES ***",
              "*** DATA START ***",
              "*** DATA END ***",
              "*** ANALYSIS POSITION ***",
              "*** ANALYSIS RECIPE ***",
              "*** ACQUISITION PARAMETERS ***",
              "*** MEASUREMENT CONDITIONS, "+sample+".dp ***",
              "*** MAIN ANALYTICAL PARAMETERS (MAP) ***",
              "*** OPTIONAL INSTRUMENTAL PARAMETERS (OIP) ***",
              "*** ION DETECTOR PARAMETERS ***",
              "*** OTHERS ***",
              "*** CALIBRATION PARAMETERS ***",]
    index = []
    compteur = -1
    
    for titre in titres:
        for ligne in lignes:
            compteur += 1  
            if titre in ligne:
                index.append(compteur)
                compteur = 0
                break
#    for titre in titres:
#        compteur = 0
#        for ligne in lignes:
#            if titre in ligne:
#                index.append (compteur)
#            compteur += 1  
    return index


###############################################################################
    
def get_nrj_datafile_index (lignes, sample)     :
    
    titres = ["*** DATA FILES ***",
              "*** DATA START ***",
              "*** DATA END ***",
              "*** ANALYSIS POSITION ***",
              "*** ANALYSIS RECIPE ***",
              "*** ACQUISITION PARAMETERS ***",
              "*** MEASUREMENT CONDITIONS, "+sample+".nrj ***",
              "*** MAIN ANALYTICAL PARAMETERS (MAP) ***",
              "*** OPTIONAL INSTRUMENTAL PARAMETERS (OIP) ***",
              "*** ION DETECTOR PARAMETERS ***",
              "*** OTHERS ***"]
    index = []
    compteur = -1
    
    for titre in titres:
        for ligne in lignes:
            compteur += 1  
            if titre in ligne:
                index.append(compteur)
                compteur = 0
                break
    return index

def get_ms_datafile_metadata (lignes, index) :

    metadata = dict()
    
    #d ata_file
    for ligne in lignes[index[0]+2:index[0]+9]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
 
    ###############################################################################
    # analysis_position
    
    for ligne in lignes[index[3]+4:index[3]+7]:
        position = ligne.split(';')
        key = "stage_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data

    for ligne in lignes[index[3]+8:index[3]+10]:
        position = ligne.split(';')
        key = "window_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data
    
    for ligne in lignes[index[3]+11:index[3]+13]:
        position = ligne.split(';')
        key = "sample_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data
         
    ###############################################################################
    # analysis_recipe 
    
    for ligne in lignes[index[4]+1:index[5]-2]:
            position = ligne.split(';')
            key = position[0]
            data = position[1]
            metadata [key] = data
    
    ###############################################################################
    # acquisition_parameters 
    
    for ligne in lignes[index[5]+1:index[6]-3]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''
    
  ###############################################################################
    # measurement_conditions
    meascons = {}
    colnames = lignes [index[6]+1].split (';')
    for i in range (len (colnames)) :
        meascons [colnames [i]] = []       
    for ligne in lignes [index[6]+2:index[7]-2]:
        ligne = ligne.split(';')
        for i in range (len (colnames)) :
            meascons [colnames [i]].append (ligne [i].strip ('\n'))
    metadata ['measurement conditions'] = meascons
    
    ###############################################################################
    # main analytical parameters (MAP) 
    
    for ligne in lignes[index[7]+1:index[8]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''
    
    ###############################################################################
    # optional instrumental parameters (IOP) 
    
    for ligne in lignes[index[8]+1:index[9]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''

    ###############################################################################
    # ion detector parameters
    
    for ligne in lignes[index[9]+1:index[10]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''      
            
    ###############################################################################
    # others
    
    for ligne in lignes[index[10]+1:]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''  
    
    return metadata

###############################################################################

def get_dp_datafile_metadata (lignes, index) :

    metadata = dict()
    
    #d ata_file
    for ligne in lignes[index[0]+2:index[0]+9]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
 
    ###############################################################################
    # analysis_position
    
    for ligne in lignes[index[3]+4:index[3]+7]:
        position = ligne.split(';')
        key = "stage_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data

    for ligne in lignes[index[3]+8:index[3]+10]:
        position = ligne.split(';')
        key = "window_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data
    
    for ligne in lignes[index[3]+11:index[3]+13]:
        position = ligne.split(';')
        key = "sample_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data
         
    ###############################################################################
    # analysis_recipe 
    
    for ligne in lignes[index[4]+1:index[5]-2]:
            position = ligne.split(';')
            key = position[0]
            data = position[1]
            metadata [key] = data
    
    ###############################################################################
    # acquisition_parameters 
    
    for ligne in lignes[index[5]+1:index[6]-3]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''
    
  ###############################################################################
    # measurement_conditions
    meascons = {}
    colnames = lignes [index[6]+1].split (';')
    for i in range (len (colnames)) :
        meascons [colnames [i]] = []       
    for ligne in lignes [index[6]+2:index[7]-2]:
        ligne = ligne.split(';')
        for i in range (len (colnames)) :
            meascons [colnames [i]].append (ligne [i].strip ('\n'))
    metadata ['measurement conditions'] = meascons
    
    ###############################################################################
    # main analytical parameters (MAP) 
    
    for ligne in lignes[index[7]+1:index[8]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''
    
    ###############################################################################
    # optional instrumental parameters (IOP) 
    
    for ligne in lignes[index[8]+1:index[9]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''

    ###############################################################################
    # ion detector parameters
    
    for ligne in lignes[index[9]+1:index[10]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''      
            
    ###############################################################################
    # calibration parameters
    
    for ligne in lignes[index[11]+1:]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''  
    
    return metadata

###############################################################################

def get_nrj_datafile_metadata (lignes, index) :

    metadata = dict()
    
    #d ata_file
    for ligne in lignes[index[0]+2:index[0]+9]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
 
    ###############################################################################
    # analysis_position
    
    for ligne in lignes[index[3]+4:index[3]+7]:
        position = ligne.split(';')
        key = "stage_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data

    for ligne in lignes[index[3]+8:index[3]+10]:
        position = ligne.split(';')
        key = "window_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data
    
    for ligne in lignes[index[3]+11:index[3]+13]:
        position = ligne.split(';')
        key = "sample_coordinates_"+position[0]
        data = position[1]
        metadata [key] = data
         
    ###############################################################################
    # analysis_recipe 
    
    for ligne in lignes[index[4]+1:index[5]-2]:
            position = ligne.split(';')
            key = position[0]
            data = position[1]
            metadata [key] = data
    
    ###############################################################################
    # acquisition_parameters 
    
    for ligne in lignes[index[5]+1:index[6]-3]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''
    
  ###############################################################################
    # measurement_conditions
    meascons = {}
    colnames = lignes [index[6]+1].split (';')
    for i in range (len (colnames)) :
        meascons [colnames [i]] = []       
    for ligne in lignes [index[6]+2:index[7]-2]:
        ligne = ligne.split(';')
        for i in range (len (colnames)) :
            meascons [colnames [i]].append (ligne [i].strip ('\n'))
    metadata ['measurement conditions'] = meascons
    
    ###############################################################################
    # main analytical parameters (MAP) 
    
    for ligne in lignes[index[7]+1:index[8]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''
    
    ###############################################################################
    # optional instrumental parameters (IOP) 
    
    for ligne in lignes[index[8]+1:index[9]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''

    ###############################################################################
    # ion detector parameters
    
    for ligne in lignes[index[9]+1:index[10]-2]:
        ligne = ligne.split (';')
        if len (ligne) > 1 :
            metadata [ligne [0]] = ligne [1]
        else :
            metadata [ligne [0]] = ''      
            


###############################################################################

def extract_ms_data (lignes, index, new_version = False) :
    # traite la rubrique *** DATA *** des fichiers Mass Spectrum
    skip_start = 4 # nb de lignes séparant la balise DATA START de la 1ere donnée
    skip_end = 2 # nb de lignes séparant la dernière donnée de DATA END
    
    if new_version:
        masse = []
        intensite = []
        items = []
        for ligne in lignes[index[1] + skip_start:index[2] - skip_end]:
            item = ligne.split(';')
            items.append(item)
        for i in range(int(len(items[0])/2)):
            for item in items:
                masse.append(float(item[2*i]))
                intensite.append(float(item[2*i+1]))
    else:
        masse1 = []
        intensite1 = []
        masse2 = []
        intensite2 = []
        for ligne in lignes[index[1] + skip_start:index[2] - skip_end]:
                a = ligne.split(';')
                for i in a:
                    masse1.append(float(a[0]))
                    intensite1.append(float(a[1]))
                    masse2.append(float(a[2]))
                    intensite2.append(float(a[3]))
        masse = masse1+masse2
        intensite = intensite1+intensite2
    return masse, intensite

###############################################################################

def extract_dp_data (lignes, index) :
    # traite la rubrique *** DATA *** des fichiers Mass Spectrum
    skiplines_to_data = 4
    NB_columns = len (lignes [index [1] + skiplines_to_data].split (';'))
    data = []
    for i in range (NB_columns) :
        data.append ([])
    for ligne in lignes[index [1] + skiplines_to_data - 2 :index [1] + skiplines_to_data]:
            a = ligne.split(';')
            for i in range (NB_columns):
                data [i].append (a [i])
    for ligne in lignes[index [1] + skiplines_to_data:index [2] - 2]:
            a = ligne.split(';')
            for i in range (NB_columns):
                if a [i] != '':
                    data [i].append (float (a [i].replace ('\n', '')))
                else:
                    data [i].append (a [i])

    return data

###############################################################################

def extract_nrj_data (lignes, index) :
    # traite la rubrique *** DATA *** des fichiers Mass Spectrum
    skiplines_to_data = 4
    NB_columns = len (lignes [index [1] + skiplines_to_data].split (';'))
    datae = []
    for i in range (NB_columns) :
        datae.append ([])
    for ligne in lignes[index [1] + skiplines_to_data - 2 :index [1] + skiplines_to_data]:
            a = ligne.split(';')
            for i in range (NB_columns):
                datae [i].append (a [i])
    for ligne in lignes[index [1] + skiplines_to_data:index [2] - 2]:
            a = ligne.split(';')
            for i in range (NB_columns):
                if a [i] != '':
                    datae [i].append (float (a [i].replace ('\n', '')))
               # else:
                #    datae [i].append (a [i])

    return datae

###############################################################################
    
def extract_ms_file (file, sample, WRITE = False, new_version = False) :
    # lit un fichier de spectres de masses
    # retourne un dictionnaire contenant les données et les métadonnées 
    lignes = read_ms_file (file, sample)
    index = get_ms_datafile_index (lignes, sample)    
    metadata = get_ms_datafile_metadata (lignes, index)  
    masse, intensite = extract_ms_data (lignes, index, new_version)

    return masse, intensite, metadata

###############################################################################
    
def extract_dp_file (file, sample, WRITE = False) :
    # lit un fichier de spectres de masses
    # retourne un dictionnaire contenant les données et les métadonnées 
    lignes = read_ms_file (file, sample)
    index = get_dp_datafile_index (lignes, sample)    
    metadata = get_dp_datafile_metadata (lignes, index)  
    data = extract_dp_data (lignes, index)
    NB_columns = len (data)
    profiles = dict ()
    for i in range (int (NB_columns / 3)) :
        c_dict = {}
        key = data [i*3][0]
        c_dict [data [i*3][1]] = data [i*3][2:]
        c_dict [data [i*3+1][1]] = data [i*3+1][2:]
        c_dict [data [i*3+2][1]] = data [i*3+2][2:]
        profiles [key] = c_dict
    data_dict = {}
    data_dict ['profiles'] = profiles
    data_dict ['metadata'] = metadata
    if WRITE :
        path, filename, samplename = get_path_filename_samplename (file)
        dictfile = open (path+sample+'_dict.txt', 'w')
        dictfile.write (str (data_dict))
        dictfile.close ()
    return profiles, metadata
    
###############################################################################

def extract_nrj_file (file, sample, WRITE = False) :
    # lit un fichier de spectres de masses
    # retourne un dictionnaire contenant les données et les métadonnées 
    lignes = read_ms_file (file, sample)
    index = get_nrj_datafile_index (lignes, sample)    
    metadata = get_nrj_datafile_metadata (lignes, index)  
    datae = extract_nrj_data (lignes, index)
    NB_columns = len (datae)
    energies = dict ()
    for i in range (int (NB_columns / 2)) :
        c_dict = {}
        key = datae [i*2][0]
        c_dict [datae [i*2][1]] = datae [i*2][2:]
        c_dict [datae [i*2+1][1]] = datae [i*2+1][2:]
        energies [key] = c_dict
    data_dict = {}
    data_dict ['energies'] = energies
    data_dict ['metadata'] = metadata
    if WRITE :
        path, filename, samplename = get_path_filename_samplename (file)
        dictfile = open (path+sample+'_dict.txt', 'w')
        dictfile.write (str (data_dict))
        dictfile.close ()
    return energies, metadata

###############################################################################

def get_path_filename_samplename (file) :
    filename = file.split ('/')[-1]
    samplename = file.split ('.')[0].split ('/')[-1]
    path = file.split ('.')[0] [:-len (samplename)]
    return path, filename, samplename

###############################################################################

def calculate_plateau_value (intens, indices) :
    return np.asarray (intens [indices[0]: indices [1]]).mean ()

###############################################################################

def calculate_ecart_type(intens, indices) :
    return  (np.std(intens [indices[0]: indices [1]]))

###############################################################################

def get_all_plateaux (profiles, plateau_indices) :
    plateaux = {}
    for elem in profiles :
        plateaux [elem] = []
        for indices in plateau_indices :
            plateaux [elem].append (calculate_plateau_value (profiles [elem]['I[cnt/s]'], indices))
    return plateaux


###############################################################################

def get_all_ecart_type (profiles, plateau_indices) :
    ecart_type = {}
    for elem in profiles :
        ecart_type[elem] = []
        for indices in plateau_indices :
            ecart_type[elem].append(calculate_ecart_type(profiles [elem]['I[cnt/s]'], indices))
    return ecart_type

###############################################################################

def append_to_data_file (file, dico):    
    d = open (file, 'r')
    temporary_data = ast.literal_eval (d.read ())
    datakeys = list (temporary_data.keys())
    d.close ()
    message = 'No data was added to the datafile'
    for key in dico :
        if key not in datakeys :
            d = open (file, 'w')
            temporary_data [key] = dico [key]
            d.write (str (temporary_data))
            message = key + ' was appended to ' + file
            datakeys = list (temporary_data.keys())
            d.close ()
    return message

###############################################################################
    

def locate_interfaces(profiles, ref = '139La') :
    # return the indices of the interface for sample GZ46
    y = profiles[ref]['I[cnt/s]']
    yp = list (np.gradient(y))
    
    return yp.index (np.array(yp).max()), yp.index (np.array (yp).min())

	
def indices_plateaux(profiles, interface_margin, ref = '139La') :
    inter1,inter2 = locate_interfaces (profiles, ref)
    list_indices = [(interface_margin, inter1 - interface_margin),
                    (inter1 + interface_margin, inter2 - interface_margin) ,
                    (inter2 + interface_margin, len (profiles [ref]['I[cnt/s]']) - interface_margin)]                      
    return list_indices


def plot_plateau_ranges (profiles, list_indices, ax, DEBUG = False):
    for indices in list_indices :
        if DEBUG : print('indices :', indices)
        ax.axvline(int(profiles['139La']['Time[s]'][indices[0]]), ls =':', lw = 1, color = 'black')
        ax.axvline(int(profiles['139La']['Time[s]'][indices[1]]), ls =':', lw = 1, color = 'black')
    return None


def get_interface_indices_in_ideal_profile (interfaces, profiles, Tideal, shift = 0, elem = '139La'):
    idx_ideal = []
    for interface in interfaces:    
        idx = 0
        while Tideal [idx] < profiles [elem]['Time[s]'][interface] * (1 + shift):
            idx += 1
        idx_ideal.append (idx)
    return idx_ideal


def get_interface_indices_in_ideal_profile_depth (interfaces, profiles, Dideal, shift = 0, elem = '139La', DEBUG = False):
    idx_ideal = []
    if DEBUG:
        print (Dideal [0])
        print (profiles [elem]['Depth[nm]'][26] * (1 + shift))
    for interface in interfaces:    
        idx = 0
        while Dideal [idx] < profiles [elem]['Depth[nm]'][interface] * (1 + shift):
            idx += 1
        idx_ideal.append (idx)
    return idx_ideal


def generate_ideal_profile (profiles, n_ideal, elem, shift = 0, ref ='139La',
                            interface_margin = 5, cancellation_thresh = 1e-3):
    # x-axis for ideal profile
    Tideal = np.linspace (profiles [ref]['Time[s]'][0],
                          profiles [ref]['Time[s]'][-1],
                          n_ideal)
    # set interface locations in ideal x-axis
    interfaces = locate_interfaces (profiles, ref)
    # get indices of interfaces in Tideal
    idx_ideal = get_interface_indices_in_ideal_profile (interfaces, profiles, Tideal, shift) 
    # get profiles plateaux values
    interface_margin = 5
    list_indices = indices_plateaux (profiles,interface_margin)    
    plateaux = get_all_plateaux (profiles, list_indices)
    # define y-axis array
    Iideal = np.ones (n_ideal)
    if plateaux [elem] [0] > cancellation_thresh:
        Iideal [0:idx_ideal [0]] *= plateaux [elem][0]
    if plateaux [elem][1]> cancellation_thresh:
        Iideal [idx_ideal [0]:idx_ideal [1]] *= plateaux [elem][1]
    if plateaux [elem][2] > cancellation_thresh:
        Iideal [idx_ideal [1]:] *= plateaux [elem][2]
   
    return Tideal, Iideal
        
        

def generate_ideal_profile_depth (profiles, n_ideal, elem, shift = 0, ref ='139La',
                            interface_margin = 5, cancellation_thresh = 1e-3, DEBUG = False):
    # x-axis for ideal profile
    Dideal = np.linspace (profiles [elem]['Depth[nm]'][0],
                          profiles [elem]['Depth[nm]'][-1],
                          n_ideal)
    # set interface locations in ideal x-axis
    interfaces = locate_interfaces (profiles, ref)
    # get indices of interfaces in Tideal
    idx_ideal = get_interface_indices_in_ideal_profile_depth(interfaces,
                                                             profiles,
                                                             Dideal,
                                                             elem = elem,
                                                             shift = shift,
                                                             DEBUG = DEBUG) 
    # get profiles plateaux values
    interface_margin = 5
    list_indices = indices_plateaux (profiles,interface_margin)    
    plateaux = get_all_plateaux (profiles, list_indices)
    # define y-axis array
    Iideal = np.ones (n_ideal)
    if plateaux [elem] [0] > cancellation_thresh:
        Iideal [0:idx_ideal [0]] *= plateaux [elem][0]
    if plateaux [elem][1]> cancellation_thresh:
        Iideal [idx_ideal [0]:idx_ideal [1]] *= plateaux [elem][1]
    if plateaux [elem][2] > cancellation_thresh:
        Iideal [idx_ideal [1]:] *= plateaux [elem][2]
   
    return Dideal, Iideal


def calculate_profile_depth (time, vitesses, idx_interfaces):
    depth = (0,)

    for i in range (1, idx_interfaces [0]):
        depth += depth [-1] + vitesses [0] * (time [i] - time [i-1]),
        
    for inter in range (1, len (idx_interfaces)):
        for i in range (idx_interfaces [inter-1], idx_interfaces [inter]):
            depth += depth [-1] + vitesses [inter] * (time [i] - time [i-1]),
    
    for i in range (idx_interfaces [-1], len (time)):
        depth += depth [-1] + vitesses [-1] * (time [i] - time [i-1]),
    
    return depth


###############################################################################

def MassSpectrum_local_max (m, intens, m_ref, n = 32, DEBUG = False):
    # returns the intensity of the mass spectrum around m_ref (+/- 0.5 at. unit)
    idx = int (m.index (m_ref) - n/2)
    if DEBUG: 
        print('Integer mass ' + str(m_ref) + ' located at index ' + str(idx))
    local_spectrum = intens [idx : idx + n]
    localmax_i = max (local_spectrum)
    if DEBUG:
        print('exp. intensity local max. intensity ' + str(localmax_i))
    localmax_m = m [local_spectrum.index (localmax_i) + idx]
    return localmax_m, localmax_i
    
   
###############################################################################
    
def deviation_to_natural_abundance (m, intens, ref, table_iso, n = 32, PRINT = False) :
    names_iso, masses_iso, abondances_iso = table_iso
    int_mass, elem = read_isotope_reference (ref)
    relevance_threshold = 100
    
    # calcul les rapports isotopiques naturels
    minors = [] # other isotopes than reference
    for iso in names_iso :
        if elem in iso :
            if iso != ref:
                minors.append (iso)
    if PRINT : print (minors)

    # reference abundance
    idx = names_iso.index (ref)
    ref_intens_theo = abondances_iso [idx]
    ref_int_mass_expe, ref_intens_expe = MassSpectrum_local_max (m, intens, int_mass, n = n, DEBUG = PRINT)

    var_ionic_interference = 0
    if PRINT : print (ref, ref_intens_theo, ref_intens_expe)
    if ref_intens_expe > relevance_threshold :
        for minor in minors :
            idx = names_iso.index (minor)
            minor_int_mass_theo = masses_iso [idx]
            minor_intens_theo = abondances_iso [idx]
            minor_int_mass_expe, minor_intens_expe = MassSpectrum_local_max (m, intens, np.round (minor_int_mass_theo), n = n, DEBUG = PRINT)
            r_theo = minor_intens_theo / ref_intens_theo
            r_expe = minor_intens_expe / ref_intens_expe
            if PRINT : print (minor, minor_intens_theo, minor_intens_expe)
            if PRINT : print (f' : r_theo = {r_theo:.2e}'
                             + f' : r_expe = {r_expe:.2e}')
            var_ionic_interference += ((r_expe - r_theo) / r_theo) ** 2
            if PRINT : print ((r_expe - r_theo) / r_theo)
    
        sigma_ionic_interference = np.sqrt (var_ionic_interference / len (minors) )
    else :
        sigma_ionic_interference = -1
    if PRINT: print (f'std dev = {sigma_ionic_interference * 100:.1f} %')
    return sigma_ionic_interference


###############################################################################

def read_isotope_reference (ref):
    elem = ''
    int_mass_str = ''
    inmass = True
    for c in ref:
        if not c.isdigit () and not inmass : 
            elem += c
        if not c.isdigit () and inmass:
            inmass = not inmass
            elem += c
        if c.isdigit () and inmass : 
            int_mass_str += c
        if c.isdigit () and not inmass : 
            elem += c
    int_mass = int (int_mass_str)
    return int_mass, elem

def format_isotope_symbol (ref):
    ref_int_mass, elem = read_isotope_reference (ref)
    if elem [-1].isdigit ():
        ion = elem[:-1] + '$_' + elem[-1] + '$'
    else:
        ion = elem
    return r'${}^{' + f'{ref_int_mass:d}' + '}$'+ ion

def format_ionic_complex_symbol (ref):
    start_idx_ = (0,)
    inmass = True
    idx = 0
    # if 'Cs2' in ref and len (ref) != 6:
    #     formatted_complex_symbol = r'${}^{133}$Cs$_2$' + format_isotope_symbol (ref.split(' ')[1])
    for c in ref:
        if not c.isdigit() and inmass:
            inmass = not inmass
        if c.isdigit() and not inmass:
            start_idx_ += (idx,)
            inmass = not inmass
        idx += 1
    if 'Cs2' in ref:
        start_idx = start_idx_[:-1]
    else:
        start_idx = start_idx_
    formatted_complex_symbol = ''
    for i in range(len(start_idx)-1):
        formatted_complex_symbol += format_isotope_symbol (ref[start_idx[i]:start_idx[i+1]])
    formatted_complex_symbol += format_isotope_symbol (ref[start_idx[-1]:])
    return formatted_complex_symbol 

###############################################################################    
#           PROFILOMETER DATA ANALYSIS (2022-06-14)
###############################################################################    

def read_profilo_file(file, encoding='ISO-8859-1'):  
    f = open(file,  encoding = encoding)
    myreader = csv.reader(f)
    lignes = []

    for extract in myreader :
        lignes.append(extract)
    return lignes    

def get_profilo_index(lignes):
    index = []
    compteur = -1
    titres = [['µm', 'nm', ''],['AnalyticalResults']]

    for titre in titres:
        for ligne in lignes:
            compteur += 1
            if titre == ligne :
                index.append(compteur)
    return index

def create_profilo_dico_data(file):
    
    lignes = read_profilo_file(file)
    index = get_profilo_index(lignes)
    data = {}
    x = []
    y = []
 
    for ligne in lignes[index[0]+1:-2]:
        x.append(float(ligne[0]))
        y.append(float(ligne[1]))

    data['X position [' + lignes[index[0]][0] + ']'] = x
    data['Height [' + lignes[index[0]][1] + ']'] = y
    
    return data

def locate_profilo_interfaces(data) :
    
    y = data['nm']
    yp = list (np.gradient(y))
    yp_max = yp.index (np.array(yp).max())
    yp_min = yp.index (np.array (yp).min())
    
    return yp_max,yp_min

def process_crater (path2profilo, crater, thick_Au = 50, max_tangente_offset = 350):    
    # process depth and surface roughness from a list of profilometer profiles
    # input : list of profilometer files
    # output : crater information stored in a crater dictionary
    crater_dict = {}
    mean_crater = []
    sigm_crater = []
    sigm_surface = []
    skipleft = 1000
    for i in range(len(crater)):
        file = path2profilo + crater [i]
        data = create_profilo_dico_data (file)
        
        c = np.ones(200)
        yc = scipy.signal.convolve(data['Height [nm]'], c, mode='same')/np.sum(c)
        yp = list (np.gradient(yc[skipleft:5000]))

        yp_max = yp.index (np.array(yp).max())
        yp_min = yp.index (np.array(yp).min())
        
        X = data['X position [µm]'][yp_min + skipleft + max_tangente_offset : yp_max + skipleft - max_tangente_offset]
        Z = data['Height [nm]'][yp_min + skipleft + max_tangente_offset : yp_max + skipleft - max_tangente_offset] 
        Z_surface = data['Height [nm]'][yp_max + skipleft:]
        mean_crater.append(np.asarray (Z).mean ())
        
        crater_dict['crater_depth_'+ str(i)] = np.asarray (Z).mean ()
        crater_dict['crater_roughness_' + str(i)] = np.std(Z)
        crater_dict['surface_roughness_' + str(i)] = np.std(Z_surface)
        
        mean_crater.append (crater_dict['crater_depth_'+ str(i)])
        sigm_crater.append (crater_dict['crater_roughness_' + str(i)])
        sigm_surface.append (crater_dict['surface_roughness_' + str(i)])
        
        
    crater_dict['Crater depth [nm]'] = -np.asarray(mean_crater).mean() - thick_Au
    crater_dict['Crater roughness profilo [nm]'] = np.asarray(sigm_crater).mean()
    crater_dict['Surface roughness profilo [nm]'] = np.asarray(sigm_surface).mean()

    return crater_dict


def get_sputtering_times (path2profiles, crater, sputtering_time_Au = 50):
    file = path2profiles + crater + ".dp_rpc_txt"
    profiles, metadata = extract_dp_file (file, crater)
    sputtimes = {}
    for elem in profiles.keys ():
        sputtimes [elem] = np.max (profiles [elem]['Time[s]']) - sputtering_time_Au
    return sputtimes


def gaussian_convolution (profile, sigma, n_filter):
    zg = np.arange (n_filter, dtype = float)
    zg -= np.max (zg) / 2
    fg = 1 / sigma / np.sqrt (2 * np.pi) * np.exp (-zg * zg / 2 / sigma / sigma)
    yc = scipy.signal.convolve(profile, fg, mode='same') / np.sum (fg)
    return zg, fg, yc


def exponential_convolution (profile, w, n_filter_w):
    zw = np.arange (n_filter_w, dtype = float)
    zw -= np.max (zw) / 2
    fw = 1 / w * np.exp (-(zw - w)/w)
    fw [:int (n_filter_w / 2) - w] = 0  
    yc_w = scipy.signal.convolve(profile , fw , mode='same') / np.sum (fw)
    return zw, fw, yc_w


def filter_normalization (profiles, elem, fit_parameters):
    n_ideal, shift, sigma_nm, w_nm = fit_parameters
    Dmax = np.max (profiles[elem]['Depth[nm]'])
    dz = Dmax / n_ideal
    sigma = int (np.round (sigma_nm / dz))
    w = int (np.round (w_nm / dz))
    return dz, sigma, w


def index_of_closest_element (array, target):
    i = 0
    while array [i] < target:
        i += 1
    return i

                
def fit_interface_crossing (profiles, elem, fit_parameters, xlim = (200, 340),
                            cancellation_thresh = 1e-3, yscale = 'linear',
                            SAVEFIG = False, Xpos = 0):
    n_ideal, shift, sigma_nm, w_nm = fit_parameters
    
    depth = profiles[elem]['Depth[nm]']
    
    # normalisation des filtres
    Dmax = np.max (profiles[elem]['Depth[nm]'])
    dz = Dmax / n_ideal
    sigma = int (np.round (sigma_nm / dz))
    w = int (np.round (w_nm / dz))

    # génération du profil idéal
    interfaces = locate_interfaces (profiles)
    Dideal, Iideal = generate_ideal_profile_depth (profiles, n_ideal, elem  = elem,
                                                   interface_margin = 5, shift = shift, cancellation_thresh = cancellation_thresh)
    ideal_interfaces = get_interface_indices_in_ideal_profile_depth (interfaces, profiles, Dideal, elem = elem, shift = shift)

    # roughness convolution
    n_filter = n_ideal / 10
    zg, fg, yc = gaussian_convolution (Iideal, sigma, n_filter)

    # atomic mixing convolution
    n_filter_w = n_filter
    zw, fw, yc_w = exponential_convolution (yc , w, n_filter_w)

    # plot figures
    fig, (ax1, ax2) = plt.subplots (figsize = (15,4), nrows = 1, ncols = 2)
    ax1.plot (profiles[elem]['Depth[nm]'], profiles[elem]['I[cnt/s]'], marker = 'o', color = 'k')
    ax1.plot (Dideal, Iideal, lw = 2, ls = 'dotted', color = 'k', alpha = 0.3)
    ax1.plot (Dideal, yc, lw = 2, ls = 'dashed', color = 'C1')
    ax1.set_yscale (yscale)
    ax1.set_xlim (xlim)
    ax1.set_xlabel('Depth[nm]')
    ax1.set_ylabel('I[cnt/s]')
    ax1.text (0.1, 0.9, elem, color = colors [elem.replace (' ', '')], 
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax1.transAxes)

    ax2.plot(zg, fg, color = 'C1')
    ax2.set_yscale (yscale)
    ax2.set_ylabel ('Numeric filter')
    ax2.set_xlabel ('z (numeric depth)')
    if SAVEFIG: plt.savefig ('MRI-fit_details_1_'+elem+f'_{int(Xpos):+05d}.png')

    fig, (ax3, ax4) = plt.subplots (figsize = (15,4), nrows = 1, ncols = 2)
    ax3.plot (profiles[elem]['Depth[nm]'], profiles[elem]['I[cnt/s]'], marker = 'o', color = 'k')
    ax3.plot (Dideal, Iideal, lw = 2, ls = 'dotted', color = 'k', alpha = 0.3)
    ax3.plot (Dideal, yc_w, lw = 2, ls = 'dashed', color = 'C2')
    ax3.set_yscale (yscale)
    ax3.set_xlim (xlim)
    ax3.set_xlabel('Depth[nm]')
    ax3.set_ylabel('I[cnt/s]')
    filter_param_str  = f'$\sigma$ = {sigma_nm:.1f} nm ({sigma:d} pxl)\n'
    filter_param_str += f'w = {w_nm:.1f} nm ({w:d} pxl)\n'
    ax3.text (0.8, 0.5, filter_param_str,
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax3.transAxes)

    ax4.plot(zw, fw, color = 'C2')
    ax4.set_yscale (yscale)
    ax4.set_ylabel ('Numeric filter')
    ax4.set_xlabel ('z (numeric depth)')

    if SAVEFIG: plt.savefig ('MRI-fit_details_2_'+elem+f'_{int(Xpos):+05d}.png')
    plt.show ()

    return yc_w

###############################################################################    


def main ():
    # data is a dictionary gathering experimental and analysis items from a single datafile
    # datafiles are stored in the ofrmat of dictionaries whose keys are:
    #   - profiles
    #   - metadata
    #   - plateaux
    #   - isotopes
    DEBUG = False
    WRITE = False # write a text file containing the data/metadata dictionary for each data file
    # plot all profiles and idealized profiles
    PLOT = True

    ext = '.dp_rpc_txt'
    path = '/home/scola/RECHERCHE/SUPERNICKEL/massifs/SIMS/DATA/'
    cratername = 'E1ECH1'
    moncrat = CRATER (path, cratername)    
    
    file = path + cratername + ext
    
    profiles, metadata = extract_dp_file (file, cratername)
    moncrat.load_profiles(profiles)    
    moncrat.load_dSRSC_values()    
    ref = '133Cs'
    print (moncrat.calculate_dSRSC_output (ref)) 
    return moncrat
        
if __name__ == '__main__':
    output = main ()
