import os
import SpecificPackage
import SourcesListManager
import RepoFileManager
import PackageInfo
import osInfo
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
def parseRequires(PackageName)->list:
	with os.popen("rpm -q --requires "+PackageName) as f:
		data=f.readlines()
		return RepoFileManager.parseRPMItemInfo(data)
def parseProvides(PackageName)->list:
	with os.popen("rpm -q --provides "+PackageName) as f:
		data=f.readlines()
		return RepoFileManager.parseRPMItemInfo(data)

def getSpecificInstalledPackage(fullName):
	p = Popen(f"/usr/bin/dnf -qi {fullName}", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	rpmhdr=dict()
	for item in data:
		pair=item.split(":",1)
		if len(pair)==2:
			pair[0]=pair[0].strip()
			pair[1]=pair[1].strip()
			rpmhdr[pair[0]]=pair[1]
	if 'Source RPM' in rpmhdr:
		name=rpmhdr['Source RPM'].split('-')[0]
	else:
		name=rpmhdr['Name']
	version=rpmhdr['Version']
	arch=rpmhdr['Architecture']
	r=rpmhdr['Release'].split(".")
	if r[0].isdigit() is True:
		release=r[0]
		dist=r[1]
	else:
		release=None
		dist=r[0]
	packageInfo=PackageInfo(osInfo.OSName,dist,name,version,release,arch)
	provides=parseProvides(fullName)
	requires=parseRequires(fullName)
	package=SpecificPackage(packageInfo,fullName,provides,requires,arch)
	package.status="installed"
	return package
def readStr(f):
	res=""
	while True:
		c=f.read(1)
		if not c:
			break
		if c==' ' or c=='\n':
			if res=="":
				continue
			else:
				break
		res=res+c
	return res
def getInstalledPackageInfo(sourcesListManager:SourcesListManager.SourcesListManager):
	res=[]
	with os.popen("/usr/bin/dnf list --installed") as f:
		readStr(f)
		readStr(f)		#ignore [Installed,Packages]
		while True:
			name_arch=readStr(f)
			if name_arch=="":
				break
			fullName=name_arch.split('.')[0]
			arch=name_arch.split('.')[-1]
			if len(name_arch.split('.'))!=2:
				raise Exception("unexpected format")
			version_dist=readStr(f).rsplit('.',1)
			version_release=version_dist[0].split(':')[-1]
			version=version_release.rsplit('-',1)[0]
			release=None
			if len(version_release.rsplit('-',1))>1:
				release=version_release.rsplit('-',1)[1]
			dist=version_dist[1]
			channel=readStr(f)
			#print(osType,dist,name,version,release)
			package=sourcesListManager.getSpecificPackage(fullName,dist,version,release,arch)
			if package is not None:
				package.status="installed"
				res.append(package)
			else:
				res.append(getSpecificInstalledPackage(fullName))
	return res

	
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
		for p in installedPackages:
			p.registerProvides(entryMap)
	
	res=dict()
	for p in selectedPackages:
		depends=SpecificPackage.getDependsPrepare(p)
	for p in selectedPackages:
		depends=SpecificPackage.getDepends(p,set())
		res[p]=list(depends)
	return res