import rasterio
import numpy
from universal_funct import endmember_finder
from universal_funct import thresholder
from universal_funct import band_extractor
from universal_funct import np_batch_writer
import spectra

def umix4(no_atm_data, pa_binary):
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
    fourth_unmixing = np.multiply(np.float16(no_atm_data), 0)
    
    (norm_const_4,
     abundances_4)= endmember_finder(fourth_unmixing,
                                     zero_member, zero_member,
                                     zero_member, zero_member,
                                     zero_member, zero_member,
                                     zero_member)
    
    pa_arr_4 = thresholder(abundances_4,
                           (0, 0, 0, 0, 0, 0, 0))
    band_22 = pa_arr_4[0]
    band_23 = pa_arr_4[1]
    band_24 = pa_arr_4[2]
    band_25 = pa_arr_4[3]
    band_26 = pa_arr_4[4]
    band_27 = pa_arr_4[5]
    band_28 = pa_arr_4[6]

    """
    # --------------------------------
    # Fourth unmixing writing
    band_22 += border_arr
    band_23 += border_arr
    band_24 += border_arr
    band_25 += border_arr
    band_26 += border_arr
    band_27 += border_arr
    band_28 += border_arr
    dst.write_band(22, np.reshape(band_22,
                                  image_dim).astype(np.int16))
    dst.write_band(23, np.reshape(band_23,
                                  image_dim).astype(np.int16))
    dst.write_band(24, np.reshape(band_24,
                                  image_dim).astype(np.int16))
    dst.write_band(25, np.reshape(band_25,
                                  image_dim).astype(np.int16))
    dst.write_band(26, np.reshape(band_26,
                                  image_dim).astype(np.int16))
    dst.write_band(27, np.reshape(band_27,
                                  image_dim).astype(np.int16))
    dst.write_band(28, np.reshape(band_28,
                                  image_dim).astype(np.int16))
    # --------------------------------
    """

    name_list = ['band_22.txt', 'band_23.txt', 'band_24.txt',
                 'band_25.txt', 'band_26.txt', 'band_27.txt',
                 'band_28.txt']

    # Writes the relevant information to text files to be transferred over to
    # other tasks
    np_batch_writer(name_list, band_22, band_23, band_24, band_25, band_26,
                    band_27, band_28)

    return (band_22, band_23, band_24, band_25, band_26,
            band_27, band_28)
