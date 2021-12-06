import rasterio
import numpy
from universal_funct import endmember_finder
from universal_funct import thresholder
from universal_funct import band_extractor
from universal_funct import np_batch_writer
import spectra

def umix5(no_atm_data, pa_binary):
    """
    One of the unmixings in the second stage of the workflow. Currently empty

    Parameters:
    no_atm_data - a 2D array of atmospherically corrected image. pixel x band
    pa_binary   - a 2D array containing indicating the presence/absence
                  of snow/ice/shadows

    Return:
    Returns the presence/absence of the endmembers
    """

    # Everything is empty for now
    (norm_const_5,
     abundances_5) = endmember_finder(fifth_unmixing,
                                      zero_member, zero_member,
                                      zero_member, zero_member,
                                      zero_member, zero_member,
                                      zero_member)
    
    pa_arr_5 = thresholder(abundances_5,
                           (0, 0, 0, 0, 0, 0, 0))
    band_29 = pa_arr_5[0]
    band_30 = pa_arr_5[1]
    band_31 = pa_arr_5[2]
    band_32 = pa_arr_5[3]
    band_33 = pa_arr_5[4]
    band_34 = pa_arr_5[5]
    band_35 = pa_arr_5[6]

    """
    # --------------------------------
    # Fifth unmixing writing
    band_29 += border_arr
    band_30 += border_arr
    band_31 += border_arr
    band_32 += border_arr
    band_33 += border_arr
    band_34 += border_arr
    band_35 += border_arr
    dst.write_band(29, np.reshape(band_29,
                                  image_dim).astype(np.int16))
    dst.write_band(30, np.reshape(band_30,
                                  image_dim).astype(np.int16))
    dst.write_band(31, np.reshape(band_31,
                                  image_dim).astype(np.int16))
    dst.write_band(32, np.reshape(band_32,
                                  image_dim).astype(np.int16))
    dst.write_band(33, np.reshape(band_33,
                                  image_dim).astype(np.int16))
    dst.write_band(34, np.reshape(band_34,
                                  image_dim).astype(np.int16))
    dst.write_band(35, np.reshape(band_35,
                                  image_dim).astype(np.int16))
    # --------------------------------
    """

    name_list = ['band_29.txt', 'band_30.txt', 'band_31.txt',
                 'band_32.txt', 'band_33.txt', 'band_34.txt',
                 'band_35.txt']

    # Writes the relevant information to text files to be transferred over to
    # other tasks
    np_batch_writer(name_list, band_29, band_30, band_31, band_32, band_33,
                    band_34, band_35)

    return (band_29, band_30, band_31, band_32, band_33,
            band_34, band_35)
