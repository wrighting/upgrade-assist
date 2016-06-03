MIRROR=alfresco-open-mirror
ALF_DIR=alfresco/
OLD=4.2.f
NEW=5.0.d
#Quick and easy way to remove failed attempts
rmdir ${MIRROR}/*/*
for i in ${OLD} ${NEW}
do
	if [ ! -d ${MIRROR}/${i}/share ]
	then
		mkdir -p ${MIRROR}/${i}/share
		#svn checkout  https://svn.alfresco.com/repos/${MIRROR}/web-apps/Share/tags/${i} ${MIRROR}/${i}/share
		#svn checkout  https://svn.alfresco.com/repos/${MIRROR}/web-apps/Share/trunk/${i} ${MIRROR}/${i}/share
		mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR}
		#For versions prior to 5.0
		mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR} -Dclassifier=config
	fi
	if [ ! -d ${MIRROR}/${i}/repo ]
	then
		mkdir -p ${MIRROR}/${i}/repo
		#svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/COMMUNITYTAGS/${i} ${MIRROR}/${i}/repo
#		svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/HEAD ${MIRROR}/${i}/repo
	fi
done
export PYTHONPATH=${PYTHONPATH}:./src
python src/parse_context.py ../my-alfresco-extensions ${ALF_DIR}${MIRROR} ${OLD} ${NEW}
