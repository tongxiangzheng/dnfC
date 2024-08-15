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
	with os.popen("/usr/bin/dnf list --installed") as f:
		data=f.readlines()
		tmp=packageName+'/'
		for info in data:
			if info.startswith(tmp):
				dist=info.split(',')[0].split('/')[1]
				version_release=info.split(',')[1].split('-')
				version=version_release[0]
				release=None
				if len(version_release)>1:
					release=version_release[1]
				#print(packageName,dist,version,release)
				return sourcesListManager.getSpecificPackage(packageName,dist,version,release)
	print("error")
	return None

def getDependes(package:SpecificPackage.SpecificPackage,dependesSet:set):
	if package in dependesSet:
		return
	dependesSet.add(package)
	for p in package.requirePointers:
		getDependes(p,dependesSet)		
def getNewInstall(args,sourcesListManager:SourcesListManager.SourcesListManager)->dict:
	cmd="/usr/bin/dnf --assumeno"
	argset=set(args)
	for arg in args:
		cmd+=' '+arg
	installPackages=[]
	#log.info('cmd is '+cmd)
	#actualPackageName=packageName
	installInfoSection=False
	p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	for info in data:
		if installInfoSection is True:
			info=info.strip()
			if len(info)==0:
				continue
			if info=="Installing dependencies:":
				continue
			if info=="Transaction Summary" or info=="Enabling module streams:":
				break
			installPackages.append(parseInstallInfo(info,sourcesListManager))
		elif info.startswith('Installing:'):
			installInfoSection=True
	selectedPackages=[]
	entryMap=SpecificPackage.EntryMap()
	for p in installPackages:
		p.registerProvides(entryMap)
		if p.fullName in argset:
			selectedPackages.append(p)
	for p in installPackages:
		p.findRequires(entryMap)
	res=dict()
	for p in selectedPackages:
		depends=set()
		getDependes(p,depends)
		res[p]=list(depends)
	return res