import os
import xml.dom.minidom
import gzip
import pyzstd
import PackageInfo
import SpecificPackage
from loguru import logger as log
def parseRPMItemInfo(data):
    res=[]
    for item in data:
        item=item.strip()
        name=None
        flags=None
        version=None
        release=None
        parse=item.split(' = ')
        if len(parse)>1:
            name=parse[0]
            flags="EQ"
            p2=parse[1].split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=item.split(' <= ')
        if len(parse)>1:
            name=parse[0]
            flags="LE"
            p2=parse[1].split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=item.split(' < ')
        if len(parse)>1:
            name=parse[0]
            flags="LT"
            p2=parse[1].split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=item.split(' >= ')
        if len(parse)>1:
            name=parse[0]
            flags="GE"
            p2=parse[1].split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=item.split(' > ')
        if len(parse)>1:
            name=parse[0]
            flags="GT"
            p2=parse[1].split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        if name is None:
            name=item
        #log.debug(" "+name)
        res.append(SpecificPackage.PackageEntry(name,flags,version,release))
    return res
def parseEntry(node:xml.dom.minidom.Element,fullName:str,type:str)->list:
	#fullName just for debug info, can be empty string
	nodelist=node.childNodes
	res=[]
	for subnode in nodelist:
		if subnode.nodeType==xml.dom.Node.TEXT_NODE:
			continue
		name=subnode.getAttribute('name').strip()
		flags=None
		if subnode.hasAttribute('flags'):
			flags=subnode.getAttribute('flags').strip()
		version=None
		if subnode.hasAttribute('ver'):
			version=subnode.getAttribute('ver').strip()
		else:
			if flags is not None:
				log.warning(fullName+" have a package have flags but no version")
		release=None
		if subnode.hasAttribute('rel'):
			release=subnode.getAttribute('rel').strip().split('.')[0]
		res.append(SpecificPackage.PackageEntry(name,flags,version,release))
	return res
def parseRPMPackage(node:xml.dom.minidom.Element,osType,dist,repoURL)->SpecificPackage.SpecificPackage:
	fullName=node.getElementsByTagName('name')[0].firstChild.nodeValue
	versionNode=node.getElementsByTagName('version')[0]
	version=versionNode.getAttribute('ver').strip().split(':')[-1]
	sourceTag=node.getElementsByTagName('rpm:sourcerpm')
	if sourceTag[0].firstChild is not None:
		sourcerpm=sourceTag[0].firstChild.nodeValue
		name=sourcerpm.split('-'+version)[0]
	else:
		name=fullName
	release=versionNode.getAttribute('rel').strip()
	arch=node.getElementsByTagName('arch')[0].firstChild.nodeValue
	provides=[]
	res=node.getElementsByTagName('rpm:provides')
	if len(res)!=0:
		provides=parseEntry(res[0],fullName,'provides')
	requires=[]
	res=node.getElementsByTagName('rpm:requires')
	if len(res)!=0:
		requires=parseEntry(res[0],fullName,'requires')
	filePath=node.getElementsByTagName('location')[0].getAttribute('href').strip()
	packageInfo=PackageInfo.PackageInfo(osType,dist,name,version,release,arch)
	return SpecificPackage.SpecificPackage(packageInfo,fullName,provides,requires,arch,repoURL=repoURL,fileName=filePath)

def parseRPMFiles(repodata,osType,dist,repoURL):
	#entryMap=EntryMap()
	res=[]
	doc=xml.dom.minidom.parseString(repodata)
	root=doc.documentElement
	nodelist=root.childNodes
	for subnode in nodelist:
		if subnode.nodeType==xml.dom.Node.TEXT_NODE:
			continue
		package=parseRPMPackage(subnode,osType,dist,repoURL)
		#package.registerProvides(entryMap)
		res.append(package)
	return res


class RepoFileManager:
	def __init__(self,repoPath,osType,dist,repoURL):
		self.repoPath=repoPath
		self.packageMap=SpecificPackage.defaultdict(SpecificPackage.defaultNoneList)
		if repoPath.endswith('.gz'):
			with gzip.open(repoPath,"rb") as f:
				data=f.read()
		elif repoPath.endswith('.zst'):
			with open(repoPath, "rb") as f:
				data = f.read()
				data = pyzstd.decompress(data)
		else:
			print("warning: cannot extract file "+repoPath)
		self.packages=parseRPMFiles(data,osType,dist,repoURL)
		for package in self.packages:
			self.packageMap[package.fullName].append(package)
	def queryPackage(self,name,version,release,arch):
		#print("\nquery:")
		#print(name,version,release,arch)
		if "." not in release:
			raise Exception("version have no '.' : "+release)
		e=SpecificPackage.PackageEntry(name,"EQ",version,release)
		if name in self.packageMap:
			for specificPackage in self.packageMap[name]:
				#print(specificPackage.packageInfo.version,specificPackage.packageInfo.release,specificPackage.packageInfo.arch)
				if SpecificPackage.compareEntry(specificPackage.getSelfEntry(),e)==0:
					if specificPackage.packageInfo.arch==arch:
							return specificPackage
			return None
	def getAllPackages(self):
		return self.packages
		
	