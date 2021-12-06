import numpy
from universal_funct import rms_finder
import rasterio
import spectra
import os

def writer(working_dir, image, border_arr, lit_geo,
           rock_abun, norm_const_rock,
           shadrock_binary, shadice_binary, snowice_binary,
           litrock_binary, band_5, band_6, unknown_binary,
           more_dol_binary, less_dol_binary, granite_binary,
           sandstone_binary, band_12, band_13, band_14,
           snow_binary, blueice_binary, water_binary,
           band_18, band_19, band_20, band_21,
           band_22, band_23, band_24, band_25,
           band_26, band_27, band_28, band_29,
           band_30, band_31, band_32, band_33,
           band_34, band_35, band_36):
    """
    Writes the 36 bands (35 from the unmixing and 1 from here) to an
    output image

    Parameters:
    working_dir     - the working directory that was passed in
    image           - the image name
    rock_abun       - the abundance of the rock endmembers (used to calculate
                      the RMS of the rock unmixing for the 36th band)
    norm_const_rock - the constant used to normalize the rock unmixing
    
    The rest of the inputs are the presence/absence of endmember bands
    in the order they will be written in the output image

    Return:
    None
    """

    # Calculates the RMS of one of the unmixings. In this case it's
    # the RMS of the rock unmixing
    rms = rms_finder(rock_abun, norm_const_rock, lit_geo,
                     spectra.more_dol, spectra.less_dol, spectra.granite,
                     spectra.sandstone, spectra.zero_member,
                     spectra.zero_member, spectra.zero_member)

    # Combines the passed in working directory and the current image
    image_dir = os.path.join(working_dir, image)

    # Get meta file of the image
    src = rasterio.open(image_dir)
    meta = src.meta
    src.close()

    # Changes some parts of the metadata for the output image:
    # There are 36 bands in the output image
    meta['count'] = 36
    # Lowers the precision of the output to save disk space
    meta['dtype'] = np.int16
    # Specifies areas of the image that contains no data
    meta['nodata'] = -99
    # Specifies the compression algorithm used on the output image
    meta['compress'] = "LZW"

    # Holds the passed in bands for easier writing
    band_holder = [shadrock_binary, shadice_binary, snowice_binary,
                   litrock_binary, band_5, band_6, unknown_binary,
                   more_dol_binary, less_dol_binary, granite_binary,
                   sandstone_binary, band_12, band_13, band_14,
                   snow_binary, blueice_binary, water_binary,
                   band_18, band_19, band_20, band_21,
                   band_22, band_23, band_24, band_25,
                   band_26, band_27, band_28, band_29,
                   band_30, band_31, band_32, band_33,
                   band_34, band_35, band_36]

    # Creates the output image
    dst = rasterio.open(image_dir.replace(".tif", "_endmember.tif"), 'w', **meta)

    # Writes the 36 bands
    for i in range(36):
        dst.write_band(i+1, np.reshape(band_holder[i],
                                       imag_dim).astype(np.int16))

    dst.close()
