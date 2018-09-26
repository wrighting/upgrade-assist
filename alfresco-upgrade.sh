MIRROR=alfresco-open-mirror
ALF_DIR=alfresco/
OLD_SHARE=5.1.g
NEW_SHARE=6.0.c
OLD_REPO=5.1.6
NEW_REPO=6.0.7
DEST=${ALF_DIR}${MIRROR}
#Quick and easy way to remove failed attempts
rmdir ${DEST}/*/*
for i in ${OLD_SHARE} ${NEW_SHARE}
do
	MAJOR_VERSION=`echo -n $i | awk -F. '{print $1}'`
	MINOR_VERSION=`echo -n $i | awk -F. '{print $2}'`
    if [[ ${MAJOR_VERSION} -ge 6 || (  ${MAJOR_VERSION} -ge 5 && ${MINOR_VERSION} -ge 1 ) ]]
    then
        test -d ${DEST}/${i}/share || git clone https://github.com/Alfresco/share.git ${DEST}/${i}/share
        (cd ${DEST}/${i}/share; git checkout tags/alfresco-share-parent-${i})
	else
		#For 4.2
		#mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR} -Dclassifier=config
		mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR} 
	fi
	#svn checkout  https://svn.alfresco.com/repos/${MIRROR}/web-apps/Share/trunk/${i} ${MIRROR}/${i}/share
	#mvn -f ${ALF_DIR}/pom.xml clean dependency:unpack -Dalfresco.version=${i} -DalternateLocation=${MIRROR}
done

for i in ${OLD_REPO} ${NEW_REPO}
do
	MAJOR_VERSION=`echo -n $i | awk -F. '{print $1}'`
	MINOR_VERSION=`echo -n $i | awk -F. '{print $2}'`
	#For versions prior to 5.0
	mkdir -p ${DEST}/${i}/repo
	CHECKOUT_VERSION=V${i}
	if [ ${MAJOR_VERSION} -ge 6 ]
	then
		CHECKOUT_VERSION=6.55
        TARGET=${DEST}/${i}/repo/alfresco-repository
        test -d ${TARGET} || git clone https://github.com/Alfresco/alfresco-repository.git ${TARGET}
        (cd ${TARGET}; git checkout tags/alfresco-repository-${CHECKOUT_VERSION})
		CHECKOUT_VERSION=6.19
        TARGET=${DEST}/${i}/repo/surf-webscripts
        test -d ${TARGET} || git clone https://github.com/Alfresco/surf-webscripts.git ${TARGET}
        (cd ${TARGET}; git checkout tags/${CHECKOUT_VERSION})
	elif [ ${MAJOR_VERSION} -ge 5 -a ${MINOR_VERSION} -ge 1 ]
    then
		CHECKOUT_VERSION=${i}
        svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/COMMUNITYTAGS/${CHECKOUT_VERSION} ${DEST}/${i}/repo
    else
        svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/COMMUNITYTAGS/${CHECKOUT_VERSION} ${DEST}/${i}/repo
#		svn checkout https://svn.alfresco.com/repos/${MIRROR}/alfresco/HEAD ${DEST}/${i}/repo
	fi
done
export PYTHONPATH=${PYTHONPATH}:./src
python3 src/compare_alfresco.py ../my-alfresco-extensions ${DEST} ${OLD_SHARE} ${NEW_SHARE}
python3 src/compare_alfresco.py ../my-alfresco-extensions ${DEST} ${OLD_REPO} ${NEW_REPO}
