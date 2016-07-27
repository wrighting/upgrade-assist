MIRROR=alfresco-open-mirror
ALF_DIR=alfresco/
OLD=5.0.d
NEW=5.1.g
DEST=${ALF_DIR}${MIRROR}
#Quick and easy way to remove failed attempts
rmdir ${DEST}/*/*
for i in ${OLD} ${NEW}
do
	MAJOR_VERSION=`echo -n $i | awk -F. '{print $1}'`
	MINOR_VERSION=`echo -n $i | awk -F. '{print $2}'`
	mkdir -p ${DEST}/${i}/share
	if [ ${MAJOR_VERSION} -ge 5 -a ${MINOR_VERSION} -ge 1 ]
	then
		svn checkout  https://svn.alfresco.com/repos/${MIRROR}/web-apps/Share/tags/${i} ${DEST}/${i}/share
	else
		#For 4.2
		#mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR} -Dclassifier=config
		mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR} 
	fi
	#svn checkout  https://svn.alfresco.com/repos/${MIRROR}/web-apps/Share/trunk/${i} ${MIRROR}/${i}/share
	#mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR}

	#For versions prior to 5.0
	mkdir -p ${DEST}/${i}/repo
	CHECKOUT_VERSION=V${i}
	if [ ${MAJOR_VERSION} -ge 5 -a ${MINOR_VERSION} -ge 1 ]
	then
		CHECKOUT_VERSION=${i}
	fi
	svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/COMMUNITYTAGS/${CHECKOUT_VERSION} ${DEST}/${i}/repo
#		svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/HEAD ${DEST}/${i}/repo
done
export PYTHONPATH=${PYTHONPATH}:./src
python3 src/compare_alfresco.py ../my-alfresco-extensions ${DEST} ${OLD} ${NEW}
