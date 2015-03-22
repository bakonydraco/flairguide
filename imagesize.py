#!/usr/local/bin/python
#imports
import sys, os
from PIL import Image
import math

width = int(sys.argv[1])
height = int(sys.argv[2])
aspectratio = width/float(height)
for filename in os.listdir("flairedit"):
 image = Image.open("flairedit/"+filename)
 filewidth = image.size[0]
 fileheight = image.size[1]
 fileaspectratio = filewidth/fileheight
 if aspectratio>fileaspectratio:
  border = math.ceil(fileheight*aspectratio)-filewidth
  filewidth = math.ceil(fileheight*aspectratio)
 else:
  border = math.ceil(filewidth/aspectratio)-fileheight
  fileheight = math.ceil(filewidth/aspectratio) 
 os.system("cp flairedit/"+filename+" fullorig")
 os.system("convert flairedit/"+filename+" -resize '"+str(filewidth)+"x"+str(fileheight)+"' -bordercolor none -border "+str(border)+" -gravity center -crop "+str(filewidth)+"x"+str(fileheight)+"+0+0! flairedit/"+filename)
 os.system("convert flairedit/"+filename+" -filter RobidouxSharp -resize "+str(width)+"x"+str(height)+"! -define png:format=png32 flairedit/"+filename)
 os.system("mv flairedit/"+filename+" full60")