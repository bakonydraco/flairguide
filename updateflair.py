#!/usr/local/bin/python
#imports
import praw
import time
from time import gmtime, strftime
from collections import defaultdict
import csv
import re
import pandas
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

currentcounter = 1
credentials = pandas.read_csv("credentials.txt")
username, password, subreddit = credentials.item
pausetime = 10
teamsheetfile = "teamsheet.csv"
print "User Flair Update Time: " + strftime("%Y-%m-%d %H:%M:%S", gmtime())
r = praw.Reddit(user_agent=subreddit+' Flair Bot')
r.login(username,password)
sub = r.get_subreddit(subreddit)
allteams = pandas.read_csv(teamsheetfile, quotechar='"', skipinitialspace=True)
protectusers = ["nolez","diagonalfish","Honestly_","sirgippy","thrav","bakonydraco","Corporal_Hicks","blueboybob","CoachHerbHand","KKTTU","rsmith26","TheBobbyBowden","FauxPelini","srs_house","Alpha_Orange","ttsci","StrawberryTea","CoachBrohm"]
f = open('flaircount/current'+subreddit+str(currentcounter)+'.csv', 'w')
i = 0
d = defaultdict(int)
for key in allteams.Filename: d[key] = 0
for item in  sub.get_flair_list(limit=None):
 i += 1
 if(i%1000==0):print(i)
 try:
  user = item['user'].encode('utf8')
 except:
  user = str(item['user'])
 try:
  flair_text = item['flair_text'].encode('utf8').replace("&amp;","&")
 except:
  flair_text = str(item['flair_text'])
  flair_text = flair_text.replace("&amp;","&") 
 try: 
  css_class = item['flair_css_class'].encode('utf8')
 except:
  css_class = str(item['flair_css_class'])
 if css_class == "None" or css_class == "":
  newflair = ""
  newcss = ""
 else: 
  csslist = css_class.split('-')
  if (len(csslist) == 8):
   flaira = csslist[0]
   flairb = csslist[4]
   d[flaira] += 1
   if flaira[-1:].isdigit(): d[flaira[:-1]] +=1
   d[flairb] += 1
   if flairb[-1:].isdigit(): d[flairb[:-1]] +=1
   newcss = allteams.Flair1[map(str,allteams.Filename).index(flaira)] + '-' + allteams.Flair2[map(str,allteams.Filename).index(flairb)]
   if user in protectusers: newflair = flair_text
   else: newflair = allteams.Flairtext[map(str,allteams.Filename).index(flaira)] + ' / ' + allteams.Flairtext[map(str,allteams.Filename).index(flairb)]
   if len(newflair) > 64: newflair = newflair[:63] + u"\u2026"
  else: 
   if (len(csslist) == 2): flair = csslist[1]
   else: flair = csslist[0]
   d[flair] += 1
   if flair[-1:].isdigit(): d[flair[:-1]] +=1
   newcss = allteams.Flair[map(str,allteams.Filename).index(flair)]
   if user in protectusers: newflair = flair_text
   else: newflair = allteams.Flairtext[map(str,allteams.Filename).index(flair)]
  if newflair != flair_text or newcss != css_class:
   try: 
    print("Modifying user " + user + " from " + css_class + " to " + newcss + " and " + flair_text + " to " + newflair)
    sub.set_flair(user, flair_text=newflair, flair_css_class=newcss)
    flairstoadd = open('flairstoadd.csv','a')
    flairstoadd.write(user+","+newflair+","+newcss+"\n")
    flairstoadd.close()
   except:
    print("error on " + user)
 f.write(user + "," + newflair + "," +  newcss + "\n")
f.close()
with open(subname+'/numflairs.csv', 'wb') as f:  
 for key, value in sorted(d.iteritems(), key=lambda (k,v): (v,k), reverse=True):
  f.write(key + "," + str(value) + "\n")
