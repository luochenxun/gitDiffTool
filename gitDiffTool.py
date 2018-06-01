#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  Code-Analysis tool of git project  """
__author__ = 'luochenxun(luochenxun@gmail.com)'
__version__ = '1.0.2'

import getopt
import sys
import re
from sys import argv
import os.path
import locale
import codecs
from subprocess import Popen, PIPE
import subprocess
import datetime
import time
import shutil
import json
import webbrowser

def usage():
  """Print usage of gitDiffTool."""
  print "   \'gitDiffTool\' is a tool to compare two commits of a gitProject and generate the diff into html.\nYou can read the diff in one html page, the list of modified files on one side and the specifics diff-content on the other. "
  print "\nUsage: %s [OPTIONS] [params]\n" % sys.argv[0]
  print "  -d [sCommit] dCommit  : diff two commit(if given one diff with current commit), output the result using html"
  print "  -h|--help             : print this usage"
  print "  -v|--version          : print the version"
  print '''
Examples:
    gitDiffTool.py -d 79809324 341324   # compare tow commit
    gitDiffTool.py -d 787234            # compare current branch with given commit
    gitDiffTool.py -d develop           # compare current branch with given branch's name
  '''
  print "\n"
  os._exit(0)

''' global variable '''

indexTemplete = '''
<!DOCTYPE html>
<html lang="en">

  <head>
    <meta charset="utf-8" />
    <title>Result of gitDiffTool</title>
  </head>

  <frameset  border="1" frameborder="1" rows="100%">
    <frameset cols="50%,*">
      <frame src="list.html" name="list" />
      <frame src="" name="page" />
    </frameset>

    <noframes>
      <body>
        你的浏览器不支持frame
      </body>
    </noframes>

  </frameset>

</html>
'''

listTemplete = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Modified files of two commit</title>
    <style type="text/css">

    /* hovertable */
    table.hovertable {
        font-family: verdana,arial,sans-serif;
        font-size:11px;
        color:#333333;
        border-width: 1px;
        border-color: #999999;
        border-collapse: collapse;
        table-layout: fixed;
        width:100%;
    }
    table.hovertable th {
        background-color:#7799dd;
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #a9c6c9;
    }
    table.hovertable tr {
        background-color:#d4e3e5;
    }
    table.hovertable td {
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #a9c6c9;
        word-break: break-all;
        word-wrap: break-word;
    }
    /* /hovertable */

    </style>
</head>
<body>


<h2>Modified files of two commit</h2>
<table class="hovertable">
    <tr>
        <th width="85%">Modifyed Files</th><th>Participants</th>
    </tr>
    <***templete of table***>
</table>

</body>
</html>
'''

modifiedFileTemplete = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Result of gitDiffTool</title>
    <style type="text/css">

    /* hovertable */
    table.hovertable {
        font-family: verdana,arial,sans-serif;
        font-size:11px;
        color:#333333;
        border-width: 1px;
        border-color: #999999;
        border-collapse: collapse;
    }
    table.hovertable th {
        background-color:#7799dd;
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #a9c6c9;
    }
    table.hovertable tr {
        background-color:#d4e3e5;
    }
    table.hovertable td {
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #a9c6c9;
    }
    /* /hovertable */

    </style>
</head>
<body>

<h2>Diff Specifics</h2>

<***templete of table***>

</body>
</html>
'''

''' class define '''

class ModifiedFile:
    fileName = ''
    filePath = ''
    modifier = ''
    commits = []
    # constructor
    def __init__(self, filePath, sCommit, dCommit):
        self.filePath = filePath
        baseName = os.path.basename(filePath)
        index = baseName.rfind('.')
        self.fileName = baseName[:index]
        self.commits = []
        result = os.popen("git log -p %s..%s %s"%(dCommit,sCommit,filePath)).readlines()
        commitInfo = []
        for line in result:
            line = line.replace("\n", "")
            if re.match(r'^commit(.*)',line):
                self.addCommit(commitInfo)
                commitInfo = []
            commitInfo.append(line)
        self.addCommit(commitInfo)
        for commit in self.commits:
            if self.modifier.find(commit.commitAuthor) == -1:
                self.modifier += (commit.commitAuthor + ',')
        self.modifier = self.modifier[:len(self.modifier)-1]
    def addCommit(self, commitInfo):
        if commitInfo and len(commitInfo) > 0:
            commit = Commit(commitInfo)
            self.commits.append(commit)

class Commit:
    commitId = ''
    commitMsg = ''
    commitDate = ''
    commitAuthor = ''
    commitContent = ''
    def __init__(self, commitInfo):
        for index, line in enumerate(commitInfo):
            # commitID
            m = re.match(r'^commit(.*)',line)
            if m:
                self.commitId = m.group(1).strip()
                continue
            # commitAuthor
            m = re.match(r'^Author:(.*)',line)
            if m:
                self.commitAuthor = m.group(1).strip()
                continue
            # commitDate
            m = re.match(r'^Date:(.*)',line)
            if m:
                self.commitDate = m.group(1).strip()
                continue
            if index == 4:
                self.commitMsg = line.strip()
                continue
            if re.match(r'^\-',line):
                self.commitContent += '<font style="font-weight:bold" color="green"><xmp>'+ line + '</xmp> </font>'
            elif re.match(r'^\+',line):
                self.commitContent += '<font style="font-weight:bold" color="red"><xmp>'+ line + '</xmp> </font>'
            elif re.match(r'^\@',line):
                self.commitContent += '<hr>'
                self.commitContent += '<b><xmp>'+ line + '</xmp> </b>'
            else:
                self.commitContent += '<xmp>'+ line + '</xmp>'


''' main logic '''

def diffTool(commits):
    if len(commits) != 1 and len(commits) != 2:
        print("please input a commit object");
        usage();
    if len(commits) == 1:
        diffCommit('', commits[0])
    else:
        diffCommit(commits[0], commits[1]);

def diffCommit(sCommit , dCommit):
    result = os.popen("git diff --name-only " + sCommit + " " + dCommit).readlines()
    files = []
    for line in result[:len(result)]:
        filePath = line.replace("\n", "")
        modifiedFile = ModifiedFile(filePath, sCommit, dCommit)
        files.append(modifiedFile)
        # _listAll(modifiedFile)
    generateHTML(files)
    print('Analysis success! The result was generate in \'output\\index.html\'.');
    openHTML('file://' + os.getcwd() + '/output/index.html')

def generateHTML(files):
    global listTemplete, modifiedFileTemplete
    _checkOutputDir()
    # generate file pages
    rows = ''
    for mf in files:
        rows = ''
        for commit in mf.commits:
            rows += "<table class=\"hovertable\"> <tr> <th> Commit ID : %s</th> </tr>"%(commit.commitId)
            rows += '<tr onmouseover=\"this.style.backgroundColor=\'#ffff66\';\" onmouseout=\"this.style.backgroundColor=\'#d4e3e5\';\"><td> Commit Date : '+ commit.commitDate + '</td></tr>'
            rows += '<tr onmouseover=\"this.style.backgroundColor=\'#ffff66\';\" onmouseout=\"this.style.backgroundColor=\'#d4e3e5\';\"><td> Commit Author : '+ commit.commitAuthor + '</td></tr>'
            rows += '<tr onmouseover=\"this.style.backgroundColor=\'#ffff66\';\" onmouseout=\"this.style.backgroundColor=\'#d4e3e5\';\"><td> Commit Msg : '+ commit.commitMsg + '</td></tr>'
            rows += '<tr style="line-height:50%"><td> '+ commit.commitContent + '</td></tr>'
            rows += '</table><p>'
        pageHTML = modifiedFileTemplete.replace('<***templete of table***>',rows)
        fout = open('output/pages/' + mf.fileName + '.html' , 'w+');
        fout.write(pageHTML)
        fout.close()
    # generate list
    rows = ''
    for mf in files:
        # file in index
        rows = rows + '''<tr onmouseover="this.style.backgroundColor='#ffff66';" onmouseout="this.style.backgroundColor='#d4e3e5';">'''
        rows = rows + '\n<td width="85%"><a href=\'pages/' + mf.fileName + '.html\' target=\'page\'>'+ mf.filePath + '</a></td><td>' + mf.modifier + '</td>\n</tr>\n'
        #
    listTemplete = listTemplete.replace('<***templete of table***>',rows)
    fout = open('output/list.html' , 'w+');
    fout.write(listTemplete)
    fout.close()
    # generate index
    fout = open('output/index.html' , 'w+');
    fout.write(indexTemplete)
    fout.close()

def openHTML(file):
    print 'opening:' + file
    webbrowser.open(file)

''' private logic '''

def _listAll(obj):
    objDict = obj.__dict__
    print('\n---------------- ')
    print(objDict)
    # for value in obj.commits:
    #     print(value.__dict__)
    print('------------------\n')

def _checkOutputDir():
    if not os.path.isdir('output'):
        os.makedirs('output/pages')


''' entry '''

def parseArgv():
    try:
        opts, argv_rest = getopt.getopt(sys.argv[1:], "dhv", ["help","info="])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    if not opts:
      usage()

    try:
        for o, a in opts:
            if o == '-d':   diffTool(argv_rest)
            if o in ("-h", "--help"):   usage()
            if o in ("-v", "--version"):   print __version__; return
    except ValueError as err:
        print str(err)
        usage()


# you can run the functions of the module or some test methods here
def main():
    # check arguments
    parseArgv()

if __name__ == "__main__":
    main()
