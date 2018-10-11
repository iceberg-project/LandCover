import xml.etree.ElementTree as ET
import rasterio
from spectral import *
import numpy as np
import math

tree=ET.parse('orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031.xml')
root = tree.getroot()

# collect image metadata
bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']
rt = root[1][2].find('IMAGE')
satid = rt.find('SATID').text
meansunel = rt.find('MEANSUNEL').text
tlctime = rt.find('TLCTIME').text

if satid == 'WV02':
  esun = [1758.2229,1974.2416,1856.4104,1738.4791,1559.4555,1342.0695,1069.7302,861.2866] # WV02
if satid == 'WV03':
  esun = [1803.9109,1982.4485,1857.1232,1746.5947,1556.9730,1340.6822,1072.5267,871.1058] # WV03

#print(esun)

# collect band metadata
abscalfactor = [1] * len(bands)
effbandwidth = [1] * len(bands)

i = 0
for band in bands:
  rt = root[1][2].find(band)
  abscalfactor[i] = float(rt.find('ABSCALFACTOR').text)
  effbandwidth[i] = float(rt.find('EFFECTIVEBANDWIDTH').text)
  print(bands[i])
  i += 1
#print(abscalfactor)

# setup tiling
src = rasterio.open('In/orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031.tif')
src_height = src.shape[0]
src_width = src.shape[1]
overlap = 0
target_height = 400
target_width = 400

xsize = math.floor(src_width/target_width)
ysize = math.floor(src_height/target_height)
ang_arr = np.empty((xsize,ysize))
var_arr = np.empty((xsize,ysize))
vband_arr = np.empty((xsize,ysize))

# start tiling
for ti in range(0, src_height - overlap, target_height - overlap):
  for tj in range(0, src_width - overlap, target_width - overlap):
    print(ti," ",tj)

    # Create tile window
    tile_window = rasterio.windows.Window(ti,tj,target_width,target_height)
    data = src.read(window=tile_window)

    # read DN (digital number) raster and build HSI array of calibrated radiance
    rad = np.empty((data.shape[0],data.shape[1],len(bands)))

    #print(rad)
    #print(rad.shape)

    i = 0
    for band in bands:
      print(abscalfactor[i]," ",effbandwidth[i])
      #print(data.read(i+1))
      rad[:,:,i] = data.read(i+1)*abscalfactor[i]/effbandwidth[i]
      #print(rad[i,:,:])
      i += 1

    print("raster ", rad.shape)

    # use upper left pixel for comparison
    ref_ang = np.array([rad[0,0,:]])
    #print(ref_ang)
    #print("ang    ", ref_ang.shape)
    ang = spectral_angles(rad,ref_ang)
 
    #print(ang) 
    #print(ang.shape) 

    # store stats
    ang_arr[ti:tj] = np.mean(ang)
    var_arr[ti:tj] = np.std(ang)
    vband_arr[ti:tj] = np.std(rad[:,:,0])

print(ang_arr)
