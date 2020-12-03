"""
Author: Brian Szutu
Email: bs886@nau.edu


This script is used to find the endmembers of each pixel of the WV2 .tif images
present within the user-specified directory/folder. There are two packages that
are used that need to be manually installed: rasterio and pysptools. rasterio
is used to access the band data within each WV2 .tif image and pysptools
is used as the endmember finder.

The output file is sent to the folder the used image resides in.

This script is safe to run multiple times in the same directory.
"""

import os
import argparse
import numpy as np
import random
import rasterio
import sys
import pysptools.abundance_maps.amaps as amaps
import matplotlib.pyplot as plt


def args_parser():
    """
    Reads the image directory passed in from console. Also reads in the
    number of runs the endmember extractor should do.
    Parameters:
    None
    Return:
    Returns a directory that has the images to be analyzed within it
    """

    # Creates an ArgumentParser object to hold the console input
    parser = argparse.ArgumentParser()
    
    # Adds an argument to the parser created above. Holds the
    # inputted directory as a string
    parser.add_argument('-ip', '--input_dir', type=str,
                        help='The directory containing the images.')
    parser.add_argument('-run_n', '--run_count', nargs='?',
                        const=500, default=500, type=int,
                        help='The number of runs to be done by the'
                        +' endmember extractor.')

    # Returns the passed in directory
    return (parser.parse_args().input_dir, parser.parse_args().run_count)


def endmember_reader(working_dir):
    """
    Reads the .txt file containing the possible geologic endmembers. 
    Parameters:
    working_dir - the directory that was passed in from the console
    Return:
    Returns two arrays. The first contains the sample ID, lithology type,
    and whether the sample was from a specimen's surface or interior. The
    second array contains the eight bands that the spectral data was
    downsampled to.
    """
    
    #working_dir = ('C:/Users/Brian/Documents/Salvatore Research/' +
    #               'WIP/polar_rock_repo_multispectral_WV02.txt')

    # Creates two lists to store the descriptions of each sample and the
    # eight bands downsampled to, respectively
    name_arr = []
    spect_arr = []

    # A temporary list to store the text from the document
    temp_arr = []

    # Opens the .txt file containing the possible endmembers
    with open(working_dir, 'r') as endmem_file:
        # and stores the text into the temporary list
        temp_arr = [line.strip().split() for line in endmem_file]

    # Closes the file
    endmem_file.close()

    # Stores the descriptions into the appropriate list
    name_arr = temp_arr[0:2]
    # Lops off the extraneous information (what each descriptor is)
    for i in range(len(name_arr)):
        name_arr[i] = name_arr[i][1:]

    # Converts the list to a numpy array
    name_arr = np.array(name_arr, dtype='str')
    # Transposes the array to more easily access the information
    # through indexing
    name_arr = name_arr.transpose(1, 0)

    # Stores the each sample's eight bands
    spect_arr = temp_arr[3:]
    # Lops off the extraneous information (what each band corresponds to)
    for i in range(len(spect_arr)):
        spect_arr[i] = spect_arr[i][1:]

    # Converts the list to a numpy array
    spect_arr = np.array(spect_arr, dtype='float')
    # Transposes the array to match the pysptools input format
    spect_arr = spect_arr.transpose(1, 0)

    # Returns the two arrays
    return (name_arr, spect_arr)


def categorizer(name_arr, spect_arr):
    """
    Categorizes the Polar Rock Repository samples into eight categories
    to be used in the endmember extraction process. Each category will
    have one endmember randomly drawn from it for the endmember extraction
    process.

    Parameters:
    name_arr  - an array containing the labels of the the samples
    spect_arr - an array containing the band data of the samples.
                Its indices correspond with the labels in name_arr

    Return:
    Returns two arrays. The first contains the associated categorized
    sample labels. The second contains the categorized sample band data.
    """

    # Pulls out the number of samples in the PRR
    spect_size = spect_arr.shape[0]

    # A dictionary containing the categories for PRR samples to be
    # split up into. EDIT THE LISTS IF DIFFERENT CATEGORIZATION IS NEEDED
    cat_dict = {0:['GRANITE'],
                1:['GRANITE'],
                2:['GRANITE'],
                3:['GRANITE'],
                4:['GRANITE'],
                5:['GRANITE'],
                6:['GRANITE'],
                7:['GRANITE']}

    # The output, categorized arrays. Will be turned into
    # numpy arrays later
    name_cat = [[],[],[],[],[],[],[],[]]
    spect_cat = [[],[],[],[],[],[],[],[]]

    # For each category...
    for i in range(8):
        
        # Get the specific category...
        category = cat_dict[i]

        # For each sample...
        for j in range(spect_size):

            # If the rock type of the sample is in the category...
            if name_arr[j][1] in category:

                # Put the sample's band data and its labels into the
                # current category's respective lists (name and spect)
                name_cat[i].append(name_arr[j])
                spect_cat[i].append(spect_arr[j])

    # Turns the two list of lists into numpy arrays
    name_cat = np.array(name_cat)
    spect_cat = np.array(spect_cat)
    
    return (name_cat, spect_cat)


def endmember_finder(band_data, spect_cat, run_count):
    """
    Reads the .txt file containing the possible geologic endmembers. 
    Parameters:
    band_data - an array containing the band data collected from satellite
                imagery. pixel x band
    spect_cat - an array containing the band data collected from ground
                samples. category x endmember x band
    run_count - the number of times to run the pysptools endmember
                extraction function, with each time using a different
                set of 8 endmembers
    Return:
    Returns two arrays. The first contains the abundances of the endmembers
    in each run. run x endmember abundance. The second contains the indices
    of those endmembers. run x endmember. KEEP IN MIND THAT EACH OF THESE
    INDICES CORRESPONDS TO ITS OWN CATEGORY. Also returns the pixel RMS
    values and the total RMS value of each run
    """

    # Keeps track of the sample used of each endmember extraction run
    index_list = []

    # Keeps track of the abundances of each run
    abundances = []

    # Keeps track of the band and total RMS values of each run
    abund_total_rms = []
    abund_pixel_rms = []

    # In each run...
    for i in range(run_count):
        
        # A temporary list to store the indices of samples
        temp_list = []


        """
        # While there aren't eight endmembers to use in the endmember
        # extraction function...
        while len(temp_list) != 8:
            # Get a random endmember...
            rand_n = random.randrange(0, len(spect_arr))

            # And if the endmember wasn't already picked...
            if rand_n not in temp_list:
                # Save it to be used
                temp_list.append(rand_n)

            # If the endmember list matches a previously used one...
            if len(temp_list) == 8 and temp_list in index_list:
                # Empty the list and start over
                temp_list = []
        """

        while len(temp_list) != 8:
            # For each category to pull the endmembers from...
            for categ in spect_cat:
                
                # Get the index of a endmember in the category...
                rand_n = random.randrange(0, categ.shape[0])

                # And add the index to the temporary list
                temp_list.append(rand_n)
            
            # If the endmember index list matches a previously used one...
            if len(temp_list) == 8 and temp_list in index_list:
                
                # Empty the list and start over
                temp_list = []
            

        # A temporary list to store the band data of the chosen samples
        temp_endm = []

        """
        # For each sample, store the band data in the list
        for index in temp_list:
            temp_endm.append(spect_arr[index])
        """

        # For each category...
        for i in range(len(temp_list)):

            # Append the randomly chosen, appropriate endmember to
            # temporary endmember list
            temp_endm.append(spect_cat[i][temp_list[i]])

        # Turns the list into a numpy array to be put into the pysptools
        # function
        temp_endm = np.array(temp_endm)

        # Stores the indices into the index list
        index_list.append(temp_list)

        # Gets the abundances from this particular set of endmembers
        temp_abun = amaps.NNLS(band_data, temp_endm)
        
        # Stores the abundances in the list
        abundances.append(temp_abun)

        # Finds the RMS values between the bands and the total RMS value
        # of all of the bands put together
        (pixel_rms, total_rms) = rms_finder(temp_endm, temp_abun, band_data)

        # Adds the RMS values to their respective lists
        abund_total_rms.append(total_rms)
        abund_pixel_rms.append(pixel_rms)

    # Turns the RMS lists into arrays
    abund_pixel_rms = np.array(abund_pixel_rms)
    abund_total_rms = np.array(abund_total_rms)

    # Returns the abundances, indices, and RMS values
    return (abundances, index_list, abund_pixel_rms, abund_total_rms)


def rms_finder(endm_arr, abundances, band_data):
    """
    Finds the RMS values of the output abundances.

    Parameters:
    endm_arr   - an array containing the band data of the eight
                 endmembers that were chosen to be in the extraction process
    abundances - an array containing the abundances of the above eight
                 endmembers in each pixel
    band_data  - the measured data in each band in the image

    Return:
    Returns two different RMS values. One contains the RMS values for pixel.
    The other contains the overall image RMS value.
    """

    # Holds all of the modelled band data
    modelled_bands = []

    # For each pixel's calculated abundances...
    for pixel_abund in abundances:

        # Temporarily holds the modelled band data pulled out of the
        # abundances and endmember band data
        temp_arr = []

        # For each endmember's abundance...
        for i in range(len(pixel_abund)):
            # Multiply the abundance to the related endmember's band data
            temp_arr.append(pixel_abund[i] * endm_arr[i])

        # Sum the numbers bandwise. So only 8 values, one value per band, is
        # left behind. This is the modelled band of the pixel
        temp_arr = np.sum(np.array(temp_arr), axis=1)

        # Append the modelled band
        modelled_bands.append(temp_arr)

    # Gets the square of the difference between the measured band data and
    # the modelled band data
    diff_sq_arr =  np.square(band_data - modelled_bands)

    # Gets the number of pixels in the image
    pixel_n = band_data.shape[0]

    # Calculates the RMS with respect to each pixel
    pixel_rms = np.sqrt(1/8 * np.sum(diff_sq_arr, axis=1))

    # Calculates the RMS value with respect to the entire image
    total_rms = np.sqrt(1/(8*pixel_n) * np.sum(diff_sq_arr))

    # Returns the pixel and image RMS values
    return (pixel_rms, total_rms)


def band_extractor(image_dir):
    """
    Extracts the band data from the image at the given file address.
    It then transforms the the 3D numpy array representing the
    band data into a 2D array so that the pysptools endmember
    finder can take the data. The 2D array is dimensioned pixel x band.

    Parameters:
    image_dir - the file address of the image

    Return:
    Returns the dimensions of the image with the band data. The band
    data is formatted as a 2D array, whose dimensions are pixel x band.
    Also returns the non-data bands in their original band x row x column
    format. The meta data is returned so that the output image of the
    script has it
    """

    # Variables used to hold the band data and the image dimensions,
    # respectively
    band_data = []
    band_extr = []
    image_dim = 0

    # Opens the image
    src = rasterio.open(image_dir)

    # Gets the meta data of the image
    meta = src.meta

    # Gets and saves the dimensions of the image
    image_dim = src.read(1).shape
    
    # For each band (from bands 1 through 8)...
    for band in range(1, 9):
        # Save the band data in the array above. "Squishes" the 3D
        # image stack into a 2D "line" stack, with the formatting
        # displayed a few lines down
        band_data.append(src.read(band).ravel())

    # Adds the non-data bands into the extraneous band list.
    # No need to lose the dimensioning unlike the above since these
    # bands are not passed through the endmember extractor
    for band in range(9, 19):
        band_extr.append(src.read(band))

    # Closes the image
    src.close()

    # FORMATTING SO FAR
    # At this point, the data is now in a 2D array that looks like this:
    # [[1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], //1st band
    #  [1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], //2nd band
    #   ...
    # This was done by combining the rows together so that the first pixel
    # of the n+1th row is right next to the last pixel of the nth row

    # Turns the list into a numpy array
    band_data = np.array(band_data)

    # Swaps the rows and columns of the array. It is now pixel x band.
    band_data = band_data.transpose(1, 0)

    # Turns the extraneous band list of list into a numpy array
    band_extr = np.array(band_extr)

    # Returns the band data and image dimensions
    return (band_data, band_extr, image_dim, meta)

def abundance_writer(image_dir, image_dim, band_data, band_extr,
                     abund_final, rms_final, meta):
    """
    Writes eight new bands into the passed in image. These bands
    are essentially true/false (1/0) for each of the eight rock
    categories existing. The thresholding for whether or not a rock
    category exists is also held in here.

    Parameters:
    image_dir   - the directory of the input image
    image_dim   - the dimensions of the image (row x column)
    band_data   - the data held within each pixel and at each band
    band_extr   - the extraneous bands in the image
    abund_final - the final abundances that correspond to the run
                  with the smallest image RMS value
    rms_final   - the final pixel RMS values that correspond to the
                  run with the smallest image RMS value
    meta        - the meta data of the passed in image

    Return:
    None
    """


    # Starts the process of turning the band data array back into a
    # a format that allows for it to be written into an image...
    # band x pixel
    band_data = band_data.transpose(1, 0)

    # Temporarily houses the properly dimensioned data
    temp_band = []

    # For each band...
    for i in range(band_data.shape[0]):
        # Unsquish the band pixels. Basically turn it back into an
        # image
        temp_band.append(np.reshape(band_data[i], image_dim))

    # Replaces the squished image with the non-squished one
    band_data = np.array(temp_band)

    # Begins the dimensioning process with the abundances. It's the
    # same thing as the process with the band data up above
    abund_final = abund_final.transpose(1, 0)

    # Temporarily holds the dimensioned abundances
    temp_abund = []

    # For each category...
    for i in range(abund_final.shape[0]):
        temp_abund.append(np.reshape(abund_final[i], image_dim))

    # Replaces the squished abundances with the non-squished ones
    abund_final = np.array(temp_abund)

    # Unsquishes the RMS values per pixel, like the above
    rms_unsquish = np.array([np.reshape(rms_final, image_dim)], dtype=np.float32)
    
    # Creates the bands that show whether or not a category exist
    # EDIT THE CONDITION HERE TO MODIFY THE THRESHOLD FOR EXISTING
    cat_exists = np.where(abund_final > 0.4, 1, 0)

    """
    plt.imshow(cat_exists[0])
    plt.show()
    print(cat_exists[0][110])
    print(cat_exists[0][110].shape)
    """

    # Creates the array to be written to a file
    final_arr = np.concatenate((band_data, band_extr))
    final_arr = np.concatenate((final_arr, abund_final))
    final_arr = np.concatenate((final_arr, rms_unsquish))

    # Creates the filename of the image to be outputted
    out_dir = image_dir.replace('.tif', '_endmember.tif')

    # Changes the band count in the metadata 
    meta['count'] = 27
    
    # Creates the new file...
    with rasterio.open(out_dir, 'w', **meta) as dst:

        # And writes the data/numbers to the new file
        dst.write(final_arr)



def main():

    # Gets the working directory and the number of times for the endmembers
    # to be randomly chosen
    #(working_dir, run_count) = args_parser()

    working_dir = 'C:/Users/Brian/Documents/Salvatore Research/test_image'
    run_count = 1

    # A list that contains all of the "_class" .tif files
    class_files = []
    # Keeps track of the number of the "_class" files
    class_count = 0

    # Saves whether or not the endmember library exists 
    endmember_lib_exist = False

    # Finds all of the ..._class.tif image filess in the directory
    for file in os.listdir(working_dir):
        if (file.endswith('_class.tif')):
            class_files.append(file)
            class_count += 1
        elif file == "polar_rock_repo_multispectral_WV02.txt":
            endmember_lib_exist = True
            

    # If the class file does not exist...
    if class_count != 0:

        # Extract the downsampled PRR samples as potential endmembers
        endmember_lib_dir = os.path.join(working_dir,
                                         "polar_rock_repo_multispectral_WV02.txt")
        (name_arr, spect_arr) = endmember_reader(endmember_lib_dir)

        (name_cat, spect_cat) = categorizer(name_arr, spect_arr)
        
        # For each detected _class.tif image file...
        for image in class_files:
            endmember_exist = os.path.isfile(
                os.path.join(working_dir,
                             image.replace('.tif', '_endmember.tif')))

            if not endmember_lib_exist:
                print("The endmember library does not exist!")

            # If the endmembers of the image weren't extracted and outputted
            elif not endmember_exist:
                
                # The file address of the image
                image_dir = os.path.join(working_dir, image)
                
                # Gets the image's band data and dimensions
                (band_data, band_extr, image_dim, meta) = \
                            band_extractor(image_dir)

                # Gets the abundances, the endmembers used (in the form
                # of indices), and the pixel and image RMS values
                (abundances, index_list,
                 abund_pixel_rms,
                 abund_total_rms) = endmember_finder(band_data, spect_cat,
                                                     run_count)

                # Gets the sorted indices
                sorted_ind = np.argsort(abund_total_rms)

                # Uses it to sort the abundances based on run
                temp_abund = []
                temp_pixel_rms = []
                for ind in sorted_ind:
                    temp_abund.append(abundances[ind])
                    temp_pixel_rms.append(abund_pixel_rms[ind])

                # Just overwrites the old abundances array with the sorted one
                abundances = temp_abund

                # Takes the abundances with the smallest image RMS value and
                # saves it to be written
                abund_final = abundances[0]

                # Saves the pixel RMS values of the run with the smallest
                # image RMS value
                pixel_rms_final = temp_pixel_rms[0]

                # Writes the image
                abundance_writer(image_dir, image_dim, band_data,
                                 band_extr, abund_final, pixel_rms_final, meta)

            if endmember_exist:

                print(image.replace('.tif', '_endmember.tif') + ' already exists!')


main()

