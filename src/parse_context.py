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

    ET.register_namespace('bean',nsbeansuri)
    for dirName, subdirList, fileList in os.walk(startDir):
        if re.match('.*/(target|\.svn|alf_data_dev)/.*', dirName):
            continue
        if True: #re.match('^(.*/templates/.*)', dirName):
            for fileName in fileList:
                if re.match('.*\.xml$', fileName):
                    filePath = os.path.join(dirName,fileName)
                    idList.update(collectBeansFromFile(filePath))
#                    print "Parsing:" + filePath
#    print str(idList)
    return idList

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
        myAsString = ET.tostring(bean1, encoding="utf-8")
        newAsString = ET.tostring(bean2, encoding="utf-8")
        for line in difflib.context_diff( \
                             map(preDiffProcess,myAsString.splitlines(1)),\
                             map(preDiffProcess,newAsString.splitlines(1))):
            sys.stdout.write(line)
        print
    else:
        info("Bean definitions match")

    return cmpResult

def actionRequired(message, customFile, oldFile, newFile):
    print
    print "You need to check: " + customFile
    print message
    print "Old file:" + oldFile
    print "New file:" + newFile
    print 
    
def info(message):
#    print message
    pass
    
def warning(message):
#    print message
    pass

def error(message):
    print message
    pass

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'v', ['version'])
    except getopt.GetOptError:
        sys.exit(1)
    customPath = args[0]
    myIdList = collectBeanIds(customPath)
#    print str(myIdList)
    oldPath = os.path.join(args[1], args[2])
    oldIdList = collectBeanIds(oldPath)
#    print str(oldIdList)
    newPath = os.path.join(args[1], args[3])
    newIdList = collectBeanIds(newPath)
    
    for beanDef in myIdList:
        if beanDef in oldIdList and beanDef in newIdList:
            info("BeanDef in all versions:" + beanDef)
            if compareBeans(oldIdList[beanDef]['element'],\
                            newIdList[beanDef]['element']) == 0:
                if myIdList[beanDef]['element'].get('class') == newIdList[beanDef]['element'].get('class') and newIdList[beanDef]['element'].get('class') == oldIdList[beanDef]['element'].get('class'):
                    info("No change so can keep same customization for:" + beanDef)
                else:
                    info("Custom class is being used:" + myIdList[beanDef]['element'].get('class'))
                    info("Checking java for:" + oldIdList[beanDef]['element'].get('class') + " " + newIdList[beanDef]['element'].get('class'))
                    oldSource = ""
                    for c in locateClass(oldIdList[beanDef]['element'].get('class'), oldPath):
                        oldSource = c
                    newSource = ""
                    for c in locateClass(newIdList[beanDef]['element'].get('class'), newPath):
                        newSource = c
                    if oldSource == "":
                            error("Cannot find java for class:" + oldIdList[beanDef]['element'].get('class'))
                    if newSource == "":
                            error("Cannot find java for class:" + newIdList[beanDef]['element'].get('class'))
                    try: 
                        if filecmp.cmp(oldSource, newSource):
                            info("Same java:" + oldSource + " " + newSource)
                        else:
                            mySource = ""
                            for c in locateClass(myIdList[beanDef]['element'].get('class'), customPath):
                                mySource = c
                            if mySource == "":
                                error("Cannot find java for class:" + myIdList[beanDef]['element'].get('class'))
                            actionRequired("Different java between versions", mySource, oldSource, newSource)
                    except OSError, ose:
                        print ose
            else:
                actionRequired("Different bean definition:", myIdList[beanDef]['path'], oldIdList[beanDef]['path'], oldIdList[beanDef]['path']) 
                compareBeans(myIdList[beanDef]['element'], oldIdList[beanDef]['element'])
        elif beanDef in oldIdList:
            print "BeanDef not in new version:" + beanDef
            print "Custom file:" + myIdList[beanDef]['path'] 
            print "Old version file:" + oldIdList[beanDef]['path'] 
            compareBeans(myIdList[beanDef]['element'], oldIdList[beanDef]['element'])
        elif beanDef in newIdList:
            print "BeanDef not in old version:" + beanDef 
            print "Custom file:" + myIdList[beanDef]['path'] 
            print "New version file:" + newIdList[beanDef]['path'] 
            compareBeans(myIdList[beanDef]['element'], newIdList[beanDef]['element'])
        else:
            info("BeanDef only in custom code:" + beanDef + ":" + myIdList[beanDef]['path'])
