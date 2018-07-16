#################################
#
# STEP 1: Prepare working environment
#
#################################

#Set working directory for wherever your files are
setwd("~/Downloads")

#load raster library
library(raster)

#load file
raster_brick<-brick("orthoWV02_13NOV131639373-M1BS-1030010029192A00_u16ns3031.tif")

#################################
#
# STEP 2: Examine file
#
#################################

#plot file
plotRGB(raster_brick,r=4,g=3,b=2)

#print information
raster_brick

##extracts the cell numbers for a Row and Column
#cells<-cellFromRowCol(raster_brick,2000,2000)
##Extract the DN value
#extract(raster_brick,cells)

#################################
#
# STEP 3: Regressions to convert TOAradiance to Surface radiance
#
#################################

#insert parameters
abscalfactor<-9.042234000000000e-03
effbandwith<-9.959999999999999e-02
#wavelengths<-c(0.425, 0.48, 0.545, 0.605, 0.660, 0.725, 0.830, 0.950)

#Select an area to zoom in on; click once in upper left and once in lower right of box
s<-select(raster_brick) #create a zoomed in portion to inspect for polygon selection
plotRGB(s,r=4,g=3,b=2)
TOAradiance<-s*(abscalfactor/effbandwith)
s2<-select(TOAradiance,use="pol",draw=T) #draw a polygon to extract spectra; click vertices and then hit esc when done

regression.spectra<-c()
for (i in 1:(dim(s2)[1]*dim(s2)[2]))
{
  if (!is.na(s2[i][1])) {
    regression.spectra<-rbind(regression.spectra,as.numeric(s2[i]))                 }
}
colnames(regression.spectra)<-c("b1","b2","b3","b4","b5","b6","b7","b8")

regression.b1<-lm(regression.spectra[,1]~regression.spectra[,8])$coefficients[1]
regression.b2<-lm(regression.spectra[,2]~regression.spectra[,8])$coefficients[1]
regression.b3<-lm(regression.spectra[,3]~regression.spectra[,8])$coefficients[1]
regression.b4<-lm(regression.spectra[,4]~regression.spectra[,8])$coefficients[1]
regression.b5<-lm(regression.spectra[,5]~regression.spectra[,8])$coefficients[1]
regression.b6<-lm(regression.spectra[,6]~regression.spectra[,8])$coefficients[1]
regression.b7<-lm(regression.spectra[,7]~regression.spectra[,8])$coefficients[1]
# regression.spectra<-data.frame(regression.spectra)
#f<-ggplot(regression.spectra,aes(b8,b1))
#f+geom_point()+coord_cartesian(ylim=c(0,max(regression.spectra$b1)),xlim=c(0,max(regression.spectra$b8)))


Surface.radiance<-TOAradiance-c(regression.b1,regression.b2,regression.b3,regression.b4,regression.b5,regression.b6,regression.b7,0)

plotRGB(Surface.radiance-min(Surface.radiance@data@min),r=4,g=3,b=2)
#Subtracting the minimum of the minimums just ensures that everything is non-negative for plotting
