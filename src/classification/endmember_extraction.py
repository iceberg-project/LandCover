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

HOW TO USE:
Call the script from console and feed it an image directory like so:

python endmember_extraction.py -ip "INSERT DIRECTORY WITH THE QUOTES"

The given directory should directly house the images and will be the place
the script outputs images.

HOW TO MODIFY:
To change the threshold values that determine whether or not an endmember exists,
change the values in the tuple passed into thresholder(). The order
should match the order of the endmembers passed into endmember_finder. The order
is commented above each instance of thresholder().
Every single variable that begins with band_ is a TBD band for the output image.
They have no real associated endmember.
"""

import os
import argparse
import numpy as np
import random
import rasterio
import sys
import pysptools.abundance_maps.amaps as amaps
import matplotlib.pyplot as plt
import pickle
import gc
import time


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

    # Returns the passed in directory
    return (parser.parse_args().input_dir)


def endmember_reader(working_dir):
    """
    Reads the .txt file containing the possible geologic endmembers.
    
    Parameters:
    working_dir - the directory of the endmember library text file.
                  It should be in the Landcover pipeline in the lib folder
    
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



def endmember_finder(band_data, *endmembers):
    """
    Extracts the endmembers from the image using the given endmembers
    Parameters:
    band_data  - an array containing the band data collected from satellite
                 imagery. pixel x band
    endmembers - an tuple containing the endmembers to be extracted.
                 Its size depends on how many endmembers were passed in
                 endmember x band
    
    Return:
    Returns an array of the abundances of the passed in endmembers. The size
    varies depending on how many endmembers were passed in. pixel x band
    """

    # Turns the tuple of a variable number of endmembers into an array
    endmembers = np.array(endmembers)

    # Gets abundances
    abundances = amaps.NNLS(band_data, endmembers)
        
    return abundances


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


def rms_finder(abundances, band_data, *endmembers):
    """
    Finds the RMS values of the output abundances.
    Note: Each pixel RMS should be somewhere between 0 and 1, inclusive,
          due to how RMS is defined

    Parameters:
    abundances - an array containing the abundances of the above
                 endmembers in each pixel. pixel x endmember
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

    """
    # For each band (from bands 1 through 8)...
    for band in range(1, 9):
        # Save the band data in the array above. "Squishes" the 3D
        # image stack into a 2D "line" stack, with the formatting
        # displayed a few lines down
        band_data.append(src.read(band).ravel())
    """

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
    # of the n+1th row is right next to the last pixel of the nth row
    # so it looks like the following:
    # [1][2]...[n-1][n]FROM NEXT ROW->[1][2]...[n-1][n] etc

    # Turns the list into a numpy array
    band_data = np.array(band_data)

    # Swaps the rows and columns of the array. It is now pixel x band.
    band_data = band_data.transpose(1, 0)

    # Returns the band data and image dimensions
    return (band_data, image_dim, meta)

def time_printer(time1, time2):
    """
    Prints the time that has passed between time1 and time2. 

    Parameters:
    time1 - the first recorded time in seconds after Jan 1, 1970, 00:00:00
    time2 - the second recorded time in seconds after Jan 1, 1970, 00:00:00

    Return:
    None
    """

    # Finds the difference in times
    time_diff = time2 - time1

    # Converts the time passed from seconds to hours, minutes, and seconds 
    hours = int(time_diff // 3600)
    time_diff -= hours * 3600
    minutes = int(time_diff // 60)
    time_diff -= minutes * 60
    seconds = int(time_diff // 1)

    print(str(hours) + " hour(s), " + str(minutes) + " minute(s), and " +
          str(seconds) + " second(s) have passed since " +
          "the start of this process")


def thresholder(abundances, thresholds):
    """
    Creates the presence/absence arrays with the passed in abundances and
    thresholds.

    Parameters:
    abundances - an array of abundances. pixel x endmember abundance
    thresholds - a tuple of arbitrary thresholds. Change what is passed in
                 to affect how lenient/strict the thresholding is. Passed in
                 values should be -1 or between 0 and 1, inclusive.
                 NOTE:
                 some of the abundance values may be above 1 due to how
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


def abundance_writer(image_dir, image_dim, meta, border_arr, *bands):
    """
    Writes a band into the output image. Each band should contain
    the values 0 (absent), 1 (present), -99 (outside of image border).

    Parameters:
    image_dir - the directory of the input image
    image_dim - the dimensions of the image (row x column)
    meta      - the meta data of the passed in image
    bands     - tuple of any number of bands to be written into the new file

    Return:
    None
    """

    # Creates the filename of the image to be outputted
    out_dir = image_dir.replace('.tif', '_endmember.tif')

    # Changes the band count in the metadata 
    meta['count'] = len(bands)
    # Changes the datatype
    meta['dtype'] = np.int16
    # Changes the nodata value to -99
    meta['nodata'] = -99
    # Specifies a lossless compression method for rasterio to use
    # (the output file will be smaller while retaining information)
    meta['compress'] = "LZW"
    
    
    # Opens/creates the output file...
    with rasterio.open(out_dir, 'w', **meta) as dst:

        # Keeps track of the band number (for writing purposes only)
        band_n = 1
        # For each passed in band...
        for band in bands:

            # Adds in the beyond-the-image-border values
            band += border_arr
            
            # Write the band to the new file
            dst.write_band(band_n, np.reshape(band,
                                              image_dim).astype(np.int16))
            band_n += 1

def main():

    # Gets the working directory and the number of times for the endmembers
    # to be randomly chosen
    working_dir = args_parser()

    # A list that contains all of the "_class" .tif files
    class_files = []
    # Keeps track of the number of the "_class" files
    class_count = 0

    # Saves whether or not the endmember library exists 
    endmember_lib_exist = False

    # Finds all of the ..._class.tif image filess in the directory
    for file in os.listdir(working_dir):
        if (file.endswith(".tif") and not file.endswith("_endmember.tif")):
            src = rasterio.open(os.path.join(working_dir, file))
            band_count = src.meta['count']
            if band_count == 8:
                class_files.append(file)
                class_count += 1

    # Gets the directory of the endmember library text, which should be in
    # the lib folder
    lib_dir = os.path.join(os.path.dirname(sys.path[0]), "lib")
    endmember_lib_dir = os.path.join(lib_dir,
                                     "polar_rock_repo_multispectral_WV02.txt")

    # Sees if the endmember library even exists (True or False)
    endmember_lib_exist = os.path.isfile(endmember_lib_dir)

    # If the class file does not exist...
    if class_count != 0 and endmember_lib_exist:

        # Reads and saves the data in the endmember library
        (name_arr, spect_arr) = endmember_reader(endmember_lib_dir)


        # ====================================================================
        # Initial Unmixing Endmembers

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

        # Gets two arbitrary samples that seem representative of the overall
        # rock spectrum
        rock_unmix_1 = rock_caller(name_arr, spect_arr, "PRR21553", False)
        rock_unmix_2 = rock_caller(name_arr, spect_arr, "PRR12723", False)
        
        # ====================================================================
        
        
        # For each detected _class.tif image file...
        for image in class_files:
            
            # Checks to see if the output file exists
            endmember_exist = os.path.isfile(
                os.path.join(working_dir,
                             image.replace('.tif', '_endmember.tif')))

            # If the endmembers of the image weren't extracted and outputted
            if not endmember_exist:

                print("PROCESSING " + image)
                
                # The file address of the image
                image_dir = os.path.join(working_dir, image)
                
                # Gets the image's band data and dimensions
                (band_data, image_dim, meta) = band_extractor(image_dir)

                # =====================================================
                # 1 - Initial
                
                # Gets the abundances, the endmembers used (in the form
                # of indices), and the pixel and image RMS values
                print("Initial unmixing START")

                init_time1 = time.time()
                
                init_abun = endmember_finder(band_data, atm_spectrum, blueice_spectrum,
                                             snow_spectrum, rock_unmix_1,
                                             rock_unmix_2, zero_member,
                                             zero_member)

                print("Initial unmixing DONE")

                init_time2 = time.time()
                time_printer(init_time1, init_time2)
                
                #outfile = open("abundances_new", "wb")
                #pickle.dump(init_abun, outfile)
                #outfile.close()
               
                #infile = open("abundances_new", "rb")
                #init_abun = pickle.load(infile)
                #init_abun = np.array(init_abun)
                #infile.close()

                #plt.imshow(np.reshape(init_abun[:,2], image_dim))
                #plt.show()
                

                # {ABUNDANCES ORDER}:
                # atm_spectrum, blueice_spectrum, snow_spectrum,
                # rock_unmix_1, rock_unmix_2
                # Creates the presence/absence arrays using the
                # abundances

                
                pa_arr_1 = thresholder(init_abun,
                                       (0.6, 0.4, 0.5, -1, -1, 0, 0))

                # Extracts the presence/absence arrays
                atm_binary = pa_arr_1[0]
                blueice_binary = pa_arr_1[1]
                snow_binary = pa_arr_1[2]
                band_5 = pa_arr_1[3]
                band_6 = pa_arr_1[4]

                # Creates a combined snow+ice presence/absence array
                snowice_binary = blueice_binary + snow_binary
                snowice_binary = np.where(snowice_binary > 1, 1,
                                          snowice_binary)

                # Not snow or ice = geology. Multiplying that by the atm_binary
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
                albedo_arr = np.sum(band_data, axis=1)/8
                dark_binary = np.where(albedo_arr < 0.2, 1, 0)
                water_binary = dark_binary * snowice_binary

                
                # Gets the RMS of each pixel from this initial
                # unmixing
                init_rms = rms_finder(init_abun, band_data,
                                      atm_spectrum, blueice_spectrum,
                                      snow_spectrum, rock_unmix_1,
                                      rock_unmix_2, zero_member,
                                      zero_member)

                #outrms = open("init_rms", "wb")
                #pickle.dump(init_rms, outrms)
                #outrms.close()
               
                #inrms = open("init_rms", "rb")
                #init_rms = pickle.load(inrms)
                #init_rms = np.array(init_rms)
                #inrms.close()

                #plt.imshow(np.reshape(init_rms, image_dim))
                #plt.show()
                #sys.exit()

                # !!!!
                # PLEASE CHANGE THE NUMBER AFTER THE > SIGN TO CHANGE
                # THE THRESHOLD
                # !!!!
                unknown_binary = np.where(init_rms > 0.4, 1, 0)
                
                # Combines the presence/absence binary arrays. Makes sure
                # it stays in a binary format so that the array can be used
                # to extract the not snow/ice/shadowed regions from the
                # image
                pa_binary = atm_binary + blueice_binary + snow_binary
                pa_binary = np.where(pa_binary > 1, 1, pa_binary)

                # Calculates the atmospheric contribution using the abundances
                # and the atmospheric spectrum
                atm_abun = init_abun[:,0]
                atm_contr = np.multiply(atm_abun[:, np.newaxis].astype(np.float32),
                                        atm_spectrum.astype(np.float32))

                # Removes the atmospheric contribution from the data
                no_atm_data = band_data.astype(np.float32) - \
                              atm_contr.astype(np.float32)


                # =====================================================
                # 2 - Rocks
                
                # Reverses the presence/absence of snow/ice/shadow array
                temp_border_arr = border_finder(band_data, image_dim)
                temp_border_arr = np.where(temp_border_arr == -99, 1, 0)
                litrock_binary = np.subtract(np.where(pa_binary == 0, 1, 0),
                                             temp_border_arr)

                #plt.imshow(np.reshape(litrock_binary, image_dim))
                #print("LITROCK")
                #plt.show()
                

                # If all bands of a pixel are non-zero, the pixel is a rock
                lit_geo = np.multiply(no_atm_data, litrock_binary[:, np.newaxis])

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

                print("Rock unmixing START")

                rock_time1 = time.time()

                # Performs the unmixing process using the given rock
                # endmembers
                rock_abun = endmember_finder(lit_geo, more_dol,
                                             less_dol, granite,
                                             sandstone, zero_member,
                                             zero_member, zero_member)

                print("Rock unmixing DONE")
                
                rock_time2 = time.time()
                time_printer(rock_time1, rock_time2)

                
                #outfile = open("rock_abun_new", "wb")
                #pickle.dump(rock_abun, outfile)
                #outfile.close()

                #infile = open("rock_abun_new", "rb")
                #rock_abun = pickle.load(infile)
                #infile.close()

                # {ABUNDANCES ORDER}:
                # more_dol, less_dol, granite, sandstone, zero, zero, zero
                pa_arr_2 = thresholder(rock_abun,
                                       (0.75, 0.1, 0.55, 0.4, 0, 0, 0))

                # Gets the thresholded abundance arrays
                more_dol_binary = pa_arr_2[0]
                less_dol_binary = pa_arr_2[1]
                granite_binary = pa_arr_2[2]
                sandstone_binary = pa_arr_2[3]
                band_12 = pa_arr_2[4]
                band_13 = pa_arr_2[5]
                band_14 = pa_arr_2[6]
                

                # =====================================================
                # 3 - Snow/ice/water
                icewater_data = np.multiply(snowice_binary[:,np.newaxis], no_atm_data)

                print("Snow unmixing START")

                snow_time1 = time.time()
                
                icewater_abun = endmember_finder(icewater_data,
                                                 blueice_spectrum, snow_spectrum,
                                                 zero_member, zero_member,
                                                 zero_member, zero_member)
                print("Snow unmixing END")

                snow_time2 = time.time()
                time_printer(snow_time1, snow_time2)
                
                pa_arr_3 = thresholder(icewater_abun,
                                       (-1, -1, 0, 0, 0, 0))

                band_18 = pa_arr_3[0]
                band_19 = pa_arr_3[1]
                band_20 = pa_arr_3[2]
                band_21 = pa_arr_3[3]
                

                # =====================================================
                # 4 - TBD
                fourth_unmixing = np.multiply(no_atm_data, 0)
                print("Fourth unmixing START")

                fourth_time1 = time.time()
                
                abundances_4 = endmember_finder(fourth_unmixing,
                                                zero_member, zero_member,
                                                zero_member, zero_member,
                                                zero_member, zero_member,
                                                zero_member)
                print("Fourth unmixing END")

                fourth_time2 = time.time()
                time_printer(fourth_time1, fourth_time2)
                
                pa_arr_4 = thresholder(abundances_4,
                                       (0, 0, 0, 0, 0, 0, 0))
                band_22 = pa_arr_4[0]
                band_23 = pa_arr_4[1]
                band_24 = pa_arr_4[2]
                band_25 = pa_arr_4[3]
                band_26 = pa_arr_4[4]
                band_27 = pa_arr_4[5]
                band_28 = pa_arr_4[6]
                

                # =====================================================
                # 5 - TBD
                fifth_unmixing = np.multiply(no_atm_data, 0)
                print("Fifth unmixing START")

                fifth_time1 = time.time()
                
                abundances_5 = endmember_finder(fifth_unmixing,
                                                zero_member, zero_member,
                                                zero_member, zero_member,
                                                zero_member, zero_member,
                                                zero_member)
                print("Fifth unmixing END")

                fifth_time2 = time.time()
                time_printer(fifth_time1, fifth_time2)
                
                pa_arr_5 = thresholder(abundances_5,
                                       (0, 0, 0, 0, 0, 0, 0))
                band_29 = pa_arr_5[0]
                band_30 = pa_arr_5[1]
                band_31 = pa_arr_5[2]
                band_32 = pa_arr_5[3]
                band_33 = pa_arr_5[4]
                band_34 = pa_arr_5[5]
                band_35 = pa_arr_5[6]

                # =====================================================
                # Band 36: RMS

                print("Finding RMS START")

                rms_time1 = time.time()
                
                rms_band = rms_finder(rock_abun, lit_geo,
                                      more_dol, less_dol, granite,
                                      sandstone, zero_member,
                                      zero_member, zero_member)

                print("Finding RMS END")

                rms_time2 = time.time()
                time_printer(rms_time1, rms_time2)
                
                rms_band = np.where(rms_band > 0.4, 1, 0)

                # =====================================================
                # Writing the Output
                
                # Gets the out of image border array. -99 for pixels beyond
                # the border and 0 otherwise
                border_arr = border_finder(band_data, image_dim)

                print("Writing " + image + " START")

                writing_time1 = time.time()
                
                abundance_writer(image_dir, image_dim, meta, border_arr,
                                 shadrock_binary, shadice_binary, snowice_binary,
                                 litrock_binary, band_5, band_6, unknown_binary,
                                 more_dol_binary, less_dol_binary, granite_binary,
                                 sandstone_binary, band_12, band_13, band_14,
                                 snow_binary, blueice_binary, water_binary,
                                 band_18, band_19, band_20, band_21,
                                 band_22, band_23, band_24, band_25,
                                 band_26, band_27, band_28, band_29,
                                 band_30, band_31, band_32, band_33,
                                 band_34, band_35, rms_band)

                print("Writing" + image + " END")

                writing_time2 = time.time()
                time_printer(writing_time1, writing_time2)

            elif endmember_exist:

                print(image.replace('.tif', '_endmember.tif') + ' already exists!')

        # If the endmember library doesn't exist...
        if not endmember_lib_exist:

            # Print a message saying so and don't run the script
            print('The endmember library does not exist!')        


main()

