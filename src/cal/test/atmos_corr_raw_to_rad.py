"""
Programmer: Brian Szutu
Email: bs886@nau.edu

This is a combination of my atmospheric correction script and Brad Spitzbart's
raw to radiance script.

This program serves two purposes:
It is used to take in .txt files of atmospheric spectrographic data
in subfolders in order to calculate the atmospheric correction values needed.
It then uses Spitzbart's script to convert raw images into their radiance .tif forms

The output files will automatically be sent into a folder called Output Files
created by the program in the same subdirectory.
The number of output .txt files will vary with the number of subfolders.

This program is safe to run multiple times in the same directory.

Change(s) from version 1.0 of atmo_correction_radiance.py:
- Allows the user to input a path to the images, allowing the script to be placed
  outside of the directory with the images

Version 1.1
"""

# Imports the ElementTree, rasterio, numpy, math, stats, and os packages
import xml.etree.ElementTree as ET
import rasterio
from spectral import *
import numpy as np
import math
from scipy import stats
import os

# This block reads and writes files
# --------------------------------------------------------------------------

def reader(file):
    """
    Reads ONE file passed into it.

    Parameters:
    file - The file to be read. It's actually a directory of the file

    Return:
    Returns an 2D list containing ALL of the bands and their respective data. Each row represents
    each band
    """
    
    # Creates an empty list to hold all of the band values. Each list
    # inside will correspond to a band
    band_array = []
    
    # Opens the passed in file...
    with open(file, 'r') as file_read:
        # ...splits each integer into their own element in a list...
        lines = [line.strip().replace('\n','').replace('   ', '  ').split('  ') for line in file_read]
        # ...and sets a new list to the 8 bands at the bottom of the .txt.
        band_lines = lines[-8:]
        
    # Closes the file. Generally a good practice
    file_read.close()
    
    # Turns all of the elements into floats. Can't really work with them
    # otherwise
    for i in range(8):
        band_lines[i] = [float(element) for element in band_lines[i]]
        if band_lines[i] == '':
            pass
    
    # Tried to copy only columns 2 and onward of the band data during
    # the coding phase. Gave up and went for the easier but
    # admittedly slower option of just removing the first column
    for i in range(8):
        del band_lines[i][0]
  
    # Sets the band_lines array to the empty band_array to be returned
    band_array = band_lines
    
    return band_array


def writer(file, file_name, output_dir, pass_fail_stat_arr, \
           pass_fail_arr, intercept_arr, set_check):
    """
    Writes into a new file.

    Parameters:
    file               - name of a text file in a subfolder
    file_name          - the name of the new file to be created and/or written into.
                         Same name as the subfolder
    output_dir         - the output directory. Folder specific                 
    pass_fail_stat_arr - a list containing the numbers compared to 3 in order to determine
                         pass/fail status of each band
    pass_fail_arr      - a list containing the pass/fail status of each band
    intercept_arr      - a list containing the atmospheric correction for each band
    set_check          - a string that equals either Pass or Fail. Depends on how many
                         Fails are in pass_fail_arr. Default overall Fail number is 1

    Return:
    None
    """

    # Creates a file to APPEND text to the end of it
    file_write = open(os.path.join(output_dir, file_name+'.txt'), 'a+')

    # Puts the name of the passed in .txt file at the top
    file_write.write(str(file) + ' RESULTS \n')

    # for each tested band...
    for x in range(7):
        # ...write the relevant data
        file_write.write('B' + str(x+1) + ' TEST: ' + str(pass_fail_arr[x])
                         + ', ' + str(pass_fail_stat_arr[x]) + '\n')
        file_write.write('B' + str(x+1) + ' CORRECTION: '
                         + str(intercept_arr[x]) + '\n')

    # Writes the overall pass/fail status of the bands
    file_write.write('OVERALL: ' + str(set_check) + '\n \n')
    # Closes the file
    file_write.close()

# --------------------------------------------------------------------------

# This block does the calculations for the atmospheric corrections
# --------------------------------------------------------------------------


def tester_caller(band_array, intercept_arr, slope_arr):
    """
    The main function of the testing part of the program. Calls tester and pass_fail_checker.
    Returns a list of numbers, each corresponding to each band, to compare to 3.

    Parameters:
    band_array    - a 2D list containing all of the band data for each band
    intercept_arr - a list containing the atmospheric correction for each band
    slope_arr     - a list containing the slope for each band compared to the last band

    Return:
    Returns two lists. pass_fail_stat_arr contains the numbers compared to 3 to determine the
    pass/fail statuses of each band while pass_fail_arr contains the pass/fail statuses of each
    band.
    """
    
    # Empy lists to be iterated into with the numbers being compared to 3 and the
    # pass/fail statuses, respectively.
    pass_fail_stat_arr = []
    pass_fail_arr = []

    # For each band...
    for band in range(7):
        # Append to the appropriate list the number to be compared to 3
        pass_fail_stat_arr.append(
            tester(band_array, intercept_arr, slope_arr, band))
        # Append to the appropriate list pass/fail status of the number above
        pass_fail_arr.append(
            pass_fail_checker(pass_fail_stat_arr[band]))
        
    return pass_fail_stat_arr, pass_fail_arr

def inter_slope(band_array):
    """
    Used to calculate the intercepts and slopes of each band vs the last band. Calls the other
    functions in this block

    Parameters:
    band_array - a 2D list containing all of the data for each band in a .txt file

    Return:
    Returns two lists containing the intercepts and slopes of each band vs the last band
    """
    # Initializes empty lists of length 7 for each band. Kinda wish I
    # could've done this using append. 
    intercept_arr = [0, 0, 0, 0, 0, 0, 0]
    slope_arr = [0, 0, 0, 0, 0, 0, 0]
    
    # For each band...
    for band in range(7):
        # Iterate into the slope and intercept lists using linregress. The other values are
        # useless for now.
        (slope_arr[band], intercept_arr[band], r_value, p_value, std_err) = \
                          stats.linregress(band_array[7], band_array[band])
        
    return intercept_arr, slope_arr

def tester(band_array, intercept_arr, slope_arr, n):
    """
    Calculates the number to be compared to 3 in order to determine the pass/fail status of a band

    Parameters: 
    band_array    - a 2D list containing all of the data for each band in a .txt file
    intercept_arr - a list containing the intercepts between each band vs the last band
    slope_arr     - a list containing the slopes between each band vs the last band
    n             - the n + 1 band to have the value compared to 3 to be calculated for

    Return:
    A single float to be compared to 3
    """

    # Initializes a variable to hold a total sum
    calc_sum = 0
    # For each element within a certain band...
    for element_n in range(len(band_array[n])):
        # Let an element be defined as such within the band array.
        element = band_array[n][element_n]
        
        # If the element is greater than 0.0000001...
        if element > 0.0000001:
            # Let the variable element_check equal 1.
            element_check = 1
        # Else...
        else:
            # Let it equal 0.
            element_check = 0

        # Doing the specified calculation for each element...
        element_calc = ((element - ((slope_arr[n] * band_array[-1][element_n]) \
                                  + (intercept_arr[n])))**2) * element_check
        # Adds the calculated number to the sum holder
        calc_sum += element_calc

    # Does the calculation to obtain the number to compare to 3.
    pass_fail_num = calc_sum/len(band_array[n])
    
    return pass_fail_num

def pass_fail_checker(pass_fail_num):
    """
    Compares a number to 3.

    Parameters:
    pass_fail_num - a float to be compared to 3

    Return:
    Returns Pass or Fail depending on how the float compares to 3
    """
    if pass_fail_num < 3:
        return 'Pass'
    else:
        return 'Fail'


def dataset_checker(pass_fail_arr, pass_fail_stat_arr):
    """
    Checks if any of the bands out of the first seven 'Fail' the test.
    If any a select number of bands do, then the whole data set fails.

    Parameters:
    pass_fail_arr - a list containing the pass/fail status of each band
    pass_fail_stat_arr - a list containing the numbers compared to 3

    Return:
    A string being either Pass or Fail depending on how many Fails there are in
    pass_fail_arr
    """
    # Variable used to keep track of how many Fails there are
    fail_n = 0
    # Finds out how many fails are in the data set. If the 
    for i in range(len(pass_fail_arr)):
        # Any band with a comparison number less than five may still be
        # passable
        if pass_fail_arr[i] == 'Fail' and pass_fail_stat_arr[i] > 5:
            fail_n += 1
            
    # Change the number here to specify how many fails is the bare minimum
    # for the data set to Fail. 1 is my set default.
    if fail_n >= 4:
        return 'Fail'
    else:
        return 'Pass'
# --------------------------------------------------------------------------

# This block calculates averages
# --------------------------------------------------------------------------

def avg_intercept(total_intercept_arr, txt_count):
    """
    Calculates the AVERAGE ATMOSPHERIC CORRECTION for each band in a subfolder

    Parameters:
    total_intercept_arr - a 2D list containing the atmospheric corrections for each band in
                          each .txt file
    txt_count           - the number of .txt files in the subfolder

    Return:
    Returns a list containing the average atmospheric correction for each band in a subfolder
    """
    # Initializes 7 variables to hold the sum of each of their respective band
    # intercepts
    (band1_sum, band2_sum, band3_sum, band4_sum, band5_sum, band6_sum, band7_sum) = \
                0, 0, 0, 0, 0, 0, 0
    # For loop does the summing
    for i in range(len(total_intercept_arr)):
        band1_sum += total_intercept_arr[i][0]
        band2_sum += total_intercept_arr[i][1]
        band3_sum += total_intercept_arr[i][2]
        band4_sum += total_intercept_arr[i][3]
        band5_sum += total_intercept_arr[i][4]
        band6_sum += total_intercept_arr[i][5]
        band7_sum += total_intercept_arr[i][6]

    # Computes the average intercept.
    band1_avg = band1_sum / txt_count
    band2_avg = band2_sum / txt_count
    band3_avg = band3_sum / txt_count
    band4_avg = band4_sum / txt_count
    band5_avg = band5_sum / txt_count
    band6_avg = band6_sum / txt_count
    band7_avg = band7_sum / txt_count

    # Puts the avg intercept data into an array.
    band_avg_arr = [band1_avg, band2_avg, band3_avg, band4_avg, \
                    band5_avg, band6_avg, band7_avg]
    
    return band_avg_arr

def avg_writer(file_name, output_dir, band_avg_arr):
    """
    Writes the avg intercept to the document at the end

    Parameters:
    file_name    - the name of the file to be appended to. In the same loop, it should be the
                   same name as the one mentioned way above in the writer() function
    output_dir   - the output directory. File specific
    band_avg_arr - a list containing the average atmospheric correction for each band in a
                   subfolder

    Return:
    None
    """
    file_write = open(os.path.join(output_dir, file_name+'.txt'), 'a+')
    file_write.write('ATMOSPHERIC CORRECTION AVG: \n')
    for x in range(7):
        file_write.write('BAND' + str(x+1) + ' AVG: '
                         + str(band_avg_arr[x]) + '\n')
    file_write.close()

# --------------------------------------------------------------------------

def main():
    """
    Main function. Responsible for having all folders be searched and all
    files be read. Calls the other big functions

    Parameters:
    None

    Return:
    None
    """

    # Prints the directory the script is in
    print("Current directory: " + os.path.dirname(os.path.abspath(__file__)))
    
    # Finds the current directory and appends a new folder to be made
    working_dir = input("Please input the FULL path to the directory with the images: \n")

    # Will keep asking the user to input a valid path. Use CTRL + C to manually terminate
    # the program
    while (not os.path.exists(working_dir)):
        working_dir = input("That path does not exist. Please input a path: \n")

    # Empty list holds all of the relevent folders in the directory
    folders = []

    # for each file/folder in the directory...
    for file in os.listdir(working_dir):
        # if there is a . or the something is named Output Files...
        if "." in file or file == 'Output Files':
            # ...Don't do anything with them
            continue
        else:
            # Else, append the thing being looked at into the folders list
            folders.append(file)


    # for every single folder in the folders list...
    for folder in folders:
        
        # List used to hold the names of all the .txt files in a folder.
        txt_files = []
        # Used to count the number of .txt files
        txt_count = 0

        # Holds the .xml file used in the raw to radiance conversion
        xml_file = ''
        # Counts the number of .xml files in the subfolder
        xml_count = 0

        # Holds the .tif files to be converted from raw to rad
        tif_files = []
        # Counts the number of .tif files
        tif_count = 0

        # Makes a temporary directory to the folder to work with the text files inside
        folder_dir = os.path.join(working_dir, folder)

        # For each file in the current directory...
        for file in os.listdir(folder_dir):
            # If it is a .txt file...
            if file.endswith('.txt'):
                # Append the name of the file to the .txt tracking list
                txt_files.append(file)
                # and add 1 to the .txt count
                txt_count += 1
            # If it is a .tif file, NOT a rad.tif file...
            elif (file.endswith('.tif') and not file.endswith('rad.tif')):
                # Append the name of the file to the .tif tracking list
                tif_files.append(file)
                # and add 1 to the .tif count
                tif_count += 1
            # if it is a .xml file...
            elif file.endswith('.xml'):
                # Save the name of the file
                xml_file = file
                print(xml_file)
                # and add 1 to the .xml count
                xml_count += 1
            else:
                continue
        
        # Creates the Output Files folder if it doesn't exist in the image subfolder already
        output_dir = os.path.join(folder_dir, 'Output Files')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initializes a list. Holds lists of intercepts, with each nested list corresponding
        # to each file.
        total_intercept_arr = []

        # Checks to see if a .txt file of the same name as a subfolder
        # already exists. Outputs True or False
        txt_file_exists = os.path.isfile(os.path.join(output_dir, folder+'.txt'))

        # If the output file does NOT exist AND the .txt file count > 0...
        if not txt_file_exists and txt_count > 0:

            # This loop does the heavy lifting. For each .txt file within the folder...
            for f in txt_files:

                # Makes a temporary directory to a text file in a folder
                text_dir = os.path.join(folder_dir, f)
                
                # Passes the file into the reader function and set the output list to something
                band_array = reader(text_dir)
                # Passes the outputted list from above into inter_slope to calculate
                # the intercepts and slopes
                (intercept_arr, slope_arr) = inter_slope(band_array)
                
                # Appends to the empty initialized list slightly above the intercepts of the
                # current file
                total_intercept_arr.append(intercept_arr)
                
                # Passes the above the above three outputs into the test_caller() function
                # to obtain the numbers to compare to 3 and the pass/fail statuses.
                (pass_fail_stat_arr, pass_fail_arr) = \
                                    tester_caller(band_array, intercept_arr, slope_arr)
                # Checks the pass/fail statuses of each band. Will return 'Fail' if
                # at least one 'Fail' exists.
                set_check = dataset_checker(pass_fail_arr, pass_fail_stat_arr)
                
                # Calls the writer() function. Does most of the file writing.
                writer(f, folder, output_dir, pass_fail_stat_arr, pass_fail_arr, \
                       intercept_arr, set_check)

            # Outside of the loop. Calculates the avg intercepts
            # between all of the files
            band_avg_arr = avg_intercept(total_intercept_arr, txt_count)
            # Writes the avg intercepts into the document.
            avg_writer(folder, output_dir, band_avg_arr)
            # Prints a message that the file was successfully created
            print(folder+'.txt was successfully created!')        

        # If the file already exists...
        elif txt_file_exists:
            # Print that the .txt already exists
            print(folder+'.txt already exists!')        
        # If the .txt count is 0...
        elif txt_count == 0:
            # Print that there are no .txt files to analyze
            print('There are no .txt files to analyze in ' + folder + '!')
        else:
            continue

    # This block is the beginning of the modified Spitzbart script
    #////////////////////////////////////////////////

        # If there are .xml and .tif files...
        if xml_count != 0 and tif_count != 0:
            # For each .tif file in the folder...
            for f in tif_files:

                # Sees if an output file for the raw image being analyzed exists...
                rad_file_exists = os.path.isfile(os.path.join(output_dir, f+'_rad.tif'))

                # If the rad.tif file doesn't exist, use Spitzbart's script
                if not rad_file_exists:
                    tree=ET.parse(os.path.join(working_dir, folder, xml_file))
                    root = tree.getroot()

                    # collect image metadata
                    bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']

                    src = rasterio.open(os.path.join(working_dir, folder, f))
                    meta = src.meta
                    # Update meta to float64
                    meta.update(dtype = rasterio.float64)
                    with rasterio.open(os.path.join(output_dir, f+'_rad.tif'), 'w', **meta) as dst:
                        i = 0
                        for band in bands:
                            rt = root[1][2].find(band)
                            # collect band metadata
                            abscalfactor = float(rt.find('ABSCALFACTOR').text)
                            effbandwidth = float(rt.find('EFFECTIVEBANDWIDTH').text)
                            print(bands[i])
                            print(src.read(i+1)[0,0]," ",abscalfactor," ",effbandwidth)
                            ### Read each layer and write it to stack
                            rad = src.read(i+1)*abscalfactor/effbandwidth
                            print(rad[0,0],rad.dtype)
                            dst.write_band(i+1, rad)
                            i += 1
                    dst.close()
                    print(f + ' is read.')

                # If the rad.tif file already exists, print out a message saying so
                elif rad_file_exists:
                    print(f+'_rad.tif already exists!')
        # If there are no .xml files, print out a message saying so
        elif xml_count == 0:
            print('There are no .xml files in ' + folder + '!')
        # If there are no raw .tif files to be analyzed, print out a message saying so
        elif tif_count == 0:
            print('There are no .tif files in ' + folder + '!')
        else:
            continue
    #////////////////////////////////////////////////

    # Program felt empty without a line saying that there was no syntax error.
    print('All new files successfully created! Look in Output Files for the results.')

# Calls the main() function
main()
