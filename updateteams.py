#!/usr/local/bin/python
#coding=utf-8

import csv
import numpy
import pandas
import math
import praw
from PIL import Image, ImageChops
import os

credentials = pandas.read_csv("credentials.txt")
username, password, subreddit = credentials.item
r = praw.Reddit(user_agent=subreddit+' Flair Bot')
r.login(username,password)
try:
 sub = r.get_subreddit(subreddit)
 maincss = sub.get_wiki_page('maincss')
 with open('maincss.css', 'w') as maincssfile:
  maincssfile.write(maincss.content_md.replace("&amp;","&"))
except: print "Error Getting CSS"
filenames = ['maincss.css','flair.css','flairlocs.css']


def unique(sequence):
 seen = set()
 for item in sequence:
  if item not in seen:
   seen.add(item)
   yield item

def createimages():
 numcols = 24
 scalefactor = .5
 padding = 10
 flairw = open('flairlocs.css','w')
 flairw.write("/*Flair Shortcuts*/\n")
 displayteams = allteams[allteams.Selectdisplay==True] 
 for i in unique(displayteams.File):
  fileteams = displayteams[displayteams.File==i]
  flairwidth = numpy.min(fileteams.Width)
  flairheight = numpy.min(fileteams.Height)
  colwidth = flairwidth+padding
  rowheight = flairheight+padding
  if(numpy.min(fileteams.File) == "Images"): folder = "full60s"
  else: folder = "full60"
  flairlocs = []
  totalrow = 0
  for j in unique(fileteams.Conf):
   confteams = fileteams[fileteams.Conf == j]
   kcount = 0
   for k in confteams.Filename:
    rowpx = rowheight*(totalrow+1)
    colpx = colwidth*kcount
    flairlocs.append([k, rowpx, colpx])
    kcount+=1
   totalrow += 1
  xfull = numcols*colwidth
  yfull = rowheight*(totalrow+1)
  fileimage = Image.new("RGBA", (xfull, yfull))
  fileimage.paste(Image.open(folder+"/rcfb.png"),(0, 0))
  for j in range(len(flairlocs)):
   fileimage.paste(Image.open(folder+"/"+flairlocs[j][0]+".png"),(int(flairlocs[j][2]),int(flairlocs[j][1])))
   row = int(flairlocs[j][1]*scalefactor)
   if (row != 0): rown = "-"+str(row)+"px"
   else: rown = "0"
   if (flairlocs[j][2] != 0): coln = "-"+str(int(flairlocs[j][2]*scalefactor))+"px"
   else: coln = "0"
   flaircoords = []
   teamrow = allteams[allteams.Filename==flairlocs[j][0]]
   teamindex = map(str,allteams.Filename).index(flairlocs[j][0])
   if str(teamrow.Shortcutflair[teamindex]) != "None": flaircoords.append('.flair-'+str(teamrow.Shortcutflair[teamindex])+':before')
   if str(teamrow.Shortcutinline[teamindex]) != "None": flaircoords.append('a[href="'+str(teamrow.Shortcutinline[teamindex])+'"]:before')
   if str(teamrow.Shortcutletter[teamindex]) != "None": flaircoords.append('a[href="'+str(teamrow.Shortcutletter[teamindex])+'"]:before')
   if len(flaircoords) > 0: flairw.write(','.join(flaircoords)+"{background-position:"+coln+" "+rown+"}")
  fileimage.save("teamsheet/new"+i+".png")
  replaceimage("teamsheet",i)
 flairw.close()

def flairtext():
 wikitext = open('wikitext.txt','w')
 flairteams = allteams[allteams.Selectflair==True] 
 wikitext.write("## This list currently contains "+str(len(flairteams))+" flairs.\n\n")
 for i in unique(flairteams.Division):
  fileteams = flairteams[flairteams.Division==i]
  if len(fileteams) > 0:
   wikitext.write("### "+numpy.min(fileteams.Division)+"\n")
   for j in unique(fileteams.Conf):
    confteams = fileteams[fileteams.Conf == j]
    if len(confteams) > 0:
     wikitext.write("\n## "+numpy.min(confteams.Conference)+"\n\n|||||||||\n|:--|:--|:--|:--|:--|:--|:--|:--|\n")
     conflist = []
     for k in confteams.Filename:
      teamrow = allteams[allteams.Filename==k]
      teamindex = map(str,allteams.Filename).index(k)
      nametourl = str(teamrow.Name[teamindex]).replace("(","%28").replace(")","%29").replace("&","%26")
      if str(teamrow.Shortcutinline[teamindex]) != "None": teaminline = "["+str(teamrow.Abbreviated[teamindex])+"]("+str(teamrow.Shortcutinline[teamindex])+")"
      else: teaminline = "["+str(teamrow.Abbreviated[teamindex])+"](#f/"+str(teamrow.Flair1[teamindex])+")"
      teamfull = teaminline+"|["+str(teamrow.Name[teamindex])+"](/message/compose/?to=cfbflair&subject=flair&message="+nametourl+")"
      conflist.append(teamfull)
     spotsusedx = (range(4)*6)[:len(conflist)]
     spotsusedy = numpy.repeat(range(6),4)[:len(conflist)]
     spotsxorder = sorted(range(len(spotsusedx)), key=lambda lambdakey: spotsusedx[lambdakey]) 
     spotsorder = sorted(range(len(spotsusedy)), key=lambda lambdakey: spotsusedy[spotsxorder][lambdakey])
     sortedconf = [conflist[l] for l in spotsorder]
     while len(sortedconf) % 4 != 0: sortedconf.append("")
     for l in range(len(sortedconf)):
      wikitext.write("|"+sortedconf[l])
      if (l+1) % 4 == 0: wikitext.write("|\n")
 wikitext.close()

def inlinetext():
 wikiinline = open('wikiinline.txt','w')
 inlineteams = allteams[allteams.Selectinline==True] 
 wikiinline.write("## This list currently contains "+str(len(inlineteams))+" flairs.\n\n")
 for i in unique(inlineteams.Division):
  fileteams = inlineteams[inlineteams.Division==i]
  if len(fileteams) > 0:
   wikiinline.write("### "+numpy.min(fileteams.Division)+"\n")
   for j in unique(fileteams.Conf):
    confteams = fileteams[fileteams.Conf == j]
    if len(confteams) > 0:
     wikiinline.write("\n## "+numpy.min(confteams.Conference)+"\n\n|Name|Code|Result|\n|:--|:--|:-:|\n")
     for k in confteams.Filename:
      teamrow = allteams[allteams.Filename==k]
      teamindex = map(str,allteams.Filename).index(k)
      if str(teamrow.Shortcutinline[teamindex]) != "None": wikiinline.write("|"+str(teamrow.Name[teamindex])+"|\["+str(teamrow.Abbreviated[teamindex])+"]("+str(teamrow.Shortcutinline[teamindex])+")|["+str(teamrow.Abbreviated[teamindex])+"]("+str(teamrow.Shortcutinline[teamindex])+")|\n")
      else: wikiinline.write("|"+str(teamrow.Name[teamindex])+"|\["+str(teamrow.Abbreviated[teamindex])+"](#f/"+str(teamrow.Flair1[teamindex])+")|["+str(teamrow.Abbreviated[teamindex])+"](#f/"+str(teamrow.Flair1[teamindex])+")|\n")
 wikiinline.close()

def replaceimage(image, folder):
 try:
  newimage = str(folder) + "/new" + str(image) + ".png"
  oldimage = str(folder) + "/" + str(image) + ".png"
  sub = r.get_subreddit(subreddit)
  if(os.path.isfile(newimage)):
   imagesize = os.path.getsize(newimage)
   if (imagesize > 512000):
    os.system("optipng " + newimage)
   imagesize = os.path.getsize(newimage)
   if (imagesize > 512000):
    os.system("pngquant teamsheet/new"+i.lower()+".png --ext=.png --force")
   if(os.path.isfile(oldimage)):
    if Image.open(newimage).size != Image.open(oldimage).size or not ImageChops.difference(Image.open(newimage), Image.open(oldimage)).getbbox() is None:
     print (str(subreddit) + " "  + str(image) + " update time: " + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
     os.rename(newimage,oldimage)
     sub.upload_image(oldimage, name=image, header=False)
     update()
   else: 
    print (str(subreddit) + " " + str(image) + " update time: " + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    os.rename(newimage,oldimage)
    sub.upload_image(oldimage, name=image, header=False)
    update()
 except: print "Error Replacing Image" + image + subreddit

def update():
 with open('new' + subreddit + '.css', 'w') as outfile:
  for fname in filenames:
   with open(fname) as infile:
    for line in infile:
     outfile.write(line)
 filechanged = not filecmp.cmp('new' + subreddit + '.css', subreddit + '.css', shallow=False)
 if hardupdate == True or filechanged:
  os.rename('new' + subreddit + '.css', subreddit + '.css')
  with open(subreddit + '.css', 'r') as content_file:
   content = content_file.read()
  sub = r.get_subreddit(subreddit)
  try: 
   sub.set_stylesheet(content)
  except: print("Error Setting Stylesheet")
  print("Updated" + subreddit)

def updatewikis():
 with open('wikitextheader.txt','r') as contentfile:
  wikitextheader = contentfile.read()
 with open('wikitext.txt','r') as contentfile:
  wikitext = contentfile.read()
 try:
  sub = r.get_subreddit(subreddit)
  sub.edit_wiki_page("flair", wikitextheader + wikitext, reason='')
  time.sleep(2)
 except: print "Error Updating Flair Text"
 with open('wikiinlineheader.txt','r') as contentfile:
  wikiinlineheader = contentfile.read()
 with open('wikiinline.txt','r') as contentfile:
  wikiinline = contentfile.read()
 try:
  sub = r.get_subreddit(subreddit)
  sub.edit_wiki_page("inlineflair", wikiinlineheader + wikiinline, reason='')
  time.sleep(2)
 except: print "Error Updating Inline Flair"

allteams = pandas.read_csv("teamsheet.csv", quotechar='"', skipinitialspace=True)
createimages()
flairtext()
inlinetext()
updatewikis()