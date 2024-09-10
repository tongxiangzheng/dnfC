import os
import repodataParser
import PackageInfo
import repoFileManager_RPM
import json
import libarchive.public
from loguru import logger as log
DIR = os.path.split(os.path.abspath(__file__))[0]

def getSpecFile(fileName):
	with libarchive.public.file_reader(fileName) as e:
		for entry in e:
			if entry.pathname.endswith('.spec'):
				specStr=b""
				for block in entry.get_blocks():
					specStr+=block
				return specStr.decode('UTF-8')
	return None
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
	return repodataParser.parseRPMItemInfo(requireEntrys)
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
        "vendor":vendor,
        "arch":rpmhdr['Architecture']}
def main(fileName):
	specInfo=getSpecFile(fileName)
	buildRequires=parseSpecFile(specInfo)
	rpmInfo=queryRPMInfo(fileName)
	repoFilesPath,systemType=repoFileManager_RPM.getRepoFile(rpmInfo['dist'],rpmInfo['arch'])
	if systemType is None:
		if rpmInfo['vendor'] is None:
			return []
		systemType=rpmInfo['vendor'].lower()
		repoFilesPath=repoFileManager_RPM.getRepoFileBySystem(systemType,rpmInfo['arch'])
	packageInfo=PackageInfo.PackageInfo(systemType,rpmInfo['dist'],rpmInfo['name'],rpmInfo['version'],rpmInfo['release'])
	targetPackage=repodataParser.SpecificPackage(packageInfo,rpmInfo['name'],[],buildRequires,rpmInfo['arch'],"installed")
	repodataParser.parseRPMFiles(repoFilesPath,[targetPackage])
	purls=[]
	for require in targetPackage.requirePointers:
		purls.append(require.packageInfo.dumpAsPurl())
	return purls

def parseRPMSrc(scanPath,res):
	for file in os.listdir(scanPath):
		if os.path.isfile(os.path.join(scanPath, file)):
			if file.endswith('.src.rpm'):		
				log.info("solve package: "+file)
				res[file]=main(os.path.join(scanPath,file))
	
res={}
scanPath="/mnt/analyze-package"
#scanPath="/mnt/analyze-rpms/"
parseRPMSrc(scanPath,res)
with open(os.path.join(scanPath,"results-rpmsrc.json"),"w") as f:
	json.dump(res,f,indent=2)