import numpy as np
import rasterio
import pysptools.abundance_maps.amaps as amaps

# Functions used in other parts of the workflow

def border_finder(band_data, image_dim):
    """
    Finds the parts of the passed in image that lie beyond the parts with data

    Parameters:
    band_data - the spectra of the passed in image (pixel x band)
    image_dim - the dimensions of the passed in image

    Return:
    Returns a 1D array (pixel x band) with either 0 or -99 as each element.
    Any element that's -99 inhabits a pixel that is beyond the image's border 
    """

    # Finds the pixels (by their matrix indices) that do not have any data
    border_arr = np.where(~band_data.any(axis=1), -99, 0)

    return border_arr


def band_extractor(image_dir):
    """
    Extracts the band data from the image at the given file address.
    It then transforms the the 3D numpy array representing the
    band data into a 2D array so that the pysptools endmember
    finder can take the data. The 2D array is dimensioned pixel x band.

    Parameters:
    image_dir - the file address of the image

    Return:
    Returns the band data with the dimensions of the image. The band
    data is formatted as a 2D array (pixel x band).
    The meta data is returned so that the output image of the
    script has it
    """

    # List used to hold the band data 
    #band_data = []

    # Opens the image
    src = rasterio.open(image_dir)

    # Gets the meta data of the image
    meta = src.meta

    # Gets and saves the dimensions of the image
    image_dim = src.read(1).shape

    # Reads the data in the image, reshapes the data by "flattening" each band,
    # and saves it. The array saved should be band x pixel
    band_data = np.reshape(src.read(), (8, -1))

    # Closes the image
    src.close()

    # FORMATTING SO FAR
    # At this point, the data is now in a 2D array that looks like this:
    # [[1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], //1st band
    #  [1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], //2nd band
    #   ...
    # This was done by combining the rows together so that the first pixel
    # of the next row is right next to the last pixel of the current row
    # so it looks like the following:
    # [1][2]...[n-1][n]FROM NEXT ROW->[1][2]...[n-1][n] etc

    # Turns the list into a numpy array
    band_data = np.array(band_data, dtype=np.float16)

    # Swaps the rows and columns of the array. It is now pixel x band.
    band_data = band_data.transpose(1, 0)

    # Makes sure the pixel values of the image is less than 1 to match
    # the top-of-atmosphere reflectance format
    if band_data[0,0] > 10:
        band_data = np.divide(band_data, 1000)

    # Returns the band data and image dimensions
    return (band_data, image_dim, meta)



def median_finder(name_arr, endmember_arr, category):
    """
    Finds the median spectrum for a given rock type (ie granite, gneiss,
    etc)

    Parameters:
    name_arr      - the categories and PRR numbers of the endmembers
    endmember_arr - an array containing the spectra of the endmember library
    category      - a string indicating what rock type to find the median of
    
    Return:
    Returns a 1D numpy array representing the median spectrum of the specified
    rock type
    """

    # Initializes a list to hold the samples of the specified rock type
    cat_arr = []
    
    # Gets the indices of the samples that are the passed in rock
    # category
    cat_ind = np.where(name_arr == category)

    # Since the PRR sample spectra are in the same order, the indices can be
    # used to pull the spectra
    cat_arr = endmember_arr[cat_ind[0]]

    # Gets the median spectrum
    median_spectrum = np.median(cat_arr, axis=0)

    return median_spectrum


def rms_finder(abundances, norm_const, band_data, *endmembers):
    """
    Finds the RMS values of the output abundances.
    Note: Each pixel RMS should be somewhere between 0 and 1, inclusive,
          due to how RMS is defined

    Parameters:
    abundances - an array containing the abundances of the above
                 endmembers in each pixel. pixel x endmember
    norm_const - a constant used to normalize the abundance values. It
                 is the maximum sum of abundances of endmembers
                 (each pixel has its own sum, the constant is the biggest
                 sum)
    band_data  - the values the found abundances are to be compared to
    endmembers - a tuple containing the band data of the endmembers
                 that were chosen to be in the extraction process

    Return:
    Returns the RMS values for each pixel. 1D array
    """

    # Keeps track of the simulated contributions to the data by each
    # endmember
    temp_arr = []

    # Used as an index to access the abundances array
    band_n = 0

    # Un-normalizes the abundances
    abundances = np.multiply(abundances, norm_const)

    # For each endmember...
    for endmember in endmembers:

        # Multiplies endmember spectra with the corresponding abundances
        # to produce the contribution of the endmember spectra in the
        # image
        simul_data = np.multiply(endmember, abundances[:, band_n,
                                                       np.newaxis])

        # Lowers the precision of the data to take less space
        simul_data = simul_data.astype(np.float16)

        # Appends the simulated contribution to the temporary array
        temp_arr.append(simul_data)

        # Adds one to the index
        band_n += 1

    # Sum the numbers bandwise. So only 8 values, one value per band, are
    # left behind. This is the modelled band of the pixel
    temp_arr = np.sum(np.array(temp_arr), axis=0)

    # Gets the square of the difference between the measured band data and
    # the modelled band data
    diff_sq_arr =  np.square(band_data - temp_arr)

    # Calculates the RMS from the above difference-squared array.
    # The 8 is from there being eight different bands
    pixel_rms = np.sqrt(1/8 * np.sum(diff_sq_arr, axis=1))

    # Returns the pixel and image RMS values
    return pixel_rms


def thresholder(abundances, thresholds):
    """
    Creates the presence/absence arrays with the passed in abundances and
    thresholds.

    Parameters:
    abundances - an array of abundances. pixel x endmember abundance
    thresholds - a tuple of arbitrary thresholds. Change what is passed in
                 to affect how lenient/strict the thresholding is. Passed in
                 values should be -1 or between 0 and 1, inclusive. An input
                 of -1 excludes corresponding endmember from being thresholded
                 and outputted
                 NOTE:
                 Some of the abundance values may be above 1 due to how
                 the imported NNLS function works

    Return:
    Returns a list of presence/absence arrays.
    endmember x pixel presence/absence
    """

    # Stores all of the presence/absence arrays to be returned 
    pa_arr = []

    # For each set of abundances...
    for i in range(abundances.shape[1]):

        # If the threshold isn't -1, the abundance won't be ignored
        # and the presence/absence array will be produced
        if thresholds[i] != -1:
            # Gets the ith abundance
            abun_i = abundances[:,i]
            # Creates the presence/absence array
            binary_i = np.where(abun_i > thresholds[i], 1, 0)
            # Appends the array to the list that's supposed to be returned
            pa_arr.append(binary_i)
            
    return pa_arr


def np_batch_writer(names, *write_arr):
    """
    Parameters:
    names     - the names of the specific numpy arrays to be written to file.
                Done to transfer the arrays from task to task in the workflow.
                list of strings
    write_arr - the numpy arrays containing the information to be written to
                file.
                any number of numpy arrays that match the number of given names

    Return:
    None
    """

    # Keeps track of which array to save
    i = 0

    # For each given name, save it and its corresponding array
    for name in names:
        np.savetxt(name, write_arr[i])



