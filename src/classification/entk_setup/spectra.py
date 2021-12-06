import os
import numpy as np

# Has functions to read in an list of in situ spectra as endmembers.
# Also has some given spectra to use as endmembers if desired

def endmember_reader():
    """
    Reads the .txt file containing the possible geologic endmembers.
    
    Parameters:
    working_dir - the directory of the endmember library text file.
                  It should be in the same location as the script
    
    Return:
    Returns two arrays. The first contains the sample ID, lithology type,
    and whether the sample was from a specimen's surface or interior. The
    second array contains the eight bands that the spectral data was
    downsampled to.
    """
    
    # Creates two lists to store the descriptions of each sample and the
    # eight bands downsampled to, respectively
    name_arr = []
    spect_arr = []

    # A temporary list to store the text from the document
    temp_arr = []

    endmember_file = os.path.join(os.getcwd,
                                  "polar_rock_repo_multispectral_WV02.txt")

    # Opens the .txt file containing the possible endmembers
    with open(endmember_file, 'r') as endmem_file:
        # and stores the text into the temporary list
        temp_arr = [line.strip().split() for line in endmem_file]

    # Closes the file
    endmem_file.close()

    # Stores the descriptions into the appropriate list (only saves the first
    # row aka the Polar Rock Repository (PRR) ID and the labelled rock type
    name_arr = temp_arr[0:2]
    
    # Lops off the extraneous information (what each descriptor is)
    for i in range(len(name_arr)):
        name_arr[i] = name_arr[i][1:]

    # Converts the list to a numpy array
    name_arr = np.array(name_arr, dtype='str')
    
    # Transposes the array to more easily access the information
    # through indexing (it is now sample x description)
    name_arr = name_arr.transpose(1, 0)

    # Stores each sample's eight bands
    spect_arr = temp_arr[3:]
    
    # Lops off the extraneous information (what each band corresponds to)
    for i in range(len(spect_arr)):
        spect_arr[i] = spect_arr[i][1:]

    # Converts the list to a numpy array. Lowers the precision
    # to attempt to make the processing faster
    spect_arr = np.array(spect_arr, dtype=np.float16)
    # Transposes the array to match the pysptools input format
    # (it is now sample x band)
    spect_arr = spect_arr.transpose(1, 0)

    # Returns the two arrays
    return (name_arr, spect_arr)

def rock_caller(name_arr, endmember_arr, rock_num, plot_bool):
    """
    Gets the spectrum of a PRR rock sample with the specified PRR number

    Parameters:
    name_arr      - an array containing the names and PRR numbers of the samples
    endmember_arr - an array containing the spectra of the samples
    rock_num      - a string of the sample's PRR code (ie PRR21153)
    plot_bool     - True for showing a plot, False if no plot desired

    Return:
    Returns a 1D array representing the spectrum of the specified sample
    """

    # Gets the PRR numbers
    name_arr = name_arr[:,0]

    # Gets the index of the specified PRR number. If the specified rock
    # had its spectrum taken multiple times, the last one is taken
    # This ensures that the sample is taken from the surface and not
    # the interior
    index = np.where(name_arr == rock_num)[0][-1]

    # Finds the rock spectrum using the found index
    rock_spectrum = endmember_arr[index]

    # Plots the rock spectrum if needed
    if plot_bool:
        # The x axis is the wavelength in nm
        plt.plot([427, 478, 546, 608, 659, 724, 831, 908],
                 rock_spectrum)
        plt.show()

    return rock_spectrum

(name_arr, spect_arr) = endmember_reader()

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||
# Placeholder endmember. Has 0 as each band value. Used
# for to-be-determined(TBD) bands in the extraction
# process
zero_member = np.array([0, 0, 0, 0, 0, 0, 0, 0])
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Given atmosphere, ice, and snow spectra for the first unmixing
#atm_spectrum = np.array([0.259389, 0.211368, 0.122011, 0.077600,
#                         0.053078, 0.034265, 0.034265, 0.000000])
#blueice_spectrum = np.array([0.318048, 0.337719, 0.306141, 0.232309,
#                             0.195406, 0.153987, 0.119120, 0.098717])
#snow_spectrum = np.array([0.574054, 0.631622, 0.664903, 0.633762,
#                          0.644898, 0.602088, 0.563149, 0.514703])

# A second batch of the above spectra. Uncomment them and comment the
# above to use
atm_spectrum = np.array([0.229667, 0.171667, 0.094333, 0.055667,
                         0.034, 0.019667, 0.001667, 0])
blueice_spectrum = np.array([0.310994, 0.328909, 0.302449, 0.234954,
                             0.197393, 0.155512, 0.122738, 0.107701])
snow_spectrum = np.array([0.7298, 0.74388, 0.758755, 0.74022,
                          0.739445, 0.71887, 0.67605, 0.615885])

# Given water spectrum
water_spectrum = [0.0806, 0.0855, 0.0945, 0.0969,
                  0.0959, 0.0889, 0.0837, 0.0812]

# Gets two arbitrary samples that seem representative of the overall
# rock spectrum
# NOTE: AT THE MOMENT THE ROCK SPECTRA ARE ZEROS ACROSS THE BOARD
#rock_unmix_1 = rock_caller(name_arr, spect_arr, "PRR21553", False)
#rock_unmix_2 = rock_caller(name_arr, spect_arr, "PRR12723", False)
#rock_unmix_1 = rock_caller(name_arr, spect_arr, "PRR12112", False)
rock_unmix_1 = zero_member
rock_unmix_2 = zero_member

# ||||||||||||||||||||||
# Some given endmembers. Uncomment these and comment the ones
# from the PRR if these are to be used in the unmixing

more_dol = np.array([0.141365, 0.162614, 0.188622, 0.203393,
                     0.210742, 0.216176, 0.182945, 0.163316])
less_dol = np.array([0.082166, 0.097734, 0.128021, 0.163402,
                     0.177911, 0.187761, 0.177382, 0.16477])
granite = np.array([0.161972, 0.184228, 0.207389, 0.218254,
                    0.218669, 0.217567, 0.216672, 0.213827])
sandstone = np.array([0.178015, 0.208722, 0.261726, 0.318685,
                      0.346399, 0.377037, 0.413383, 0.43422])
# ||||||||||||||||||||||

# More mafic (Mg rich) dolerite endmember
#more_dol = rock_caller(name_arr, spect_arr, "PRR12602", False)
# Less mafic (Mg poor) dolerite endmember
#less_dol = rock_caller(name_arr, spect_arr, "PRR11149", False)
# Granite/metamorphic endmember
#granite = rock_caller(name_arr, spect_arr, "PRR21578", False)
# Sandstone/mudstone endmember
#sandstone = rock_caller(name_arr, spect_arr, "PRR12805", False)

# Soil_B235_20181222_CAL03_PROC_AVG 
# soil_b235 = [0.11252352673352867, 0.12831983620230558, 0.1543490784718553, 0.16897626234892552,
#              0.170874278850688, 0.1700069906420524, 0.1649994942062938, 0.16126979692425344]

# Soil_bowles_3_wet_soil 
# soil_bowles_3 = [0.06927708300920764, 0.07635483306892545, 0.09176553537867067, 0.10156158251867968,
#                  0.10109479399718689, 0.10009265182886719, 0.09560329223620738, 0.09430395495317109]

# Moss_bow02_opp_20190125_sat_4 
# moss_bow02 = [0.01654872544194769, 0.02375619996889153, 0.07387816933660053, 0.08310167513755072,
#               0.05866421811129647, 0.23223763121548482, 0.3174657749556898, 0.3649145578659193]

# Black_pla03_poop_20181218_dry_19 
# black_pla03 = [0.03534084783022605, 0.03822200227238683, 0.04661914674017628, 0.053665135162879324,
#                0.05732210195192126, 0.0823476803081346, 0.19045994806598507, 0.3438802278826755]

# Black_bow_opp_20190125_sat_14 
# black_bow = [0.025038663445809153, 0.025864771217631876, 0.02752827367931875, 0.026715511910279783,
#              0.025597984758045145, 0.030995298192429698, 0.07977468944204681, 0.1605709490607983]

# Red_bow02_20181230_inun_78 
# red_bow02 = [0.04839002553176692, 0.05255026783879072, 0.073166209982959, 0.1003938610429521,
#              0.0945747959436475, 0.1147058780894044, 0.11849448283638578, 0.10318868964045738]

# Orange_bow02_opp_20181222_inun_4
# orange_bow02 = [0.08495563453249949, 0.08499935161256106, 0.13044750132673766, 0.18020468396360786,
#                 0.154625878994879, 0.3666560697430291, 0.40091977205160917, 0.375634474616427]

