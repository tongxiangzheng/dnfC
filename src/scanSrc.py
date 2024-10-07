import os
import SourcesListManager
import RepoFileManager
import PackageInfo
import os
from subprocess import PIPE, Popen
import SpecificPackage
import PackageInfo
import normalize
import shutil
import requests
import loadConfig
import osInfo
from spdx.srcmain import srcmain
from loguru import logger as log
DIR = os.path.split(os.path.abspath(__file__))[0]

def postFile(file,dnfConfigure:loadConfig.dnfcConfigure):
	try:
		files = {'file': open(file, 'rb')}
		response = requests.post(dnfConfigure.postfileURL,files=files)
	except requests.exceptions.ConnectionError as e:
		print("failed to upload file: Unable to connect: "+dnfConfigure.postfileURL)
		return None
	except Exception as e:
		print(f'failed to upload file: {e}')
		return None
	if response.status_code == 200:
		data=response.json()
		if data['error']==0:
			return data['token']
		else:
			print("failed to upload file: failinfo: "+data['errorMessage'])
			return None
	else:
		print(f'failed to upload file: Request failed with status code {response.status_code}')
		return None
	
def queryBuildInfo(srcFile,srcFile2,osType,osDist,arch,dnfConfigure:loadConfig.dnfcConfigure):
	src1token=postFile(srcFile,dnfConfigure)
	if src1token is None:
		return None
	src2token=None
	if srcFile2 is not None:
		src2token=postFile(srcFile2,dnfConfigure)
		if src2token is None:
			return None
	try:
		data={"srcFile":src1token,"srcFile2":src2token,"osType":osType,"osDist":osDist,"arch":arch}
		print("waiting build from server... It may take some time.")
		response = requests.post(dnfConfigure.querybuildinfoURL, json=data)
	except requests.exceptions.ConnectionError as e:
		print("failed to query buildInfo: Unable to connect: "+dnfConfigure.querybuildinfoURL)
		return None
	except Exception as e:
		print(f'failed to query buildInfo: {e}')
	if response.status_code == 200:
		data=response.json()
		if data['error']==0:
			return data['buildinfo']
		else:
			print("failed to query package info: failinfo: "+data['errorMessage'])
			return None
	else:
		print(f'failed to query buildInfo: Request failed with status code {response.status_code}')
		return None
def getSrcPackageDepends(srcPath):
	dnfConfigure=loadConfig.loadConfig()
	if dnfConfigure is None:
		print('ERROR: cannot load config file in /etc/dnfC/config.json, please check config file ')
		return None
def queryRPMInfo(fileName):
	rpmhdr={}
	with os.popen("rpm -qi --nosignature "+fileName) as f:
		data=f.readlines()
		for item in data:
			pair=item.split(":",1)
			if len(pair)==2:
				pair[0]=pair[0].strip()
				pair[1]=pair[1].strip()
				rpmhdr[pair[0]]=pair[1]
	name=rpmhdr['Name']
	version=rpmhdr['Version']
	r=rpmhdr['Release'].split(".")
	if r[0].isdigit() is True:
		release=r[0]
		dist=r[1]
	else:
		release=None
		dist=r[0]
	vendor=None
	if 'Vendor' in rpmhdr:
		vendor=rpmhdr['Vendor'].split(' ')[0]
	return{"name":name,
		"version":version,
		"release":release,
		"dist":dist,
		"vendor":vendor}
#		"arch":rpmhdr['Architecture']}
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
def parseRequires(PackageName)->list:
    with os.popen("rpm -q --requires "+PackageName) as f:
        data=f.readlines()
        return RepoFileManager.parseRPMItemInfo(data)
def parseProvides(PackageName)->list:
    with os.popen("rpm -q --provides "+PackageName) as f:
        data=f.readlines()
        return RepoFileManager.parseRPMItemInfo(data)
def setInstalledPackagesStatus(sourcesListManager:SourcesListManager.SourcesListManager):
	res=list()
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
			channel=readStr(f)[1:]
			if channel=="system":
				continue
			#print(osType,dist,name,version,release)
			package=sourcesListManager.getSpecificPackage(fullName,channel,version,release,arch)
			if package is not None:
				package.status="installed"
			else:
				packageInfo=PackageInfo.PackageInfo(osInfo.OSName,dist,fullName,version,release,arch)
				provides=parseProvides(fullName)
				requires=parseRequires(fullName)
				res.append(SpecificPackage.SpecificPackage(packageInfo,fullName,provides,requires,None,"installed"))
	return res

def scansrc(args):
	srcFile=None
	genSpdx=False
	spdxPath='.'
	genCyclonedx=False
	cyclonedxPath='.'
	for option in args:
		if option.startswith('--genspdx='):
			genSpdx=True
			spdxPath=option.split('=',1)[1]
		elif option.startswith('--gencyclonedx='):
			genCyclonedx=True
			cyclonedxPath=option.split('=',1)[1]
		elif option=="scansrc":
			continue
		else:
			srcFile=option
	if genSpdx is False and genCyclonedx is False:
		genSpdx=True
	srcPath=os.path.join("/tmp/dnfC/",normalize.normalReplace(os.path.abspath(srcFile)))
	shutil.copyfile(srcFile,srcPath)
	depends=getSrcPackageDepends(srcPath)
	if depends is None:
		return 1
	rpmInfo=queryRPMInfo(srcFile)
	packageInfo=PackageInfo.PackageInfo(osInfo.OSName,osInfo.OSDist,rpmInfo['name'],rpmInfo['version'],rpmInfo['release'],osInfo.arch)
	srcpackage=SpecificPackage.SpecificPackage(packageInfo,rpmInfo['name'],[],depends,osInfo.arch,"willInstalled")
	sourcesListManager=SourcesListManager.SourcesListManager()
	repoPackages=sourcesListManager.getAllPackages()
	repoPackages.extend(setInstalledPackagesStatus(sourcesListManager))
	entryMap=SpecificPackage.EntryMap()

	srcpackage.registerProvides(entryMap)
	for package in repoPackages:
		if package.fullName in srcpackage.fullName:
			continue
		package.registerProvides(entryMap)

	
	depset=SpecificPackage.getDepends(entryMap,srcpackage,set())
	depends=dict()
	for p in depset:
		depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
	dependsList=list(depends.values())
	if genSpdx is True:
		srcmain(normalize.normalReplace(srcpackage.fullName),srcPath,dependsList,'spdx',spdxPath)
	if genCyclonedx is True:
		srcmain(normalize.normalReplace(srcpackage.fullName),srcPath,dependsList,'cyclonedx',cyclonedxPath)

	print("generate SBOM for "+srcpackage.fullName)
	return 0
