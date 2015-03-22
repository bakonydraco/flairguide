#!/usr/local/bin/python
#coding=utf-8

#imports
import subprocess
import praw
import time, datetime, calendar
from time import gmtime, strftime
import re
from PIL import ImageChops, Image
import os, sys, os.path
import urllib, urllib2
from urllib2 import urlopen
from bs4 import BeautifulSoup
import requests
import filecmp
import cStringIO
import tweepy
import csv
from splinter import Browser
import signal
from contextlib import contextmanager
import pandas

credentials = pandas.read_csv("credentials.txt")
username, password, subreddit = credentials.item
pausetime = 10
robotmessage = "\n\n*I'm just a robot and this account is not checked often, so if you have further questions please check our [FAQ](/r/CFB/wiki/rules)*."
modlist = ['bakonydraco']
teamsheetfile = "teamsheet.csv"

def checkmessages(j,r):
 for msg in r.get_unread(limit=None):
  print(msg)
  auth = str(msg.author).encode("utf8")
  subj = msg.subject.encode("utf8").strip().lower().replace("&amp;","&")
  body = msg.body.encode("utf8").replace("&amp;","&")
  if (subj == "flair"): setflair(auth,body,r)
  elif (subj == "flairuser"): setflairuser(auth,body,r)
  elif (subj == "award"): logaward(auth,body,msg,r)
  elif (subj == "grantaward"): grantaward(auth,body,msg,r)
  else: r.send_message(auth, 'Command not recognized', "Sorry, the subject line of your message is not a command I recognize."+robotmessage)
  msg.mark_as_read()
 return(j)

def checkteam(team):
 try: 
  if allteams.Selectflair[map(str,allteams.Name).index(team)]: return(True)
 except: pass
 return(False)

def setflairuser(auth,body,r):
 if auth in modlist["cfb"]:
  auth = body.split("\n")[0]
  bodyuser = "\n".join(body.split("\n")[1:]).rstrip()
  setflair(auth,bodyuser,msg,subredditflag,r)
 else: 
  r.send_message(auth, 'Permission Denied', "Sorry, you don't have permission to set images for that subreddit."+robotmessage)
  print "Permission Denied: " + subreddits 

def settingflair(auth,teamname,teamflair,r):
 try:
  if len(teamname) > 64: teamname = teamname[:63].decode("utf-8") + u"\u2026"
  message = 'Setting Flair: ' + auth + ' : ' + teamname + ' @ ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " to " + subreddit
  sub = r.get_subreddit(subreddit)
  sub.set_flair(auth, teamname, teamflair)
  flairlog = open('flairlog.csv','a')
  flairlog.write(auth+","+teamname+","+teamflair+","+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\n")
  flairlog.close()
  print message
 except: print "Error Setting Flair"

def setflair(auth,body,r):
 tokens = body.split("\n")
 team = tokens[0]
 retcss = ""
 if("/" in team):
  twoteams = team.split("/")
  teama1 = twoteams[0].strip()
  teamb1 = twoteams[1].strip()
  try: 
   teama = allteams.Flairtext[map(str,allteams.Name).index(teama1)]
   teamb = allteams.Flairtext[map(str,allteams.Name).index(teamb1)]
  except: 
   teama = teama1
   teamb = teamb1
  team = teama + " / " + teamb
  if checkteam(teama1):
   if checkteam(teamb1):
    if not checkaward(auth,allteams.Filename[map(str,allteams.Name).index(teama)],r):
     r.send_message(auth, "You haven't earned that!", "You haven't earned that award yet."+robotmessage)
     if not checkaward(auth,allteams.Filename[map(str,allteams.Name).index(teamb)],r):
      r.send_message(auth, "You haven't earned that!", "You haven't earned that award yet."+robotmessage)
      team = ""
      retcss = ""
     else: 
      team = teamb
      retcss = allteams.Flair[map(str,allteams.Name).index(teamb1)]
    else:
     if not checkaward(auth,allteams.Filename[map(str,allteams.Name).index(teamb)],r):
      r.send_message(auth, "You haven't earned that!", "You haven't earned that award yet."+robotmessage)
      team = teama
      retcss = allteams.Flair[map(str,allteams.Name).index(teama1)]
     else:
      if(teama == teamb):
       r.send_message(auth, "Two of the same", "At this point we do not allow you to select two flairs from the same school, both for stylistic and flair count reasons."+robotmessage)
       team = teama
       retcss = allteams.Flair[map(str,allteams.Name).index(teama1)]
      else: retcss = allteams.Flair1[map(str,allteams.Name).index(teama1)]+"-"+allteams.Flair2[map(str,allteams.Name).index(teamb1)]
 else: 
  team1 = team.strip()
  try:
   team = allteams.Flairtext[map(str,allteams.Name).index(team1)]
   if checkteam(team.strip()):
    if not checkaward(auth,allteams.Filename[map(str,allteams.Name).index(team1)],r):
     r.send_message(auth, "You haven't earned that!", "You haven't earned that award yet."+robotmessage)
     team = ""
     retcss = ""
    else: retcss = allteams.Flair[map(str,allteams.Name).index(team1)]
  except: retcss = ""
 if retcss != "":
  settingflair(auth,team,retcss,r)
 else: 
  r.send_message(auth, 'Team not found', "It looks like you were trying to set your flair for a team we don't have."+robotmessage)
  print "Team not found: " + team
  
awardflairs = ["beard","artist","medal","contributor","brick","checkbox","tv","coach","media","player","ref","staff","fulmer","offtopicbelt"]
awardtables = ["","","Alternate Flairs","/r/CFB Showdown Trophy History","The Battle for Texas Trophy History","/r/CFB Emeritus Mod","/r/CFB Artist","/r/CFB Patron","/r/CFB Top Scorer","/r/CFB Pick 'Ems","Best of /r/CFB","/r/CFB Contributor","Miscellaneous Contributions","132+ Teams in 132+ Days","35 Bowls in 17 Days","Complete History of CFB","/r/CFB Donor","/r/CFB ALS Ice Bucket Challenge","Thanksgiving Food Drive","/r/CFB Love Drive","/r/CFB Brickmason","Baylor Brick Fund","CFB Hall of Fame Brick Fund","Rose Bowl Brick Fund","UCF Brick Fund","/r/CFB Brick Fund V: The Magnificent Seven","/r/CFB Pollster","/r/CFB Promoter","Verified Coach","Verified Media","Verified Player","Verified Referee","Verified Staff","Fulmer Cup Committee Member","/r/CFB Off Topic Belt","Marching Band"]
def checkaward(auth,award,r):
 if not award in awardflairs: return(True)
 if award == "beard": tablenum = [5]
 if award == "artist": tablenum = [6]
 if award == "patron": tablenum = [7]
 if award == "medal": tablenum = [9,10]
 if award == "contributor": tablenum = [12,13,14,15]
 if award == "tophat": tablenum = [17,18,19]
 if award == "brick": tablenum = [21,22,23,24,25]
 if award == "checkbox": tablenum = [26]
 if award == "tv": tablenum = [27]
 if award == "coach": tablenum = [28]
 if award == "media": tablenum = [29]
 if award == "player": tablenum = [30]
 if award == "ref": tablenum = [31]
 if award == "staff": tablenum = [32]
 if award == "fulmer": tablenum = [33]
 if award == "offtopicbelt": tablenum = [34]
 awardswiki = r.get_wiki_page("cfb","awards")
 tables = awardswiki.content_md.split("##")
 returnflag = False
 for tnum in tablenum:
  if auth.lower() in tables[tnum].encode('utf8').lower(): returnflag = True
 return(returnflag)

def logaward(auth,body,msg,r):
 try:
  sub = r.get_subreddit('cfb')
  awardlog = sub.get_wiki_page('awardlog')
  sub.edit_wiki_page("awardlog", awardlog.content_md.replace("&amp;","&") + "\n\n" + auth  +", " + body, reason='')
  time.sleep(2)
 except: print "Error Logging Award"

def grantaward(auth,body,msg,r):
 if auth in modlist["cfb"]:
  try: 
   authuser = body.split("\n")[0].strip()
   bodyuser = body.split("\n")[1].strip()
   table = body.split("\n")[2].strip()
   verificationtitle = body.split("\n")[3].strip()
   verificationlink = body.split("\n")[4].strip()
   tablenum = awardtables.index(table)
   awardswiki = r.get_wiki_page("cfb","awards")
   tables = awardswiki.content_md.replace("&amp;","&").split("##")
   tables[tablenum] = tables[tablenum].rstrip() + "\n|/u/" + authuser.replace("/u/","") + "|[" + verificationtitle + "](" + verificationlink + ")|\n\n" 
   awardswikiupdate = "##".join(tables)
   sub = r.get_subreddit(allsubreddits[0])
   sub.edit_wiki_page("awards", awardswikiupdate, reason='')
   time.sleep(2)
   r.send_message(authuser,'You won a ' + bodyuser + ' award flair!', "Check out our [Awards Page](/r/cfb/wiki/awards) for details on how you won.  You can now change to and from it at any time from the [flair selector](/r/cfb/wiki/flair)."+robotmessage)
  except: print "Error granting award"
 else: 
  r.send_message(auth, 'Permission Denied', "Sorry, you don't have permission to set images for that subreddit."+robotmessage)
  print "Permission Denied: " + subreddits 

print "CFBFlair start time: " + strftime("%Y-%m-%d %H:%M:%S", gmtime())
r = praw.Reddit(user_agent=subreddit+' Flair Bot')
r.login(username,password)
allteams = pandas.read_csv(teamsheetfile, quotechar='"', skipinitialspace=True)
while True:
 print "Flair Bot update time: " + strftime("%Y-%m-%d %H:%M:%S", gmtime())
 try:
  j = checkmessages(j,r)
 except: print "Error in messages"
 time.sleep(pausetime)
