import rasterio
import numpy
from universal_funct import endmember_finder
from universal_funct import thresholder
from universal_funct import band_extractor
from universal_funct import np_batch_writer
import spectra

def umix3(no_atm_data, pa_binary):
    """
    One of the unmixings in the second stage of the workflow. Specifically
    looks for water

    Parameters:
    no_atm_data - a 2D array of atmospherically corrected image. pixel x band
    pa_binary   - a 2D array containing indicating the presence/absence
                  of snow/ice/shadows

    Return:
    Returns the presence/absence of the endmembers
    """    

    # Gets the ice/snow/water of the image
    icewater_data = np.multiply(np.float16(no_atm_data),
                                            np.int16(pa_binary[:,np.newaxis]))

    # Unmixing
    (norm_const_icewater,
     icewater_abun) = endmember_finder(icewater_data,
                                       snow_spectrum, blueice_spectrum,
                                       water_spectrum, zero_member,
                                       zero_member, zero_member,
                                       zero_member)


    # {ABUNDANCES ORDER}:
    # snow, blueice, water, zero, zero, zero, zero
    pa_arr_3 = thresholder(icewater_abun,
                           (-1, -1, -1, 0, 0, 0, 0))
    
    band_18 = pa_arr_3[1]
    band_19 = pa_arr_3[2]
    band_20 = pa_arr_3[3]
    band_21 = pa_arr_3[4]

    """
    # --------------------------------
    # Snow/ice/water writing
    snow_binary += border_arr
    blueice_binary += border_arr
    water_binary += border_arr
    band_18 += border_arr
    band_19 += border_arr
    band_20 += border_arr
    band_21 += border_arr
    dst.write_band(15, np.reshape(snow_binary,
                                  image_dim).astype(np.int16))
    dst.write_band(16, np.reshape(blueice_binary,
                                  image_dim).astype(np.int16))
    dst.write_band(17, np.reshape(water_binary,
                                  image_dim).astype(np.int16))
    dst.write_band(18, np.reshape(band_18,
                                  image_dim).astype(np.int16))
    dst.write_band(19, np.reshape(band_19,
                                  image_dim).astype(np.int16))
    dst.write_band(20, np.reshape(band_20,
                                  image_dim).astype(np.int16))
    dst.write_band(21, np.reshape(band_21,
                                  image_dim).astype(np.int16))
    # --------------------------------
    """

    name_list = ['snow_binary.txt', 'blueice_binary.txt', 'water_binary.txt',
                 'band_18.txt', 'band_19.txt', 'band_20.txt',
                 'band_21.txt', 'band_21.txt']

    # Writes the relevant information to text files to be transferred over to
    # other tasks
    np_batch_writer(name_list, snow_binary, blueice_binary, water_binary,
                    band_18, band_19, band_20, band_21, band_21)

    return (snow_binary, blueice_binary, water_binary,
            band_18, band_19, band_20, band_21, band_21)
