import os
import getopt
import sys
import re
import xml.etree.ElementTree as ET
import string
import difflib
import xmlUtil
import copy

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
        print "Parse error:" + filePath
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
    else:
        print "Bean definitions match"

    return cmpResult

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'v', ['version'])
    except getopt.GetOptError:
        sys.exit(1)
    startDir = args[0]
    myIdList = collectBeanIds(startDir)
#    print str(myIdList)
    oldIdList = collectBeanIds(os.path.join(args[1], args[2]))
#    print str(oldIdList)

    newIdList = collectBeanIds(os.path.join(args[1], args[3]))
    
    for beanDef in myIdList:
        if beanDef in oldIdList and beanDef in newIdList:
            print "BeanDef in all versions:" + beanDef
            if compareBeans(oldIdList[beanDef]['element'],\
                            newIdList[beanDef]['element']) == 0:
                print "No change so can keep same customization for:" + beanDef
            else:
                print "Compared BeanDef in new version:" + oldIdList[beanDef]['path'] 
                print "Compared BeanDef in old version:" + newIdList[beanDef]['path'] 
                print "Comparing custom BeanDef with old version:" + myIdList[beanDef]['path'] 
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
            print "BeanDef only in custom code:" + beanDef + ":" + myIdList[beanDef]['path']
