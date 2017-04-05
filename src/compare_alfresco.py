import getopt
import sys
import os
import re
import filecmp
import difflib
import sys
import json

import report
import java_compare
import comparitor

class ScriptChecker():

    def collectExtensions(self, startDir, extHomes):
        srcFileList = {}
        for dirName, subdirList, fileList in os.walk(startDir):
            if re.match('.*/(target|\.svn|\.git|alf_data_dev)/.*', dirName):
                continue
            srcRoot = None
            for extHome in extHomes:
                match = re.match('(.*/' + extHome + ')(/.*)', dirName)
                if match:
                    srcRoot = match.group(2)
            if not srcRoot:
                continue
            for fileName in fileList:
                srcFile = os.path.join(srcRoot, fileName)
                if srcFile in srcFileList:
                    self.reporter.actionRequired("Conflicting customization", "", srcFileList[srcFile]["path"],os.path.join(dirName, fileName))
                else:
                    srcFileList[srcFile] = { 
                        "path": os.path.join(dirName, fileName),
                        "dir": dirName,
                        "file": fileName,
                        "srcRoot": srcRoot
                    }
        return srcFileList

    def collectOriginals(self, startDir, customFiles):
        srcFileList = {}
        for dirName, subdirList, fileList in os.walk(startDir):
            if re.match('.*/(target|\.svn|alf_data_dev)/.*', dirName):
                continue
            found = False
            for key, value in customFiles.items():
                match = re.match('.*'+value["srcRoot"], dirName)
                if match:
                    found = True
            if not found:
                continue
            for fileName in fileList:
                srcFile = os.path.join(value["srcRoot"], fileName)
                orig = os.path.join(dirName, fileName)
                for custom in customFiles:
                    if orig.endswith(custom):
                        srcFileList[custom] = { 
                            "path": orig,
                            "dir": dirName,
                            "file": fileName,
                        }
                    
        return srcFileList


    def compareFiles(self, customFiles, oldFiles, newFiles):
        for customFile in customFiles:
            if customFile in oldFiles and customFile in newFiles:
                self.reporter.info("file in all versions:" + customFile)
                if filecmp.cmp(oldFiles[customFile]['path'], newFiles[customFile]['path']):
                    self.reporter.info("No change between versions:" + customFile)
                else:
                    msg = "Different file:"
                    if "bean" in customFiles[customFile]:
                        msg = "Implementation in bean:" + customFiles[customFile]['bean'] + " defined in " + customFiles[customFile]['beanDef']['path']
                    self.reporter.actionRequired(msg, customFiles[customFile]['path'], oldFiles[customFile]['path'], newFiles[customFile]['path'])
                    fromfile = oldFiles[customFile]['path']
                    tofile = newFiles[customFile]['path']
                    with open(fromfile) as fromf, open(tofile) as tof:
                        fromlines, tolines = list(fromf), list(tof)
                    diff = difflib.context_diff(fromlines, tolines, fromfile=fromfile, tofile=tofile)

                    sys.stdout.writelines(diff) 
            elif customFile in oldFiles:
                self.reporter.info("file not in new version:" + customFile)
            elif customFile in newFiles:
                self.reporter.info("file not in old version:" + customFile)
            else:
                self.reporter.info("file only in custom code:" + customFile + ":" + customFiles[customFile]['path'])


    def findDef(self, defList, defName, mapping):
        fileDef = None
        if defName in defList:
            fileDef = defList[defName]

        if not fileDef:
            if "files" in mapping and defName in mapping["files"]:
                self.reporter.info("Found mapping config")
                mappedFile = mapping["files"][defName]
                if "reference-file" in mappedFile and mappedFile["reference-file"] in defList:
                    self.reporter.info("Using " + mappedFile["reference-file"] + " instead of " + defName)
                    fileDef = defList[mappedFile["reference-file"]]
        return fileDef

    def run(self, customPath, oldPath, newPath):

        mappings = {}

        mappingsFile = os.path.join(customPath, "upgrade-assist.mapping.json")
        if os.path.isfile(mappingsFile):
            with (open(mappingsFile)) as json_data:
                mappings = json.load(json_data)

        self.reporter = report.Report()

        extHomes = [ "src/main/amp/config/alfresco/extension", "src/main/resources/alfresco/extension"]
        customFiles = self.collectExtensions(customPath, extHomes)
        jc = java_compare.JavaCompare(customPath, self.reporter)
        self.comparitor = comparitor.Comparitor(self.reporter)

        myIdList, myOtherXML, oldIdList, oldOtherXML, newIdList, newOtherXML = jc.compareBeanDefs(oldPath, newPath)
        jc.compareAspects(oldPath, newPath)

        for bean in myIdList:
            beanDef = myIdList[bean]
            if not "beans" in mappings:
                continue
            if bean in mappings["beans"]:
                self.reporter.info("Found mapping config")
                mapping = mappings["beans"][bean]
                if 'files' in mapping:
                    for mappedFile in mapping['files']:
                        self.reporter.info("bean " + bean + " script " + mappedFile)
                        customFiles[mappedFile] = {
                            "path": mappedFile,
                            "srcRoot": os.path.dirname(mappedFile),
                            "bean": bean,
                            "beanDef": beanDef
                            }


        oldFiles = self.collectOriginals(oldPath, customFiles)
        newFiles = self.collectOriginals(newPath, customFiles)

        self.compareFiles(customFiles, oldFiles, newFiles)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'v', ['version'])
    except getopt.GetOptError:
        sys.exit(1)
    customPath = args[0]
    oldPath = os.path.join(args[1], args[2])
    newPath = os.path.join(args[1], args[3])

    checker = ScriptChecker()
    checker.run(customPath, oldPath, newPath)

    
    myXML = {
              'repo-web.xml': { 'path': ''}, 
              'share-web.xml': { 'path': ''},
              'share-config-custom.xml': { 'path': ''}
             }

    oldXML = {
              'repo-web.xml': { 'path': os.path.join(oldPath,'repo/root/projects/web-client/source/web/WEB-INF/web.xml')}, 
#              'share-web.xml': { 'path': os.path.join(oldPath,'share/share/src/main/webapp/WEB-INF/web.xml')},
              'share-web.xml': { 'path': os.path.join(oldPath,'share/WEB-INF/web.xml')},
              'share-config-custom.xml': { 'path': os.path.join(oldPath,'repo/root/packaging/installer/src/main/resources/bitrock/bitrock/alfresco/shared/web-extension/share-config-custom.xml')}
             }
             
    newXML = {
              'repo-web.xml': { 'path': os.path.join(newPath,'repo/root/projects/web-client/source/web/WEB-INF/web.xml')}, 
              'share-web.xml': { 'path': os.path.join(newPath,'share/share/src/main/webapp/WEB-INF/web.xml')},
              'share-config-custom.xml': { 'path': os.path.join(newPath,'repo/root/packaging/installer/src/main/resources/bitrock/bitrock/alfresco/shared/web-extension/share-config-custom.xml')}
             }
    checker.comparitor.compareXML(myXML, oldXML, newXML)
