from parse_context import compareBeanDefs
from compare_xml import compareXML
import getopt
import sys
import os
import re
import filecmp
import difflib
import sys
import json
from common import actionRequired, info, warning, error

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
                    actionRequired("Conflicting customization", "", srcFileList[srcFile]["path"],os.path.join(dirName, fileName))
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
                if srcFile in customFiles:
                    srcFileList[srcFile] = { 
                        "path": os.path.join(dirName, fileName),
                        "dir": dirName,
                        "file": fileName,
                    }
        return srcFileList


    def compareFiles(self, customFiles, oldFiles, newFiles):
        for customFile in customFiles:
            if customFile in oldFiles and customFile in newFiles:
                info("file in all versions:" + customFile)
                if filecmp.cmp(oldFiles[customFile]['path'], newFiles[customFile]['path']):
                    info("No change between versions:" + customFile)
                else:
                    actionRequired("Different file:", customFiles[customFile]['path'], oldFiles[customFile]['path'], newFiles[customFile]['path'])
                    fromfile = oldFiles[customFile]['path']
                    tofile = newFiles[customFile]['path']
                    with open(fromfile) as fromf, open(tofile) as tof:
                        fromlines, tolines = list(fromf), list(tof)
                    diff = difflib.context_diff(fromlines, tolines)

                    sys.stdout.writelines(diff) 
            elif customFile in oldFiles:
                info("file not in new version:" + customFile)
            elif customFile in newFiles:
                info("file not in old version:" + customFile)
            else:
                info("file only in custom code:" + customFile + ":" + customFiles[customFile]['path'])


    def findDef(self, defList, defName, mapping):
        fileDef = None
        if defName in defList:
            fileDef = defList[defName]

        if not fileDef:
            if "files" in mapping and defName in mapping["files"]:
                info("Found mapping config")
                mappedFile = mapping["files"][defName]
                if "reference-file" in mappedBean and mappedFile["reference-file"] in defList:
                    info("Using " + mappedFile["reference-file"] + " instead of " + defName)
                    fileDef = defList[mappedFile["reference-file"]]
        return fileDef

    def run(self, customPath, oldPath, newPath):

        mappings = {}

        mappingsFile = os.path.join(customPath, "upgrade-assist.mapping.json")
        if os.path.isfile(mappingsFile):
            with (open(mappingsFile)) as json_data:
                mappings = json.load(json_data)
        extHomes = [ "src/main/amp/config/alfresco/extension", "src/main/resources/alfresco/extension"]
        customFiles = self.collectExtensions(customPath, extHomes)

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

    compareBeanDefs(customPath, oldPath, newPath)

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
    compareXML(myXML, oldXML, newXML)
