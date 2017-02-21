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

import report

class JavaCompare(object):
        
    nsbeansuri = 'http://www.springframework.org/schema/beans'
    nsbeans = '{' + nsbeansuri +'}'
    
    def __init__(self, reporter):
        
        self.reporter = reporter
        
    def findDef(self, defList, defName, mapping):
        beanDef = None
        if defName in defList:
            beanDef = defList[defName]
    
        if not beanDef:
            if "beans" in mapping and defName in mapping["beans"]:
                self.reporter.info("Found mapping config")
                mappedBean = mapping["beans"][defName]
                if "reference-bean-id" in mappedBean and mappedBean["reference-bean-id"] in defList:
                    self.reporter.info("Using " + mappedBean["reference-bean-id"] + " instead of " + defName)
                    beanDef = defList[mappedBean["reference-bean-id"]]
        return beanDef
    

    def compareJava(self, customPath, oldPath, newPath, myDef, oldDef, newDef):
        self.reporter.info("Custom class is being used:" + myDef['element'].get('class'))
        self.reporter.info("Checking java for:" + oldDef['element'].get('class') + " " + newDef['element'].get('class'))
        oldSource = ""
        for c in self.locateClass(oldDef['element'].get('class'), oldPath):
            oldSource = c
        
        newSource = ""
        for c in self.locateClass(newDef['element'].get('class'), newPath):
            newSource = c
        
        if oldSource == "":
            self.reporter.error("Cannot find java for class:" + oldDef['element'].get('class'))
        if newSource == "":
            self.reporter.error("Cannot find java for class:" + newDef['element'].get('class'))
        try:
            if filecmp.cmp(oldSource, newSource):
                self.reporter.info("Same java:" + oldSource + " " + newSource)
            else:
                mySource = ""
                for c in self.locateClass(myDef['element'].get('class'), customPath):
                    mySource = c
                
                if mySource == "":
                    self.reporter.error("Cannot find java for class:" + myDef['element'].get('class'))
                self.reporter.actionRequired("Different java between versions", mySource, oldSource, newSource)
                fromfile = oldSource
                tofile = newSource
                with open(fromfile) as fromf, open(tofile) as tof:
                    fromlines, tolines = list(fromf), list(tof)
                diff = difflib.context_diff(fromlines, tolines, fromfile=oldSource, tofile=newSource)

                sys.stdout.writelines(diff) 
        except OSError as ose:
            print(ose)

    def compareBeanDefs(self, customPath, oldPath, newPath):
    
        mappings = {}
    
    #    print (os.path.join(customPath, "upgrade-assist.mapping.json"))
        mappingFile = os.path.join(customPath, "upgrade-assist.mapping.json")
        if os.path.isfile(mappingFile):
            with (open(mappingFile)) as json_data:
                mappings = json.load(json_data)
    
        myIdList, myOtherXML = self.collectBeanIds(customPath) #    print str(myIdList)
        oldIdList, oldOtherXML = self.collectBeanIds(oldPath)
    #    print str(oldIdList)
        newIdList, newOtherXML = self.collectBeanIds(newPath)
        for beanDef in myIdList:
            myDef = self.findDef(myIdList, beanDef, mappings)
            oldDef = self.findDef(oldIdList, beanDef, mappings)
            newDef = self.findDef(newIdList, beanDef, mappings)
            if oldDef and newDef:
                self.reporter.info("BeanDef in all versions:" + beanDef)
                if self.compareBeans(oldDef['element'], newDef['element']) == 0:
                    if myDef['element'].get('class') == newDef['element'].get('class') and newDef['element'].get('class') == oldDef['element'].get('class'):
                        self.reporter.info("No change so can keep same customization for:" + beanDef)
                    else:
                        self.compareJava(customPath, oldPath, newPath, myDef, oldDef, newDef)
                else:
                    self.reporter.actionRequired("Different bean definition:", myDef['path'], oldDef['path'], newDef['path'])
                    self.compareBeans(myDef['element'], oldDef['element'])
            elif oldDef:
                self.reporter.info("BeanDef not in new version:" + beanDef)
                self.reporter.info("Custom file:" + myDef['path'])
                self.reporter.info("Old version file:" + oldDef['path'])
                self.compareBeans(myDef['element'], oldDef['element'])
            elif newDef:
                self.reporter.info("BeanDef not in old version:" + beanDef)
                self.reporter.info("Custom file:" + myDef['path'])
                self.reporter.info("New version file:" + newDef['path'])
                self.compareBeans(myDef['element'], newDef['element'])
            else:
                self.reporter.info("BeanDef only in custom code:" + beanDef + ":" + myDef['path'])
        
        return myIdList, myOtherXML, oldIdList, oldOtherXML, newIdList, newOtherXML
    

    
    
    def parseContextFile(self, tree, xpath, namespaces):
        ids = []
        for bean in tree.findall(xpath, namespaces):
            if 'id' in bean.attrib:
    #            bean.
                ids.append({ 'id': bean.attrib['id'], 'element': copy.deepcopy(bean)})
    #        else:
    #            print "Bean missing Id" + str(bean)
        return ids
    
    def collectBeansFromFile(self, filePath):
        idList = {}
        try:
            tree = ET.parse(filePath)
        except ET.ParseError:
    #        print "Parse error:" + filePath
            return idList
        #for bean in parseContextFile(tree,nsbeans + 'bean', {'bean': nsbeansuri}):
        for bean in self.parseContextFile(tree,self.nsbeans + 'bean', {}):
            bean['path'] = filePath
            idList[bean['id']] = copy.deepcopy(bean)
    #                        print "Adding beanId1:" + bean['id']
        #for bean in parseContextFile(tree,'bean', {'xmlns': nsbeansuri}):
        for bean in self.parseContextFile(tree,'bean', {}):
            bean['path'] = filePath
            idList[bean['id']] = copy.deepcopy(bean)
    #        print "Adding beanId2:" + bean['id']
    
        return idList
    
    def collectBeanIds(self, startDir):
        idList = {}
        otherXML = {}
        
        ET.register_namespace('bean',self.nsbeansuri)
        for dirName, subdirList, fileList in os.walk(startDir):
            if re.match('.*/(target|\.svn|alf_data_dev)/.*', dirName):
                continue
            if True: #re.match('^(.*/templates/.*)', dirName):
                for fileName in fileList:
                    if re.match('.*\.xml$', fileName):
                        filePath = os.path.join(dirName,fileName)
                        beans = self.collectBeansFromFile(filePath)
                        if beans:
                            idList.update(beans)
                        else:
                            key = filePath.replace(startDir,'')
                            otherXML[key] = { 'path': filePath }
                            #print ("No beans in:" + key + ':' + filePath)
    #                    print "Parsing:" + filePath
    #    print str(idList)
        return idList, otherXML
    
    def locateClass(self, className, root=os.curdir):
        '''Locate all files matching supplied filename pattern in and below
        supplied root directory.'''
        for path, dirs, files in os.walk(os.path.abspath(root)):
            pattern = className.split(".")[-1].rstrip() + '.java'
            #for filename in fnmatch.filter(files, pattern):
            if pattern in files:
                yield os.path.join(path, pattern)
    
    def preDiffProcess(self, inString):
        return inString
    #Less results but harder to read
    #    return inString.translate(None, string.whitespace)
    
    def compareBeans(self, bean1, bean2):
        cmpResult = xmlUtil.cmp_el(bean1, bean2)
        if cmpResult != 0:
            myAsString = ET.tostring(bean1, encoding="unicode")
            newAsString = ET.tostring(bean2, encoding="unicode")
            for line in difflib.context_diff( \
                                 list(map(self.preDiffProcess, myAsString.splitlines(True))),\
                                 list(map(self.preDiffProcess, newAsString.splitlines(True)))):
                sys.stdout.write(line)
            print()
        else:
            self.reporter.info("Bean definitions match")
    
        return cmpResult



if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'v', ['version'])
    except getopt.GetOptError:
        sys.exit(1)
    customPath = args[0]
    oldPath = os.path.join(args[1], args[2])
    newPath = os.path.join(args[1], args[3])
     
    jc = JavaCompare(Report())
    jc.compareBeanDefs(customPath, oldPath, newPath)
            
   
