import os
import RepoFileManager
import SpecificPackage
import xml.dom.minidom
from loguru import logger as log
from subprocess import PIPE, Popen
#import dnf
import json
def getSelfOSName():
	with open("/etc/os-release") as f:
		data=f.readlines()
		for info in data:
			if info.startswith('ID='):
				return info.strip()[4:-1]	
	return ""
selfOSName=getSelfOSName()
class SourceConfigItem:
	def __init__(self,dist,primaryFilePath,repoURL):
		self.dist=dist
		self.primaryFilePath=primaryFilePath
		self.repoFiles=dict()
		self.repoURL=repoURL
		#self.machineArch=machineArch
	def getGitLink(self,name,arch):
		#abandon
		log.warning("abandon")
		repoPath=self.primaryFilePath
		if repoPath not in self.repoFiles:
			self.repoFiles[repoPath]=RepoFileManager.RepoFileManager(self.url,repoPath,selfOSName,self.dist,self.repoURL)
		return self.repoFiles[repoPath].getGitLink(name)
	def getSpecificPackage(self,name,version,release,arch)->SpecificPackage.SpecificPackage:
		repoPath=self.primaryFilePath
		if repoPath not in self.repoFiles:
			self.repoFiles[repoPath]=RepoFileManager.RepoFileManager(repoPath,selfOSName,self.dist,self.repoURL)
		return self.repoFiles[repoPath].queryPackage(name,version,release,arch)

def parseRPMSources(data):
	name=None
	baseurl=None
	res=[]
	for info in data:
		info=info.split('#',1)[0].strip()
		if len(info)==0:
			continue
		if info.startswith('['):
			if name is not None:
				if not name.endswith('-source'):
					res.append((name,baseurl))
			name=info[1:-1]
			baseurl=None
		if info.startswith('baseurl'):
			baseurl=info.split('=',1)[1].strip()
	if name is not None:
		if not name.endswith('-source'):
			res.append((name,baseurl))
	return res
def parseRPMsrcSources(data):
	name=None
	baseurl=None
	res=[]
	for info in data:
		info=info.split('#',1)[0].strip()
		if len(info)==0:
			continue
		if info.startswith('['):
			if name is not None:
				if name.endswith('-source'):
					res.append((name.split('-')[0],baseurl))
			name=info[1:-1]
			baseurl=None
		if info.startswith('baseurl'):
			baseurl=info.split('=',1)[1].strip()
	if name is not None:
		if name.endswith('-source'):
			res.append((name.split('-')[0],baseurl))
	return res
		
def getPrimaryFilePath(repoPath)->str:
	repomdPath=os.path.join(repoPath,"repomd.xml")
	doc=xml.dom.minidom.parse(repomdPath)
	root=doc.documentElement
	nodelist=root.childNodes
	for subnode in nodelist:
		if subnode.nodeType==xml.dom.Node.TEXT_NODE:
			continue
		if subnode.hasAttribute("type"):
			if subnode.getAttribute("type")!="primary":
				continue
			hash=subnode.getElementsByTagName('checksum')[0].firstChild.nodeValue
			fileName=hash+"-primary.xml.gz"
			filePath=os.path.join(repoPath,fileName)
			if not os.path.isfile(filePath):
				fileName=hash+"-primary.xml.zst"
				filePath=os.path.join(repoPath,fileName)
			return filePath

def queryDnfContext():
	cmd="python3 -c 'import dnf, pprint; db = dnf.dnf.Base(); pprint.pprint(db.conf.substitutions, width=1)'"
	p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=json.load(stdout.decode)
	return data
class SourcesListManager:
	def __init__(self):
		self.binaryConfigItems=dict()
		self.rpmURL=dict()
		self.srcURL=dict()
		#db = dnf.dnf.Base()
		#self.arch=db.conf.substitutions['arch']
		#self.basearch=db.conf.substitutions['basearch']
		#self.releasever=db.conf.substitutions['releasever']
		conf=queryDnfContext()
		self.arch=conf['arch']
		self.basearch=conf['basearch']
		self.releasever=conf['releasever']
		self.contentdir=""
		if os.path.isfile('/etc/yum/vars/contentdir'):
			with open('/etc/yum/vars/contentdir') as f:
				self.contentdir=f.read().strip()
		srcSourcesd='/etc/yum.repos.d/'
		for file in os.listdir(srcSourcesd):
			filePath=os.path.join(srcSourcesd, file)
			if os.path.isfile(filePath):
				with open(filePath) as f:
					data=f.readlines()
					srcs=parseRPMsrcSources(data)
					for dist,sourceURL in srcs:
						sourceURL=sourceURL.replace('$contentdir',self.contentdir)
						sourceURL=sourceURL.replace('$releasever',self.releasever)
						sourceURL=sourceURL.replace('$arch',self.arch)
						sourceURL=sourceURL.replace('$basearch',self.basearch)
						self.srcURL[dist]=sourceURL
					rpms=parseRPMSources(data)
					for dist,sourceURL in rpms:
						sourceURL=sourceURL.replace('$contentdir',self.contentdir)
						sourceURL=sourceURL.replace('$releasever',self.releasever)
						sourceURL=sourceURL.replace('$arch',self.arch)
						sourceURL=sourceURL.replace('$basearch',self.basearch)
						self.rpmURL[dist]=sourceURL
					
		sourcesd='/var/cache/dnf/'
		for file in os.listdir(sourcesd):
			distPath=os.path.join(sourcesd, file)
			if os.path.isdir(distPath):
				dist=file.split('-')[0]
				repoPath=os.path.join(distPath,'repodata')
				primaryFilePath=getPrimaryFilePath(repoPath)
				self.binaryConfigItems[dist]=[SourceConfigItem(dist,primaryFilePath,self.rpmURL[dist])]
		
		

	
	def getSpecificPackage(self,name,dist,version,release,arch)->SpecificPackage.SpecificPackage:
		for configItem in self.binaryConfigItems[dist]:
			specificPackage=configItem.getSpecificPackage(name,version,release,arch)
			if specificPackage is not None:
				return specificPackage
		return None
	#def getSpecificSrcPackage(self,name,dist,version,release,arch)->SpecificPackage.SpecificPackage:
		#for configItem in self.binaryConfigItems[dist]:
		#	specificPackage=configItem.getSpecificPackage(name,version,release,arch)
		#	if specificPackage is not None:
		#		return specificPackage
		#return None
	