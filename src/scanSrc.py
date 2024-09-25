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
import re
import osInfo
from spdx.srcmain import srcmain
from loguru import logger as log
DIR = os.path.split(os.path.abspath(__file__))[0]

def getSpecFile(src_rpm_path):
	dpkg_command = f'rpm2archive {src_rpm_path}'
	os.system(dpkg_command)
	#创建一个文件夹放置解压后的文件
	tgzFilepath = src_rpm_path+'.tgz'
	dir_Path = re.sub(r'\.rpm$','',src_rpm_path)
	if os.path.isdir(dir_Path):
		rm_command = f'rm -rf {dir_Path}'
		os.system(rm_command)
	mkdir_command = f'mkdir {dir_Path}'
	os.system(mkdir_command)
	#解压tgz文件
	unpack_command = f'tar -zxvf {tgzFilepath} -C {dir_Path}'
	p = Popen(unpack_command, shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()

	#找到关键压缩包，解压后，得到解压后的文件夹
	for root,dirs,files in os.walk(dir_Path):
		for file in files:
			if file.endswith('.spec'):
				#获取压缩包完整路径
				spec_path = os.path.join(root,file)
				with open(spec_path,"r") as f:
					return f.read()
	return None

	# with tarfile.open(fileName) as f:
	# 	for e in f.getmembers():
	# 		if e.name.endswith('.spec'):
	# 			specFilePointer=f.extractfile(e)
	# 			return specFilePointer.read()
				
	# with libarchive.public.file_reader(fileName) as e:
	# 	for entry in e:
	# 		if entry.pathname.endswith('.spec'):
	# 			specStr=b""
	# 			for block in entry.get_blocks():
	# 				specStr+=block
	# 			return specStr.decode('UTF-8')
	# return None
def parseSpecFile(specInfo):
	requireEntrys=[]
	for info in specInfo.split('\n'):
		info=info.strip()
		if info.startswith('BuildRequires:'):
			requireEntrys_raw=info.split(':')[1].split(',')
			requireEntrys_raw2=[]
			for entrys in requireEntrys_raw:
				for e2 in entrys.split(' '):
					e2=e2.strip()
					if e2!='':
						requireEntrys_raw2.append(e2)
			needMerge=False
			for entrys in requireEntrys_raw2:
				if needMerge is True:
					requireEntrys[-1]+=' '+entrys
					needMerge=False
				elif entrys == '>' or entrys =='>=' or entrys =='<' or entrys =='<=' or entrys =='=':
					requireEntrys[-1]+=' '+entrys
					needMerge=True
				else:
					requireEntrys.append(entrys)
	return RepoFileManager.parseRPMItemInfo(requireEntrys)
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
	osType="centos"
	res=list()
	with os.popen("yum list installed") as f:
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
			version=version_dist[0].split(':')[-1]
			release=version.rsplit('-',1)[-1]
			version=version.rsplit('-',1)[0]
			dist=version_dist[1]
			channel=readStr(f)[1:]
			if channel=="system":
				continue
			#print(osType,dist,name,version,release)
			package=sourcesListManager.getSpecificPackage(fullName,channel,version,release,arch)
			if package is not None:
				package.status="installed"
			else:
				packageInfo=PackageInfo.PackageInfo(osType,dist,fullName,version,release,arch)
				provides=parseProvides(fullName)
				requires=parseRequires(fullName)
				res.append(SpecificPackage.SpecificPackage(packageInfo,fullName,provides,requires,None,"installed"))
	return res

def scansrc(args):
	srcFile=None
	genSpdx=False
	spdxPath='.'
	genCyclonedx=False
	cyclonePath='.'
	for option in args:
		if option.startswith('--genspdx='):
			genSpdx=True
			spdxPath=option.split('=',1)[1]
		elif option.startswith('--gencyclonedx='):
			genCyclonedx=True
			cyclonePath=option.split('=',1)[1]
		elif option=="scansrc":
			continue
		else:
			srcFile=option
	if spdxPath is False and cyclonePath is False:
		spdxPath=True
	srcPath=os.path.join("/tmp/dnfC/",normalize.normalReplace(os.path.abspath(srcFile)))
	shutil.copyfile(srcFile,srcPath)
	specInfo=getSpecFile(srcPath)
	depends=parseSpecFile(specInfo)
	rpmInfo=queryRPMInfo(srcFile)
	packageInfo=PackageInfo.PackageInfo(osInfo.OSName,osInfo.OSDist,rpmInfo['name'],rpmInfo['version'],rpmInfo['release'],osInfo.arch)
	srcpackage=SpecificPackage.SpecificPackage(packageInfo,rpmInfo['name'],[],depends,osInfo.arch,"installed")
	sourcesListManager=SourcesListManager.SourcesListManager()
	repoPackages=sourcesListManager.getAllPackages()
	repoPackages.extend(setInstalledPackagesStatus(sourcesListManager))
	entryMap=SpecificPackage.EntryMap()
	srcpackage.registerProvides(entryMap)
	for package in repoPackages:
		package.registerProvides(entryMap)
	
	for package in repoPackages:
		package.findRequires(entryMap)
	srcpackage.findRequires(entryMap)

	
	depset=set()
	SpecificPackage.getDependes(package,depset)
	depends=dict()
	for p in depset:
		depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
	dependsList=list(depends.values())
	print(dependsList)
	if genSpdx is True:
		srcmain(normalize.normalReplace(srcpackage.fullName),srcPath,dependsList,'spdx',spdxPath)
	if genCyclonedx is True:
		srcmain(normalize.normalReplace(srcpackage.fullName),srcPath,dependsList,'cyclonedx',cyclonedxPath)

	print("generate SBOM for "+srcpackage.fullName)
	return 0
