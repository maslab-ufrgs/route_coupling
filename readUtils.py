#!/usr/bin/python
import re

def readNext(file):
    tmp = file.readline()
    if not tmp:
        return ""
    tmp = tmp.strip()
    while (len(tmp)==0):
        tmp = file.readline()
        if not tmp:
            return ""
        else:
            tmp = tmp.strip()
    return tmp
    
def readNextWithTag(file, tagName):
    tmp = readNext(file)
    regex = re.compile(r"%s (.*)" % tagName)
    return re.match(regex, tmp).group(1)

def readODName(file):
    tmp = readNext(file)
    regex = re.compile(r'.*\[ # (.*) flow')
    return re.match(regex, tmp).group(1)

def readSP(str):
    regex = re.compile(r'.*\[(.*)\].*cost (.*)') # first group is an unformatted list of links in a SP, second is the cost
    regex_linkName = re.compile(r'\'(.*)\',*')  # used to extract the link name from a string like    'name',

    links = re.match(regex, str).group(1)
    links = [i for i in links.split()]
    linkNames = []
    for i in links:
        name = re.match(regex_linkName, i).group(1)
        linkNames.append(name)

    cost  = re.match(regex, str).group(2)

    list_of_links = ' '.join(linkNames)
    return [list_of_links, cost]
    