import os
import SpecificPackage
import SourcesListManager
from subprocess import PIPE, Popen
from loguru import logger as log
def parseInstallInfo(info:str,sourcesListManager:SourcesListManager.SourcesListManager)->SpecificPackage.SpecificPackage:
	info=info.strip().split()
	name=info[0]
	arch=info[1]
	version_release=info[2].split('-')
	version=version_release[0]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=info[3]
	specificPackage=sourcesListManager.getSpecificPackage(name,dist,version,release,arch)
	#specificPackage.setGitLink()
	return specificPackage
def getInstalledPackageInfo(packageName,sourcesListManager:SourcesListManager.SourcesListManager):
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
			res.append(parseInstallInfo(info,sourcesListManager))
		elif info.startswith('Installing:'):
			installInfoSection=True
	selectedPackage=None
	for p in res:
		if p.fullName==packageName:
			selectedPackage=p
	if selectedPackage is None:
		for p in res:
			print(p.fullName)
			for provide in p.providesInfo:
				if provide.name==packageName:
					selectedPackage=p
	#if selectedPackage is None:
	return selectedPackage,res