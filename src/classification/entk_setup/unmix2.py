import rasterio
import numpy
from universal_funct import border_finder
from universal_funct import endmember_finder
from universal_funct import thresholder
from universal_funct import band_extractor
from universal_funct import np_batch_writer
import spectra

def unmix2(no_atm_data, pa_binary):

    """
    One of the unmixings done in the second stage of the workflow. Specifically
    unmixes the types of rocks

    Parameters:
    no_atm_data - a 2D array of atmospherically corrected image. pixel x band
    pa_binary   - a 2D array containing indicating the presence/absence
                  of snow/ice/shadows

    Return:
    Returns the part of the image that has been deemed to be unshadowed rocks.
    Also returns a constant that was used to normalize the abundances.
    The array containing the raw abundances and the array indicating
    the presence/absence (1/0) of rocks are also included. Finally,
    the presence/absence of each endmember are returned
    """
    
    # Reverses the presence/absence of snow/ice/shadow array
    temp_border_arr = border_finder(band_data, image_dim)
    temp_border_arr = np.where(temp_border_arr == -99, 1, 0)
    litrock_binary = np.subtract(np.where(pa_binary == 0, 1, 0),
                                 temp_border_arr)

    #plt.imshow(np.reshape(litrock_binary, image_dim))
    #print("LITROCK")
    #plt.show()
    

    # If all bands of a pixel are non-zero, the pixel is a rock
    lit_geo = np.multiply(np.float16(no_atm_data),
                          np.int16(litrock_binary[:, np.newaxis]))

    # Performs the unmixing process using the given rock
    # endmembers
    (norm_const_rock,
     rock_abun) = endmember_finder(spectra.lit_geo, spectra.more_dol,
                                   spectra.less_dol, spectra.granite,
                                   spectra.sandstone, spectra.zero_member,
                                   spectra.zero_member, spectra.zero_member)

    # {ABUNDANCES ORDER}:
    # more_dol, less_dol, granite, sandstone, zero, zero, zero
    pa_arr_2 = thresholder(rock_abun,
                           (0.25, 0.25, 0.25, 0.25, 0, 0, 0))

    # Gets the thresholded abundance arrays
    more_dol_binary = pa_arr_2[0]
    less_dol_binary = pa_arr_2[1]
    granite_binary = pa_arr_2[2]
    sandstone_binary = pa_arr_2[3]
    band_12 = pa_arr_2[4]
    band_13 = pa_arr_2[5]
    band_14 = pa_arr_2[6]

    """
    # --------------------------------
    # Rock Writing
    litrock_binary += border_arr
    band_5 += border_arr
    band_6 += border_arr
    unknown_binary += border_arr
    more_dol_binary += border_arr
    less_dol_binary += border_arr
    granite_binary += border_arr
    sandstone_binary += border_arr
    band_12 += border_arr
    band_13 += border_arr
    band_14 += border_arr
    dst.write_band(4, np.reshape(litrock_binary,
                                 image_dim).astype(np.int16))
    dst.write_band(5, np.reshape(band_5,
                                 image_dim).astype(np.int16))
    dst.write_band(6, np.reshape(band_6,
                                 image_dim).astype(np.int16))
    dst.write_band(7, np.reshape(unknown_binary,
                                 image_dim).astype(np.int16))
    dst.write_band(8, np.reshape(more_dol_binary,
                                 image_dim).astype(np.int16))
    dst.write_band(9, np.reshape(less_dol_binary,
                                 image_dim).astype(np.int16))
    dst.write_band(10, np.reshape(granite_binary,
                                  image_dim).astype(np.int16))
    dst.write_band(11, np.reshape(sandstone_binary,
                                  image_dim).astype(np.int16))
    dst.write_band(12, np.reshape(band_12,
                                  image_dim).astype(np.int16))
    dst.write_band(13, np.reshape(band_13,
                                  image_dim).astype(np.int16))
    dst.write_band(14, np.reshape(band_14,
                                  image_dim).astype(np.int16))
    # --------------------------------
    """

    name_list = ['lit_geo.txt', 'norm_const_rock.txt', 'rock_abun.txt',
                 'litrock_binary.txt', 'band_5.txt', 'band_6.txt', 'unknown_binary.txt',
                 'more_dol_binary.txt', 'less_dol_binary.txt', 'granite_binary.txt',
                 'sandstone_binary.txt', 'band_12.txt', 'band_13.txt', 'band_14.txt']

    # Writes the relevant information to text files to be transferred over to
    # other tasks
    np_batch_writer(name_list, lit_geo, norm_const_rock, rock_abun,
                    litrock_binary, band_5, band_6, unknown_binary,
                    more_dol_binary, less_dol_binary, granite_binary,
                    sandstone_binary, band_12, band_13, band_14)

    return (lit_geo, norm_const_rock, rock_abun,
            litrock_binary, band_5, band_6, unknown_binary,
            more_dol_binary, less_dol_binary, granite_binary,
            sandstone_binary, band_12, band_13, band_14)

