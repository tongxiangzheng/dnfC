import nwkTools
from loguru import logger as log
import os
def getDscFile(repoURL,dscFileName):
	baseURL=repoURL
	try:
		dscFilePath=nwkTools.downloadFile(baseURL+dscFileName,os.path.join("/tmp","aptC","repoMetadata","dscFiles",dscFileName.rsplit('/',1)[0]),dscFileName.rsplit('/',1)[1])
		#os.chmod(dscFilePath, 0o744)
		return dscFilePath
	except Exception as e:
		#log.info("download failed : dsc file :"+dscFileName+" from "+baseURL+dscFileName)
		return None
def parseDscFile(dscFilePath):
	with open(dscFilePath,"r") as f:
		data=f.readlines()
	for info in data:
		info=info.strip()
		if info.startswith("Vcs-Git:") or info.startswith("Debian-Vcs-Git:"):
			return info.split(' ',1)[1]
def getGitLink(specPackageInfo):
	repoURL=specPackageInfo.repoURL
	if repoURL is None or specPackageInfo.fileName == "":
		return None
	version=specPackageInfo.fileName.rsplit('_',2)[1]
	source=specPackageInfo.source.split(' ')
	if len(source)>1:
		version=source[1].strip()[1:-1]
	dscFileName=specPackageInfo.fileName.rsplit('/',1)[0]+'/'+specPackageInfo.packageInfo.name+'_'+version+".dsc"
	dscFilePath=getDscFile(repoURL,dscFileName)
	if dscFilePath is None:
		return None
	gitLink=parseDscFile(dscFilePath)
	return gitLink
