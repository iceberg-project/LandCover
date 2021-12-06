#!/usr/bin/env python

from radical.entk import Pipeline, Stage, Task, AppManager
import rasterio
import os
import argparse
import numpy as np

#export RADICAL_PILOT_DBURL=mongodb://bszutu:djnxUDMB4Gz3aXcu@95.217.193.116:27017/bszutu
#export RADICAL_PILOT_DBURL=mongodb://localhost:27017/db
#export RADICAL_ENTK_VERBOSE="DEBUG"
#export RADICAL_LOG_LVL="DEBUG"

#hostname = os.environ.get('RMQ_HOSTNAME', 'localhost')
# RADICAL Test Machine
hostname = "95.217.193.116"
port = int(os.environ.get('RMQ_PORT', 5672))
#username = os.environ.get('RMQ_USERNAME')
username = "bszutu"
#username = "guest"
#password = os.environ.get('RMQ_PASSWORD')
password = "djnxUDMB4Gz3aXcu"
#password = "guest"

image_list = []


#DatasetWriter not able to be passed in

def args_parser():
    """
    Reads the image directory passed in from console. 
    
    Parameters:
    None
    
    Return:
    Returns a directory as a string that has the images inside of it to
    be analyzed
    """

    # Creates an ArgumentParser object to hold the console input
    parser = argparse.ArgumentParser()
    
    # Adds an argument to the parser created above. Holds the
    # inputted directory as a string
    parser.add_argument('-ip', '--input_dir', type=str,
                        help='The directory containing the images.')

    # Returns the passed in directory
    return (parser.parse_args().input_dir)


def generate_pipeline(working_dir, image):
    """
    Generates a pipeline for an image in the specified directory

    Parameters:
    working_dir - the specified directory
    image       - the image name

    Return:
    Returns the completed pipeline for a single image
    """

    """
    # The path to the passed in image
    image_dir = os.path.join(working_dir, image)
    
    # Extracts the metadata of the passed in image
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

    # Responsible for the image writing. Passed onto the tasks
    dst = rasterio.open(image_dir.replace(".tif", "_endmember.tif"), 'w', **meta)
    # Appends the dst object to a global list to eventually close after writing
    # (this is a pass-by-reference action)
    dst_list.append(dst)
    """

    # Makes a Pipeline object
    p = Pipeline()

    # Makes a Stage object (the first of two)
    s1 = Stage()

    # Makes a Task object (the only task in the first stage)
    t1 = Task()
    # Name of the task
    t1.name = "unmix1"
    # Executes the corresponding Python script to extract some key spectral endmembers
    t1.executable = "python unmix1.py"
    # Passes in arguments to the script
    t1.arguments = [os.path.join(working_dir, image)]
    # Puts the outputted arrays into text files for further use
    t1.download_output_data = ['border_arr.txt', 'image_dim.txt',
                               'no_atm_data.txt', 'pa_binary.txt',
                               'shadrock_binary', 'shadice_binary',
                               'snowice_binary']

    # Adds the task to the stage and the stage to the pipeline
    s1.add_tasks(t1)
    p.add_stages(s1)

    # Creates the second Stage object
    s2 = Stage()

    # Creates four tasks, each with fairly similar roles in extracting spectral endmembers
    # from the passed in image
    for i in range(2,6):
        t2 = Task()
        # Name of the task; depends on the loop iteration
        t2.name = "unmix"+str(i)
        # Executes the corresponding Python script
        t2.executable = "python unmix"+str(i)+".py"
        # Passes in the output from the task in the previous stage
        t2.arguments = ['no_atm_data.txt', 'pa_binary.txt']
        # Extracts the data from the above
        t2.copy_input_data = ['$Pipeline_%s_Stage_%s_Task_%s/border_arr.txt' % (p.name, s1.name, t1.name),
                              '$Pipeline_%s_Stage_%s_Task_%s/no_atm_data.txt' % (p.name, s1.name, t1.name),
                              '$Pipeline_%s_Stage_%s_Task_%s/pa_binary.txt' % (p.name, s1.name, t1.name)]
        if i == 2:
            t2.download_output_data = ['lit_geo.txt', 'norm_const_rock.txt',
                                       'rock_abun.txt', 'litrock_binary.txt',
                                       'band_5.txt', 'band_6.txt',
                                       'unknown_binary.txt', 'more_dol_binary.txt',
                                       'less_dol_binary.txt', 'granite_binary.txt',
                                       'sandstone_binary.txt', 'band_12.txt',
                                       'band_13.txt', 'band_14.txt']
        elif i == 3:
            t2.download_output_data = ['snow_binary.txt', 'blueice_binary.txt',
                                       'water_binary.txt', 'band_18.txt',
                                       'band_19.txt', 'band_20.txt',
                                       'band_21.txt']
        elif i == 4:
            t2.download_output_data = ['band_22.txt', 'band_23.txt',
                                       'band_24.txt', 'band_25.txt',
                                       'band_26.txt', 'band_27.txt',
                                       'band_28.txt']
        elif i == 5:
            t2.download_output_data = ['band_29.txt', 'band_30.txt',
                                       'band_31.txt', 'band_32.txt',
                                       'band_33.txt', 'band_34.txt',
                                       'band_35.txt']

            
        # Adds the tasks to the second stage
        s2.add_tasks(t2)

    # Adds the second stage to the pipeline
    p.add_stages(s2)

    # Initializes the third and final stage
    s3 = Stage()

    # Task writes the bands to an output image
    t3 = Task()

    t3.name = "writer"

    t3.arguments = [working_dir, image, 'border_arr.txt', 'lit_geo.txt',
                    'rock_abun.txt', 'norm_const_rock.txt',
                    'shadrock_binary', 'shadice_binary', 'snowice_binary',
                    'litrock_binary.txt', 'band_5.txt', 'band_6.txt',
                    'unknown_binary.txt', 'more_dol_binary.txt',
                    'less_dol_binary.txt', 'granite_binary.txt',
                    'sandstone_binary.txt', 'band_12.txt',
                    'band_13.txt', 'band_14.txt',
                    'snow_binary.txt', 'blueice_binary.txt',
                    'water_binary.txt', 'band_18.txt',
                    'band_19.txt', 'band_20.txt', 'band_21.txt', 'band_22.txt',
                    'band_23.txt', 'band_24.txt', 'band_25.txt', 'band_26.txt',
                    'band_27.txt', 'band_28.txt', 'band_29.txt', 'band_30.txt',
                    'band_31.txt', 'band_32.txt', 'band_33.txt', 'band_34.txt',
                    'band_35.txt']

    t3.executable = "python writer.py"

    # Saves the "path" to each task's outputted text files
    input_data_arr = []

    # Loop for getting the appropriate text files of the inputs
    for i in range(2, len(t3.arguments)):
        task_name = ""
        stage_name = s2.name
        if i > 33:
            task_name = "unmix5"
        elif i > 26:
            task_name = "unmix4"
        elif i > 19:
            task_name = "unmix3"
        elif i > 8:
            task_name = "unmix2"
        elif i > 3:
            task_name = "unmix1"
            stage_name = s1.name

        # Appends the "path" of the specific text file
        input_data_arr.append(('$Pipeline_%s_Stage_%s_Task_%s/' % (p.name, stage_name, task_name)) +
                              str(t3.arguments[i]))

    # Copies the data in the text files to the inputs
    t3.copy_input_data = input_data_arr

    # Adds the final task to the final stage
    s3.add_tasks(t3)

    # Adds the final stage to the pipeline
    p.add_stages(s3)

    # Returns the pipeline
    return p



if __name__ == '__main__':
    """
    Main
    """
    # Holds each image's pipeline
    pipelines = []

    # Gets the working directory from the console
    working_dir = args_parser()
    
    # Finds all of the image filess in the directory
    for file in os.listdir(working_dir):
        # Makes sure that the images aren't already processed
        if (file.endswith(".tif") and
            file.endswith("_endmember.tif") not in os.listdir(working_dir)):
            # Pulls the number of bands in the current image
            src = rasterio.open(os.path.join(working_dir, file))
            band_count = src.meta['count']
            src.close()
            # Only uses images that have eight bands
            if band_count == 8:
                image_list.append(file)

    # For each image, generate a pipeline
    for image in image_list:
        pipelines.append(generate_pipeline(working_dir, image))

    
    appman = AppManager(hostname=hostname, port=port, username=username, password=password)

    res_dict = {'resource':'local.localhost',
                'walltime':10,
                'cpus':1}

    appman.resource_desc = res_dict
    appman.workflow = set(pipelines)
    appman.run()

