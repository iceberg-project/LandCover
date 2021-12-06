import rasterio
import numpy
from universal_funct import endmember_finder
from universal_funct import thresholder
from universal_funct import band_extractor
from universal_funct import rms_finder
from universal_funct import np_batch_writer
import spectra

def unmix1(input_image):
    """
    The unmixing done in the first stage of the workflow

    Parameters:
    input_image - the full path of the image

    Return:
    Returns an array indicating where there is no data in the image and
    a tuple containing the image's dimensions. Returns the atmospherically
    corrected image and the an array indicating the presence/absence of
    snow, ice, or shadowed regions.
    """

    # Extracts the data from the image
    (band_data, image_dim, meta) = band_extractor(input_image)

    # Gets the no data part of the image
    border_arr = border_finder(band_data, image_dim)

    # First unmixing
    (norm_const, init_abun) = endmember_finder(spectra.band_data,
                                               spectra.blueice_spectrum,
                                               spectra.snow_spectrum,
                                               spectra.rock_unmix_1,
                                               spectra.rock_unmix_2,
                                               spectra.zero_member,
                                               spectra.zero_member)

    # {ABUNDANCES ORDER}:
    # atm_spectrum, blueice_spectrum, snow_spectrum,
    # rock_unmix_1, rock_unmix_2
    # Creates the presence/absence arrays using the
    # abundances 
    pa_arr_1 = thresholder(init_abun,
                           (0.07, 0.10, 0.20, -1, -1, 0, 0))

    # Extracts the presence/absence arrays
    atm_binary = pa_arr_1[0]
    blueice_binary = pa_arr_1[1]
    snow_binary = pa_arr_1[2]
    #rock_1_binary = pa_arr_1[3]
    #rock_2_binary = pa_arr_1[4]
    band_5 = pa_arr_1[3]
    band_6 = pa_arr_1[4]

    # Creates a combined snow+ice presence/absence array
    snowice_binary = blueice_binary + snow_binary
    snowice_binary = np.where(snowice_binary > 1, 1,
                              snowice_binary)

    # Not snow or ice = geology. Multiplying that by atm_binary
    # gives the intersection of shadows and geology
    shadrock_binary = np.where(snowice_binary == 1, 0, 1) *\
                      atm_binary

    # Gets the shadowed ice binary by multiplying the
    # snowice and atmosphere binaries together
    shadice_binary = snowice_binary * atm_binary
    
    # Finds the presence/absence of liquid water using albedo
    # and the snow/ice binary. The albedo here is defined as
    # the average value of each pixel over all bands
    # (b1+b2+b3+...+b8)/8 for each pixel
    band_data_min = np.argmin(band_data, axis=1)
    min_binary = np.where(band_data_min == 7,
                          1, 0)
    albedo_arr = np.sum(band_data, axis=1)/8
    albedo_mean = np.mean(albedo_arr)

    # !!!!!
    # PLEASE CHANGE THE CONSTANT BEFORE albedo_mean TO CHANGE
    # THE THRESHOLD
    # !!!!!
    dark_binary = np.where(albedo_arr < 0.20*albedo_mean, 1, 0)

    # Gets the RMS of each pixel from this initial
    # unmixing
    init_rms = rms_finder(init_abun, norm_const, band_data,
                          atm_spectrum, blueice_spectrum,
                          snow_spectrum, rock_unmix_1,
                          rock_unmix_2, zero_member,
                          zero_member)

    # !!!!!
    # PLEASE CHANGE THE NUMBER AFTER THE > SIGN TO CHANGE
    # THE THRESHOLD
    # !!!!!
    unknown_binary = np.where(init_rms > 0.4, 1, 0)
    
    # Combines the presence/absence binary arrays. Makes sure
    # it stays in a binary format so that the array can be used
    # to extract the not snow/ice/shadowed regions from the
    # image
    pa_binary = atm_binary + blueice_binary + snow_binary
    pa_binary = np.where(pa_binary > 1, 1, pa_binary)

    # Calculates the atmospheric contribution using the abundances
    # and the given atmosphere spectrum
    atm_abun = init_abun[:,0]
    atm_abun = np.multiply(atm_abun, norm_const)
    atm_contr = np.multiply(atm_abun[:, np.newaxis].astype(np.float32),
                            atm_spectrum.astype(np.float32))

    # Removes the atmospheric contribution from the data
    no_atm_data = band_data.astype(np.float32) - \
                  atm_contr.astype(np.float32)

    name_list = ['border_arr.txt', 'image_dim.txt', 'no_atm_data.txt',
                 'pa_binary.txt', 'shadrock_binary.txt', 'shadice_binary.txt',
                 'snowice_binary.txt']
    
    # Writes the relevant information to text files to be transferred over to
    # other tasks
    np_batch_writer(name_list, border_arr, image_dim, no_atm_data,
                    pa_binary, shadrock_binary,
                    shadice_binary, snowice_binary)

    return (border_arr, image_dim, no_atm_data, pa_binary, shadrock_binary,
            shadice_binary, snowice_binary)
