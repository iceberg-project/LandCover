import xml.etree.ElementTree as ET
import rasterio
from spectral import *
import numpy as np

tree=ET.parse('orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031.xml')
root = tree.getroot()

# collect image metadata
bands = ['BAND_C','BAND_B','BAND_G','BAND_Y','BAND_R','BAND_RE','BAND_N','BAND_N2']
src=root[1][2].find('IMAGE')
satid = src.find('SATID').text
meansunel = src.find('MEANSUNEL').text
tlctime = src.find('TLCTIME').text

if satid == 'WV02':
  esun = [1758.2229,1974.2416,1856.4104,1738.4791,1559.4555,1342.0695,1069.7302,861.2866] # WV02
if satid == 'WV03':
  esun = [1803.9109,1982.4485,1857.1232,1746.5947,1556.9730,1340.6822,1072.5267,871.1058] # WV03

print(esun)

# collect band metadata
abscalfactor = [1] * len(bands)
effbandwidth = [1] * len(bands)

i = 0
for band in bands:
  src=root[1][2].find(band)
  abscalfactor[i] = float(src.find('ABSCALFACTOR').text)
  effbandwidth[i] = float(src.find('EFFECTIVEBANDWIDTH').text)
  print(bands[i])
  i += 1
print(abscalfactor)

# tiling goes here - using one example for now

# read DN (digital number) raster and build HSI array of calibrated radiance
data = rasterio.open('sample_10.tif')
rad = np.empty((data.shape[0],data.shape[1],len(bands)))

print(rad)
print(rad.shape)

i = 0
for band in bands:
  print(abscalfactor[i]," ",effbandwidth[i])
  print(data.read(i+1))
  rad[:,:,i] = data.read(i+1)*abscalfactor[i]/effbandwidth[i]
  print(rad[i,:,:])
  i += 1

print("raster ", rad.shape)

# ref_ang = np.array([[672,1220,1626,977,1524,931,1550,620]])
# use upper left pixel for comparison
ref_ang = np.array([rad[0,0,:]])
print(ref_ang)
print("ang    ", ref_ang.shape)
ang = spectral_angles(rad,ref_ang)
 
print(ang) 
print(ang.shape) 
