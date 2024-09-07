import os
import SpecificPackage
import SourcesListManager
from subprocess import PIPE, Popen
from loguru import logger as log
def parseInstallInfo(info:list,sourcesListManager:SourcesListManager.SourcesListManager)->SpecificPackage.SpecificPackage:
	name=info[0]
	arch=info[1]
	version_release=info[2].split('-')
	version=version_release[0].split(':')[-1]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=info[3]
	specificPackage=sourcesListManager.getSpecificPackage(name,dist,version,release,arch)
	return specificPackage
def getInstalledPackageInfo(sourcesListManager:SourcesListManager.SourcesListManager):
	res=[]
	with os.popen("/usr/bin/dnf list --installed") as f:
		data=f.readlines()
		for info in data:
			dist=info.split(',')[0].split('/')[1]
			version_release=info.split(',')[1].split('-')
			version=version_release[0]
			release=None
			if len(version_release)>1:
				release=version_release[1]
			#print(packageName,dist,version,release)
			package=sourcesListManager.getSpecificPackage(packageName,dist,version,release)
			if package is not None:
				res.append(package)
	return res

def getDependes(package:SpecificPackage.SpecificPackage,dependesSet:set):
	if package in dependesSet:
		return
	dependesSet.add(package)
	for p in package.requirePointers:
		getDependes(p,dependesSet)		
def getNewInstall(args,sourcesListManager:SourcesListManager.SourcesListManager,includeInstalled=False)->dict:
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
	data=stdout.decode()
	data=data.split('\n')
	i=-1
	while i < len(data):
		i+=1
		info=data[i]
		if info.startswith('Error: This command has to be run with superuser privileges'):
			return {}
		if installInfoSection is True:
			info=info.strip()
			if len(info)==0:
				continue
			if info=="Installing dependencies:" or info=="Installing weak dependencies:":
				continue
			if info=="Transaction Summary" or info=="Enabling module streams:":
				break
			info=info.split()
			while len(info) < 6:
				i+=1
				info.extend(data[i].strip().split())
			installPackages.append(parseInstallInfo(info,sourcesListManager))
		elif info.startswith('Installing:'):
			installInfoSection=True
	selectedPackages=[]
	entryMap=SpecificPackage.EntryMap()
	for p in installPackages:
		p.registerProvides(entryMap)
		if p.fullName in argset:
			selectedPackages.append(p)
	if includeInstalled is True:
		installedPackages=getInstalledPackageInfo()
		for p in installPackages:
			p.registerProvides(entryMap)
	for p in installPackages:
		p.findRequires(entryMap)
	if includeInstalled is True:
		for p in installPackages:
			p.findRequires(entryMap)
	res=dict()
	for p in selectedPackages:
		depends=set()
		getDependes(p,depends)
		res[p]=list(depends)
	return res