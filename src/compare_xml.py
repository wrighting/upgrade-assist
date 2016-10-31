import filecmp
import difflib
import sys
from common import actionRequired, info, warning, error
import os

def compareXML(myOtherXML, oldOtherXML, newOtherXML):
    for xmlFile in myOtherXML:
        oldPath = oldOtherXML[xmlFile]['path']
        newPath = newOtherXML[xmlFile]['path']
        if xmlFile in oldOtherXML and os.path.isfile(oldPath) and xmlFile in newOtherXML and os.path.isfile(newPath):
            info("XML file in all versions:" + xmlFile)
            if filecmp.cmp(oldPath, newPath):
                info("No change between versions:" + xmlFile)
            else:
                actionRequired("Different XML file:", myOtherXML[xmlFile]['path'], oldPath, newPath)
                fromfile = oldPath
                tofile = newPath
                with open(fromfile) as fromf, open(tofile) as tof:
                    fromlines, tolines = list(fromf), list(tof)
                diff = difflib.context_diff(fromlines, tolines)

                sys.stdout.writelines(diff) 
        elif xmlFile in oldOtherXML:
            info("XML file not in new version:" + xmlFile)
        elif xmlFile in newOtherXML:
            info("XML file not in old version:" + xmlFile)
        else:
            info("XML file only in custom code:" + xmlFile + ":" + myOtherXML[xmlFile]['path'])

