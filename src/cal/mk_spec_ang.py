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

# setup tiling
src = rasterio.open('In/orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031_rad.tif')
print("src ",src.shape)
src_height = src.shape[0]
src_width = src.shape[1]
overlap = 0
target_height = 100
target_width = 100

ysize = math.floor(src_width/target_width) - 2
xsize = math.floor(src_height/target_height) - 2
print(xsize,ysize,"  img")
ang_arr = np.empty((src_height,src_width))
var_arr = np.empty((src_height,src_width))
vband_arr = np.empty((src_height,src_width))
#ang_arr = np.empty((xsize,ysize))
#var_arr = np.empty((xsize,ysize))
#vband_arr = np.empty((xsize,ysize))
print(ang_arr.shape[0])
print(ang_arr.shape[1])

# start tiling
ti = 0
while ti < src_height - target_height:
  tj = 0
  while tj < src_width - target_width:
    #print(ti," ",ti+target_height," ",src_height - target_height," ",tj, " ",tj+target_width," ",src_width - target_width," ",ysize," ",xsize)

    # Create tile window
    tile_window = rasterio.windows.Window(tj,ti,target_width,target_height)
    dt = src.read(window=tile_window)
    data = dt.transpose()

    #print(ang_arr.shape)
    #print(src.shape)
    #print(src_height, src_width)
    #print("data ",data.shape)

    # read radiance raster and build HSI array of calibrated radiance/band
    rad = np.empty((data.shape[0],data.shape[1],len(bands)))
    i = 0
    for band in bands:
      #print(abscalfactor[i]," ",effbandwidth[i])
      rad[:,:,i] = data[:,:,i]

      #print(rad[:,:,i])
      i += 1

    #print("raster ", rad.shape)


    # use upper left pixel for comparison
    ref_ang = np.array([rad[0,0,:]])
    #print(ref_ang)
    #print("ang    ", ref_ang.shape)
    ang = spectral_angles(rad,ref_ang)

    #print(ang) 
    #print(ang.shape) 
    #print("Max ",np.max(ang))

    # store stats
    ##ang_arr[ti:ti+target_width,tj:tj+target_height] = np.mean(ang)
    ang_arr[ti:ti+target_height,tj:tj+target_width] = ang[:,:,0]
    var_arr[ti:ti+target_height,tj:tj+target_width] = np.std(ang)
    vband_arr[ti:ti+target_height,tj:tj+target_width] = np.std(rad[:,:,0])
    tj += target_width
  ti += target_height

print(ang_arr[800:850,800:850])
print(var_arr[800:850,800:850])
print(vband_arr[800:850,800:850])
np.savetxt("ang_arr_100.csv", ang_arr, delimiter=",")
np.savetxt("var_arr_100.csv", var_arr, delimiter=",")
np.savetxt("vband_arr_100.csv", vband_arr, delimiter=",")

# save in tif
meta = src.meta
# Update meta to reflect the number of layers
meta.update(count = 3)
ang_arr.astype(int)
# Read each layer and write it to stack
with rasterio.open('stack_100.tif', 'w', **meta) as dst:
  dst.write_band(1, ang_arr)
  dst.write_band(2, var_arr)
  dst.write_band(3, vband_arr)
