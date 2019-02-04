import xml.etree.ElementTree as ET
import rasterio
import numpy as np
import math
import os

"""
CURRENT ALGORITHM DOESN'T WORK WITH ATMCORR.TIF FILES
"""

# This is a large dictionary of the Earth-Sun distance in AU.
# Goes by date. Hopefully nothing was misinputted
date_distance = {'JAN01':0.98331,'JAN02':0.98330,'JAN03':0.98330,'JAN04':0.98330,
                 'JAN05':0.98330,'JAN06':0.98332,'JAN07':0.98333,'JAN08':0.98335,
                 'JAN09':0.98338,'JAN10':0.98341,'JAN11':0.98345,'JAN12':0.98349,
                 'JAN13':0.98354,'JAN14':0.98359,'JAN15':0.98365,'JAN16':0.98371,
                 'JAN17':0.98378,'JAN18':0.98385,'JAN19':0.98393,'JAN20':0.98401,
                 'JAN21':0.98410,'JAN22':0.98419,'JAN23':0.98428,'JAN24':0.98439,
                 'JAN25':0.98449,'JAN26':0.98460,'JAN27':0.98472,'JAN28':0.98484,
                 'JAN29':0.98496,'JAN30':0.98509,'JAN31':0.98523,
                 'FEB01':0.98536,'FEB02':0.98551,'FEB03':0.98565,'FEB04':0.98580,
                 'FEB05':0.98596,'FEB06':0.98612,'FEB07':0.98628,'FEB08':0.98645,
                 'FEB09':0.98662,'FEB10':0.98680,'FEB11':0.98698,'FEB12':0.98717,
                 'FEB13':0.98735,'FEB14':0.98755,'FEB15':0.98774,'FEB16':0.98794,
                 'FEB17':0.98814,'FEB18':0.98835,'FEB19':0.98856,'FEB20':0.98877,
                 'FEB21':0.98899,'FEB22':0.98921,'FEB23':0.98944,'FEB24':0.98966,
                 'FEB25':0.98989,'FEB26':0.99012,'FEB27':0.99036,'FEB28':0.99060,
                 'FEB29':0.99084,
                 'MAR01':0.99084,'MAR02':0.99108,'MAR03':0.99133,'MAR04':0.99158,
                 'MAR05':0.99183,'MAR06':0.99208,'MAR07':0.99234,'MAR08':0.99260,
                 'MAR09':0.99252,'MAR10':0.99312,'MAR11':0.99339,'MAR12':0.99365,
                 'MAR13':0.99392,'MAR14':0.99419,'MAR15':0.99446,'MAR16':0.99474,
                 'MAR17':0.99501,'MAR18':0.99529,'MAR19':0.99556,'MAR20':0.99584,
                 'MAR21':0.99612,'MAR22':0.99640,'MAR23':0.99669,'MAR24':0.99697,
                 'MAR25':0.99725,'MAR26':0.99754,'MAR27':0.99782,'MAR28':0.99811,
                 'MAR29':0.99840,'MAR30':0.99868,'MAR31':0.99897,
                 'APR01':0.99926,'APR02':0.99954,'APR03':0.99983,'APR04':1.00012,
                 'APR05':1.00041,'APR06':1.00069,'APR07':1.00098,'APR08':1.00127,
                 'APR09':1.00155,'APR10':1.00184,'APR11':1.00212,'APR12':1.00240,
                 'APR13':1.00269,'APR14':1.00297,'APR15':1.00325,'APR16':1.00353,
                 'APR17':1.00381,'APR18':1.00409,'APR19':1.00437,'APR20':1.00464,
                 'APR21':1.00492,'APR22':1.00519,'APR23':1.00546,'APR24':1.00573,
                 'APR25':1.00600,'APR26':1.00626,'APR27':1.00653,'APR28':1.00679,
                 'APR29':1.00705,'APR30':1.00731,
                 'MAY01':1.00756,'MAY02':1.00781,'MAY03':1.00806,'MAY04':1.00831,
                 'MAY05':1.00856,'MAY06':1.00880,'MAY07':1.00904,'MAY08':1.00928,
                 'MAY09':1.00952,'MAY10':1.00975,'MAY11':1.00998,'MAY12':1.01020,
                 'MAY13':1.01043,'MAY14':1.01065,'MAY15':1.01087,'MAY16':1.01108,
                 'MAY17':1.01129,'MAY18':1.01150,'MAY19':1.01170,'MAY20':1.01191,
                 'MAY21':1.01210,'MAY22':1.01230,'MAY23':1.01249,'MAY24':1.01267,
                 'MAY25':1.01286,'MAY26':1.01304,'MAY27':1.01321,'MAY28':1.01338,
                 'MAY29':1.01355,'MAY30':1.01371,'MAY31':1.01387,
                 'JUN01':1.01403,'JUN02':1.01418,'JUN03':1.01433,'JUN04':1.01447,
                 'JUN05':1.01461,'JUN06':1.01475,'JUN07':1.01488,'JUN08':1.01500,
                 'JUN09':1.01513,'JUN10':1.01524,'JUN11':1.01536,'JUN12':1.01547,
                 'JUN13':1.01557,'JUN14':1.01567,'JUN15':1.01577,'JUN16':1.01586,
                 'JUN17':1.01595,'JUN18':1.01603,'JUN19':1.01610,'JUN20':1.01618,
                 'JUN21':1.01625,'JUN22':1.01631,'JUN23':1.01637,'JUN24':1.01642,
                 'JUN25':1.01647,'JUN26':1.01652,'JUN27':1.01656,'JUN28':1.01659,
                 'JUN29':1.01662,'JUN30':1.01665,
                 'JUL01':1.01667,'JUL02':1.01668,'JUL03':1.01670,'JUL04':1.01670,
                 'JUL05':1.01670,'JUL06':1.01670,'JUL07':1.01669,'JUL08':1.01668,
                 'JUL09':1.01666,'JUL10':1.01664,'JUL11':1.01661,'JUL12':1.01658,
                 'JUL13':1.01655,'JUL14':1.01650,'JUL15':1.01646,'JUL16':1.01641,
                 'JUL17':1.01635,'JUL18':1.01629,'JUL19':1.01623,'JUL20':1.01616,
                 'JUL21':1.01609,'JUL22':1.01601,'JUL23':1.01592,'JUL24':1.01584,
                 'JUL25':1.01575,'JUL26':1.01565,'JUL27':1.01555,'JUL28':1.01544,
                 'JUL29':1.01533,'JUL30':1.01522,'JUL31':1.01510,
                 'AUG01':1.01497,'AUG02':1.01485,'AUG03':1.01471,'AUG04':1.01458,
                 'AUG05':1.01444,'AUG06':1.01429,'AUG07':1.01414,'AUG08':1.01399,
                 'AUG09':1.01383,'AUG10':1.01367,'AUG11':1.01351,'AUG12':1.01334,
                 'AUG13':1.01317,'AUG14':1.01299,'AUG15':1.01281,'AUG16':1.01263,
                 'AUG17':1.01244,'AUG18':1.01225,'AUG19':1.01205,'AUG20':1.01186,
                 'AUG21':1.01165,'AUG22':1.01145,'AUG23':1.01124,'AUG24':1.01103,
                 'AUG25':1.01081,'AUG26':1.01060,'AUG27':1.01037,'AUG28':1.01015,
                 'AUG29':1.00992,'AUG30':1.00969,'AUG31':1.00946,
                 'SEP01':1.00922,'SEP02':1.00898,'SEP03':1.00874,'SEP04':1.00850,
                 'SEP05':1.00825,'SEP06':1.00800,'SEP07':1.00775,'SEP08':1.00750,
                 'SEP09':1.00724,'SEP10':1.00698,'SEP11':1.00672,'SEP12':1.00646,
                 'SEP13':1.00620,'SEP14':1.00593,'SEP15':1.00566,'SEP16':1.00539,
                 'SEP17':1.00512,'SEP18':1.00485,'SEP19':1.00457,'SEP20':1.00430,
                 'SEP21':1.00402,'SEP22':1.00374,'SEP23':1.00346,'SEP24':1.00318,
                 'SEP25':1.00290,'SEP26':1.00262,'SEP27':1.00234,'SEP28':1.00205,
                 'SEP29':1.00177,'SEP30':1.00148,
                 'OCT01':1.00119,'OCT02':1.00091,'OCT03':1.00062,'OCT04':1.00033,
                 'OCT05':1.00005,'OCT06':0.99976,'OCT07':0.99947,'OCT08':0.99918,
                 'OCT09':0.99890,'OCT10':0.99861,'OCT11':0.99832,'OCT12':0.99804,
                 'OCT13':0.99775,'OCT14':0.99747,'OCT15':0.99718,'OCT16':0.99690,
                 'OCT17':0.99662,'OCT18':0.99634,'OCT19':0.99605,'OCT20':0.99577,
                 'OCT21':0.99550,'OCT22':0.99522,'OCT23':0.99494,'OCT24':0.99467,
                 'OCT25':0.99440,'OCT26':0.99412,'OCT27':0.99385,'OCT28':0.99359,
                 'OCT29':0.99332,'OCT30':0.99306,'OCT31':0.99279,
                 'NOV01':0.99253,'NOV02':0.99228,'NOV03':0.99202,'NOV04':0.99177,
                 'NOV05':0.99152,'NOV06':0.99127,'NOV07':0.99102,'NOV08':0.99078,
                 'NOV09':0.99054,'NOV10':0.99030,'NOV11':0.99007,'NOV12':0.98983,
                 'NOV13':0.98961,'NOV14':0.98938,'NOV15':0.98916,'NOV16':0.98894,
                 'NOV17':0.98872,'NOV18':0.98851,'NOV19':0.98830,'NOV20':0.98809,
                 'NOV21':0.98789,'NOV22':0.98769,'NOV23':0.98750,'NOV24':0.98731,
                 'NOV25':0.98712,'NOV26':0.98694,'NOV27':0.98676,'NOV28':0.98658,
                 'NOV29':0.98641,'NOV30':0.98624,
                 'DEC01':0.98608,'DEC02':0.98592,'DEC03':0.98577,'DEC04':0.98562,
                 'DEC05':0.98547,'DEC06':0.98533,'DEC07':0.98519,'DEC08':0.98506,
                 'DEC09':0.98493,'DEC10':0.98481,'DEC11':0.98469,'DEC12':0.98457,
                 'DEC13':0.98446,'DEC14':0.98436,'DEC15':0.98426,'DEC16':0.98416,
                 'DEC17':0.98407,'DEC18':0.98399,'DEC19':0.98391,'DEC20':0.98383,
                 'DEC21':0.98376,'DEC22':0.98370,'DEC23':0.98363,'DEC24':0.98358,
                 'DEC25':0.98353,'DEC26':0.98348,'DEC27':0.98344,'DEC28':0.98340,
                 'DEC29':0.98337,'DEC30':0.98335,'DEC31':0.98333,
                 }

#///////////
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

for folder in folders:
    xml_file = ''
    xml_count = 0

    atmcorr_files = []
    atmcorr_count = 0

    folder_dir = os.path.join(working_dir, folder)

    for file in os.listdir(folder_dir):
        if file.endswith('.xml'):
            xml_file = file
            xml_count += 1
        elif file.endswith('atmcorr.tif'):
            atmcorr_files.append(file)
            atmcorr_count += 1
        else:
            continue

    output_dir = os.path.join(folder_dir, 'Output Files')
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    if xml_count!= 0 and atmcorr_count != 0:
        for f2 in atmcorr_files:
            refl_file_exists = os.path.isfile(os.path.join(output_dir, f2+'_atmcorr_refl.tif'))

            if not refl_file_exists:
#///////////
                date = folder[2:7]

                d = date_distance[date]

                tree=ET.parse(os.path.join(working_dir, folder, xml_file))
                root = tree.getroot()

                # collect image metadata
                bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']
                rt = root[1][2].find('IMAGE')
                satid = rt.find('SATID').text
                meansunel = rt.find('MEANSUNEL').text

                if satid == 'WV02':
                    esun = [1758.2229,1974.2416,1856.4104,1738.4791,1559.4555,1342.0695,1069.7302,861.2866] # WV02
                if satid == 'WV03':
                    esun = [1803.9109,1982.4485,1857.1232,1746.5947,1556.9730,1340.6822,1072.5267,871.1058] # WV03

                src = rasterio.open(os.path.join(working_dir, folder, f2))
                meta = src.meta
                # Update meta to float64
                meta.update(dtype = rasterio.float64)
                with rasterio.open(os.path.join(output_dir, f2+'_refl.tif', 'w', **meta)) as dst:
                    i = 0
                    for band in bands:
                        rt = root[1][2].find(band)
                        # collect band metadata
                        abscalfactor = float(rt.find('ABSCALFACTOR').text)
                        effbandwidth = float(rt.find('EFFECTIVEBANDWIDTH').text)
                        print(bands[i])
                        print(src.read(i+1)[0,0]," ",abscalfactor," ",effbandwidth)
                        ### Read each layer and write it to stack
                        rad = src.read(i+1)*pi*(d^2)/(esun[i]*sin(meansunel))
                        print(rad[0,0],rad.dtype)
                        dst.write_band(i+1, rad)
                        i += 1

