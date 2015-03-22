#!/usr/local/bin/python
#imports
import sys, os

os.system("mogrify -format png flairedit/*.gif")
os.system("mogrify -format png flairedit/*.GIF")
os.system("mogrify -format png flairedit/*.jpg")
os.system("mogrify -format png flairedit/*.JPG")
os.system("mogrify -format png flairedit/*.jpeg")
os.system("mogrify -format png flairedit/*.JPEG")
os.system("rm flairedit/*.gif")
os.system("rm flairedit/*.GIF")
os.system("rm flairedit/*.jpg")
os.system("rm flairedit/*.JPG")
os.system("rm flairedit/*.jpg")
os.system("rm flairedit/*.JPEG")
os.system("mogrify -bordercolor white -border 60 -gravity center +repage flairedit/*.png")
os.system("mogrify -fill none -fuzz 15% -draw 'color 1,1 floodfill' -trim +repage flairedit/*.png")
