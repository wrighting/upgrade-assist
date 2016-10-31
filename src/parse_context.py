import os
import getopt
import sys
import re
import xml.etree.ElementTree as ET
import string
import difflib
import xmlUtil
import copy
import fnmatch
import filecmp
import json

from common import actionRequired, info, warning, error

def findDef(defList, defName, mapping):
    beanDef = None
    if defName in defList:
        beanDef = defList[defName]

    if not beanDef:
        if "beans" in mapping and defName in mapping["beans"]:
            info("Found mapping config")
            mappedBean = mapping["beans"][defName]
            if "reference-bean-id" in mappedBean and mappedBean["reference-bean-id"] in defList:
                info("Using " + mappedBean["reference-bean-id"] + " instead of " + defName)
                beanDef = defList[mappedBean["reference-bean-id"]]
    return beanDef

def compareBeanDefs(customPath, oldPath, newPath):

    mappings = {}

#    print (os.path.join(customPath, "upgrade-assist.mapping.json"))
    mappingFile = os.path.join(customPath, "upgrade-assist.mapping.json")
    if os.path.isfile(mappingFile):
        with (open(mappingFile)) as json_data:
            mappings = json.load(json_data)

    myIdList, myOtherXML = collectBeanIds(customPath) #    print str(myIdList)
    oldIdList, oldOtherXML = collectBeanIds(oldPath)
#    print str(oldIdList)
    newIdList, newOtherXML = collectBeanIds(newPath)
    for beanDef in myIdList:
        myDef = findDef(myIdList, beanDef, mappings)
        oldDef = findDef(oldIdList, beanDef, mappings)
        newDef = findDef(newIdList, beanDef, mappings)
        if oldDef and newDef:
            info("BeanDef in all versions:" + beanDef)
            if compareBeans(oldDef['element'], 
                newDef['element']) == 0:
                if myDef['element'].get('class') == newDef['element'].get('class') and newDef['element'].get('class') == oldDef['element'].get('class'):
                    info("No change so can keep same customization for:" + beanDef)
                else:
                    info("Custom class is being used:" + myDef['element'].get('class'))
                    info("Checking java for:" + oldDef['element'].get('class') + " " + newDef['element'].get('class'))
                    oldSource = ""
                    for c in locateClass(oldDef['element'].get('class'), oldPath):
                        oldSource = c
                    
                    newSource = ""
                    for c in locateClass(newDef['element'].get('class'), newPath):
                        newSource = c
                    
                    if oldSource == "":
                        error("Cannot find java for class:" + oldDef['element'].get('class'))
                    if newSource == "":
                        error("Cannot find java for class:" + newDef['element'].get('class'))
                    try:
                        if filecmp.cmp(oldSource, newSource):
                            info("Same java:" + oldSource + " " + newSource)
                        else:
                            mySource = ""
                            for c in locateClass(myDef['element'].get('class'), customPath):
                                mySource = c
                            
                            if mySource == "":
                                error("Cannot find java for class:" + myDef['element'].get('class'))
                            actionRequired("Different java between versions", mySource, oldSource, newSource)
                    except OSError as ose:
                        print (ose)
            else:
                actionRequired("Different bean definition:", myDef['path'], oldDef['path'], newDef['path'])
                compareBeans(myDef['element'], oldDef['element'])
        elif oldDef:
            print("BeanDef not in new version:" + beanDef)
            print("Custom file:" + myDef['path'])
            print("Old version file:" + oldDef['path'])
            compareBeans(myDef['element'], oldDef['element'])
        elif newDef:
            print("BeanDef not in old version:" + beanDef)
            print("Custom file:" + myDef['path'])
            print("New version file:" + newDef['path'])
            compareBeans(myDef['element'], newDef['element'])
        else:
            info("BeanDef only in custom code:" + beanDef + ":" + myDef['path'])
    
    return myOtherXML, oldOtherXML, newOtherXML

nsbeansuri = 'http://www.springframework.org/schema/beans'
nsbeans = '{' + nsbeansuri +'}'


def parseContextFile(tree, xpath, namespaces):
    ids = []
    for bean in tree.findall(xpath, namespaces):
        if 'id' in bean.attrib:
#            bean.
            ids.append({ 'id': bean.attrib['id'], 'element': copy.deepcopy(bean)})
#        else:
#            print "Bean missing Id" + str(bean)
    return ids

def collectBeansFromFile(filePath):
    idList = {}
    try:
        tree = ET.parse(filePath)
    except ET.ParseError:
#        print "Parse error:" + filePath
        return idList
    #for bean in parseContextFile(tree,nsbeans + 'bean', {'bean': nsbeansuri}):
    for bean in parseContextFile(tree,nsbeans + 'bean', {}):
        bean['path'] = filePath
        idList[bean['id']] = copy.deepcopy(bean)
#                        print "Adding beanId1:" + bean['id']
    #for bean in parseContextFile(tree,'bean', {'xmlns': nsbeansuri}):
    for bean in parseContextFile(tree,'bean', {}):
        bean['path'] = filePath
        idList[bean['id']] = copy.deepcopy(bean)
#        print "Adding beanId2:" + bean['id']

    return idList

def collectBeanIds(startDir):
    idList = {}
    otherXML = {}
    
    ET.register_namespace('bean',nsbeansuri)
    for dirName, subdirList, fileList in os.walk(startDir):
        if re.match('.*/(target|\.svn|alf_data_dev)/.*', dirName):
            continue
        if True: #re.match('^(.*/templates/.*)', dirName):
            for fileName in fileList:
                if re.match('.*\.xml$', fileName):
                    filePath = os.path.join(dirName,fileName)
                    beans = collectBeansFromFile(filePath)
                    if beans:
                        idList.update(beans)
                    else:
                        key = filePath.replace(startDir,'')
                        otherXML[key] = { 'path': filePath }
                        #print ("No beans in:" + key + ':' + filePath)
#                    print "Parsing:" + filePath
#    print str(idList)
    return idList, otherXML

def locateClass(className, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        pattern = className.split(".")[-1].rstrip() + '.java'
        #for filename in fnmatch.filter(files, pattern):
        if pattern in files:
            yield os.path.join(path, pattern)

def preDiffProcess(inString):
    return inString
#Less results but harder to read
#    return inString.translate(None, string.whitespace)

def compareBeans(bean1, bean2):
    cmpResult = xmlUtil.cmp_el(bean1, bean2)
    if cmpResult != 0:
        myAsString = ET.tostring(bean1, encoding="unicode")
        newAsString = ET.tostring(bean2, encoding="unicode")
        for line in difflib.context_diff( \
                             list(map(preDiffProcess, myAsString.splitlines(True))),\
                             list(map(preDiffProcess, newAsString.splitlines(True)))):
            sys.stdout.write(line)
        print()
    else:
        info("Bean definitions match")

    return cmpResult



if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'v', ['version'])
    except getopt.GetOptError:
        sys.exit(1)
    customPath = args[0]
    oldPath = os.path.join(args[1], args[2])
    newPath = os.path.join(args[1], args[3])
     
    compareBeanDefs(customPath, oldPath, newPath)
            
   
