MIRROR=alfresco-open-mirror
ALF_DIR=alfresco/
OLD=5.0.d
NEW=5.1.f
DEST=${ALF_DIR}${MIRROR}
#Quick and easy way to remove failed attempts
rmdir ${DEST}/*/*
for i in ${OLD} ${NEW}
do
	if [ ! -d ${DEST}/${i}/share ]
	then
		mkdir -p ${DEST}/${i}/share
		svn checkout  https://svn.alfresco.com/repos/${MIRROR}/web-apps/Share/tags/${i} ${DEST}/${i}/share
		#svn checkout  https://svn.alfresco.com/repos/${MIRROR}/web-apps/Share/trunk/${i} ${MIRROR}/${i}/share
		#mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR}
		#For versions prior to 5.0
		#mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR} -Dclassifier=config
	fi
	if [ ! -d ${DEST}/${i}/repo ]
	then
		mkdir -p ${DEST}/${i}/repo
		svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/COMMUNITYTAGS/${i} ${DEST}/${i}/repo
#		svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/HEAD ${DEST}/${i}/repo
	fi
done
export PYTHONPATH=${PYTHONPATH}:./src
python src/parse_context.py ../my-alfresco-extensions ${DEST} ${OLD} ${NEW}
