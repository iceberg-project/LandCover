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
import pysptools.abundance_maps.amaps as amaps


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
    
    working_dir = ('C:/Users/Brian/Documents/Salvatore Research/' +
                   'WIP/polar_rock_repo_multispectral_WV02.txt')

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

def endmember_finder(band_data, spect_arr, run_count):
    """
    Reads the .txt file containing the possible geologic endmembers. 
    Parameters:
    band_data - an array containing the band data collected from satellite
                imagery. pixel x band
    spect_arr - an array containing the band data collected from ground
                samples. endmember x band
    run_count - the number of times to run the pysptools endmember
                extraction function, with each time using a different
                set of 8 endmembers
    Return:
    Returns two arrays. The first contains the abundances of the endmembers
    in each run. run x endmember abundance. The second contains the indices
    of those endmembers. run x endmember
    """

    # Keeps track of the sample used in each endmember extraction run
    index_list = []

    # Keeps track of the abundances in each run
    abundances = []

    # In each run...
    for i in range(run_count):
        # A temporary list to store the indices of samples
        temp_list = []

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

        # A temporary list to store the band data of the chosen samples
        temp_endm = []
        # For each sample, store the band data in the list
        for index in temp_list:
            temp_endm.append(spect_arr[index])

        # Turns the list into a numpy array to be put into the pysptools
        # function
        temp_endm = np.array(temp_endm)

        # Stores the indices into the index list
        index_list.append(temp_list)

        # Gets the abundances from this particular set of endmembers
        temp_abun = amaps.NNLS(band_data, temp_endm)
        # Stores the abundances in the list
        abundances.append(temp_abun)

    """
    Visualization stuff. Unblock if band 1 comparison of the first pixel is
    needed between the actual data and the sum of extracted endmembers
    print(abundances[0][0])
    print(band_data[0])
    new = []
    for i in index_list:
        new.append(spect_arr[i])
    new = np.array(new)
    print(new)
    der = new.transpose()[0].transpose() * abundances[0][0]
    print(der)
    print(der.sum())
    input()
    """

    # Returns the abundance and index lists
    return (abundance, index_list)


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
    """

    # Variables used to hold the band data and the image dimensions,
    # respectively
    band_data = []
    image_dim = 0

    # Opens the image
    src = rasterio.open(image_dir)

    # Gets and saves the dimensions of the image
    image_dim = src.read(1).shape
    
    # For each band (from bands 1 through 8)...
    for band in range(1, 9):
        # Save the band data in the array above
       band_data.append(src.read(band).ravel())

    # Closes the image
    src.close()

    # At this point, the data is now in a 2D array that looks like this:
    # [[1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], \\1st band
    #  [1st pixel, 2nd pixel, 3rd pixel, ... nth pixel], \\2nd band
    #   ...
    # This was done by combining the rows together so that the first pixel
    # of the next row is right next to the last pixel of the current row

    # Turns the list into a numpy array
    band_data = np.array(band_data)

    # Swaps the rows and columns of the array. It is now pixel x band.
    band_data = band_data.transpose(1, 0)

    # Returns the band data and image dimensions
    return (band_data, image_dim)


def main():
    
    #(working_dir, run_count) = args_parser()

    working_dir = 'C:/Users/Brian/Documents/Salvatore Research/test_image'
    run_count = 1

    # A list that contains all of the "_class" .tif files
    class_files = []
    # Keeps track of the number of the "_class" files
    class_count = 0
    
    for file in os.listdir(working_dir):
        if (file.endswith('_class.tif')):
            class_files.append(file)
            class_count += 1
        else:
            continue

    # If the class file does not exist...
    if class_count != 0:

        # Extract the downsampled PRR samples as potential endmembers
        (name_arr, spect_arr) = endmember_reader(working_dir)
        
        # For each detected _class.tif image file...
        for image in class_files:
            endmember_exist = os.path.isfile(
                os.path.join(working_dir,
                             image.replace('.tif', '_endmember.tif')))

            if not endmember_exist:
                # The file address of the image
                image_dir = os.path.join(working_dir, image)
                (band_data, image_dim) = band_extractor(image_dir)
                (abundance, index_list) = endmember_finder(band_data, spect_arr,
                                                           run_count)
                

            else:
                continue

    """
    test = np.array([[4, 2, 4],
                    [3, 3, 3]])
    print(test.shape)
    end_test = np.array([[2, 1, 2],
                        [1, 2, 1]])

    abundance_test = amaps.NNLS(test, end_test)
    print(abundance_test)
    """

main()

