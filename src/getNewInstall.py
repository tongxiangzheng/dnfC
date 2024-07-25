import os
import SpecificPackage
import SourcesListManager
from subprocess import PIPE, Popen
from loguru import logger as log
def getSelfDist():
	with open("/etc/os-release") as f:
		data=f.readlines()
		for info in data:
			if info.startswith('VERSION_CODENAME='):
				return info.strip()[17:]	
	return ""
dist=getSelfDist()
def parseInstallInfo(info:str,sourcesListManager:SourcesListManager.SourcesListManager)->SpecificPackage.SpecificPackage:
	info=info.strip().split(' ',2)
	name=info[1]
	additionalInfo=info[2][1:-2].split(' ')
	version_release=additionalInfo[0].split('-')
	version=version_release[0]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=additionalInfo[1].split('/')[1].split(',')[0]
	#arch=additionalInfo[-1][1:-1]
	#packageInfo=PackageInfo.PackageInfo('Ubuntu',dist,name,version,release,arch)
	specificPackage=sourcesListManager.getSpecificPackage(name,dist,version,release)
	specificPackage.setGitLink()
	return specificPackage
def getInstalledPackageInfo(packageName,sourcesListManager):
	#abandon
	log.warning("it's a abandon function")
	with os.popen("/usr/bin/apt list --installed") as f:
		data=f.readlines()
		tmp=packageName+'/'
		print(tmp)
		for info in data:
			if info.startswith(tmp):
				dist=info.split(',')[0].split('/')[1]
				version_release=info.split(',')[1].split('-')
				version=version_release[0]
				release=None
				if len(version_release)>1:
					release=version_release[1]
				print(packageName,dist,version,release)
				return sourcesListManager.getSpecificPackage(packageName,dist,version,release)
	print("error")
	return None

def getNewInstall(packageName:str,options,sourcesListManager:SourcesListManager.SourcesListManager):
	cmd="/usr/bin/dnf install --assumeno "
	for option in options:
		cmd+=option+' '
	cmd+=packageName
	res=[]
	#log.info('cmd is '+cmd)
	#actualPackageName=packageName
	installInfoSection=False
	p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	for info in data:
		if installInfoSection is True:
			info=info.strip()
			if info=="Installing dependencies:":
				continue
			if info=="Transaction Summary" or info=="Enabling module streams:":
				break
			print(info)
		elif info.startswith('Installing:'):
			installInfoSection=True
	return None,[]
	selectedPackage=None
	for p in res:
		if p.fullName==packageName:
			selectedPackage=p
	if selectedPackage is None:
		for p in res:
			print(p.fullName)
			for provide in p.providesInfo:
				if provide.name==packageName:
					print(provide.name)
					selectedPackage=p
	#if selectedPackage is None:
	return selectedPackage,res