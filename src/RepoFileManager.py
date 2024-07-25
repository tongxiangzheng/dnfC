import os

import lz4.frame

from SpecificPackage import *




def parseDEBItemInfo(item):
    item=item.strip()
    name=None
    flags=None
    version=None
    release=None
    items_version=item.split('(')
    if len(items_version)>1:
        name=items_version[0].strip()
        v=items_version[1].split(')')[0]
        parse=v.split('=')
        if len(parse)>1:
            flags="EQ"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('<')
        if len(parse)>1:
            flags="LE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('<=')
        if len(parse)>1:
            flags="LE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('<<')
        if len(parse)>1:
            flags="LT"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('>')
        if len(parse)>1:
            flags="GE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('>=')
        if len(parse)>1:
            flags="GE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('>>')
        if len(parse)>1:
            flags="GT"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        # In dpkg document:
        # The < and > operators are obsolete and should not be used, due to confusing semantics.
        # To illustrate: 0.1 < 0.1 evaluates to true.
    else:
        name=item
    return PackageEntry(name,flags,version,release)

def parseDEBPackages(repoInfos,osType,dist,repoURL,repoFileManager)->SpecificPackage:
	fullName=""
	name=""
	version=""
	release=None
	provides=[]
	requires=[]
	arch=""
	filename=""
	source=""
	res=[]
	for i in range(len(repoInfos)):
		info=repoInfos[i].strip()
		if len(info)==0:
			if name=="":
				name=fullName
			provides.append(PackageEntry(fullName,"EQ",version,release))
			packageInfo=PackageInfo(osType,dist,name,version,release,arch)
			res.append(SpecificPackage(packageInfo,fullName,provides,requires,arch,source,repoURL=repoURL,fileName=filename))
			fullName=""
			name=""
			version=""
			release=None
			provides=[]
			requires=[]
			arch=""
			filename=""
			source=""
		if info.startswith("Package:"):
			fullName=info.split(' ',1)[1]
		if info.startswith("Source:"):
			source=info.split(' ',1)[1]
			name=info.split(' ',2)[1]
		if info.startswith("Version:"):
			version_release=info.split(' ',1)[1].split('-')
			version=version_release[0]
			if len(version_release)>1:
				release=version_release[1]
		if info.startswith("Architecture:"):
			arch=info.split(' ',1)[1]
		if info.startswith("Depends:"):
			depInfos=info.split(' ',1)[1].split("|")
			for depInfo in depInfos:
				requires.append(parseDEBItemInfo(depInfo))
		if info.startswith("Provides:"):
			proInfos=info.split(' ',1)[1].split("|")
			for proInfo in proInfos:
				provides.append(parseDEBItemInfo(proInfo))
		if info.startswith("Filename:"):
			filename=info.split(' ',1)[1]
	return res

class RepoFileManager:
	def __init__(self,url,repoPath,osType,dist):
		self.url=url
		self.repoPath=repoPath
		self.packageMap=defaultdict(defaultNoneList)
		try:
			with open(repoPath,"r") as f:
				data=f.readlines()
		except Exception:
			with open(repoPath+".lz4","rb") as f:
				data=f.read()
				data = lz4.frame.decompress(data).decode().split('\n')
		packages=parseDEBPackages(data,osType,dist,url,self)
		for package in packages:
			self.packageMap[package.fullName].append(package)
	def queryPackage(self,name,version,release):
		if name in self.packageMap:
			for specificPackage in self.packageMap[name]:
				if specificPackage.packageInfo.version==version and specificPackage.packageInfo.release==release:
					return specificPackage
		return None
	