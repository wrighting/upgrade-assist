import filecmp
import difflib
import sys
from common import actionRequired, info, warning, error

def compareXML(myOtherXML, oldOtherXML, newOtherXML):
    for xmlFile in myOtherXML:
        if xmlFile in oldOtherXML and xmlFile in newOtherXML:
            info("XML file in all versions:" + xmlFile)
            if filecmp.cmp(oldOtherXML[xmlFile]['path'], newOtherXML[xmlFile]['path']):
                info("No change between versions:" + xmlFile)
            else:
                actionRequired("Different XML file:", myOtherXML[xmlFile]['path'], oldOtherXML[xmlFile]['path'], newOtherXML[xmlFile]['path'])
                fromfile = oldOtherXML[xmlFile]['path']
                tofile = newOtherXML[xmlFile]['path']
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

