#!/usr/local/bin/python
#imports
import urllib2
import simplejson
import cStringIO
from PIL import Image
import pandas
import os

teamsheetfile = "teamsheet.csv"
allteams = pandas.read_csv(teamsheetfile, quotechar='"', skipinitialspace=True)
fetcher = urllib2.build_opener()
for imagename in allteams.Name:
 try:
  searchterm = imagename.replace(' ','%20')
  startIndex = 0
  searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + searchterm + "&start=" + str(startIndex)
  f = fetcher.open(searchUrl)
  deserialized_output = simplejson.load(f)
  imageUrl = deserialized_output['responseData']['results'][0]['unescapedUrl']
  file = cStringIO.StringIO(urllib2.urlopen(imageUrl).read())
  img = Image.open(file)
  img.save("flairedit/"+str(allteams.Filename[map(str,allteams.Name).index(imagename)])+".png")
  print allteams.Filename[map(str,allteams.Name).index(imagename)]
 except: print "Error on " + imagename
os.system("mogrify -format png flairedit/*.png")