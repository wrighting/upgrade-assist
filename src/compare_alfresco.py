from parse_context import compareBeanDefs
from compare_xml import compareXML
import getopt
import sys
import os

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'v', ['version'])
    except getopt.GetOptError:
        sys.exit(1)
    customPath = args[0]
    oldPath = os.path.join(args[1], args[2])
    newPath = os.path.join(args[1], args[3])
     
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
