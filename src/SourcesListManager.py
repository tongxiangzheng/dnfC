import os
import RepoFileManager
import SpecificPackage
import xml.dom.minidom
import osInfo

class SourceConfigItem:
	def __init__(self,dist,primaryFilePath,repoURL):
		self.dist=dist
		self.primaryFilePath=primaryFilePath
		self.repoFileManager=None
		self.repoURL=repoURL
		#self.machineArch=machineArch
	def getRepoFileManager(self):
		if self.repoFileManager is None:
			self.repoFileManager=RepoFileManager.RepoFileManager(self.primaryFilePath,osInfo.OSName,self.dist,self.repoURL)
	def getSpecificPackage(self,name,version,release,arch)->SpecificPackage.SpecificPackage:
		self.getRepoFileManager()
		return self.repoFileManager.queryPackage(name,version,release,arch)
	def getAllPackages(self):
		self.getRepoFileManager()
		return self.repoFileManager.getAllPackages()
def parseRPMSources(data):
	name=None
	baseurl=None
	enabled='1'
	res=[]
	for info in data:
		info=info.split('#',1)[0].strip()
		if len(info)==0:
			continue
		if info.startswith('['):
			if name is not None:
				if enabled=='1':
					res.append((name,baseurl))
			name=info[1:-1]
			baseurl=None
			enabled='1'
		elif info.startswith('baseurl'):
			baseurl=info.split('=',1)[1].strip()
		elif info.startswith('enabled'):
			enabled=info.split('=',1)[1].strip()
	if name is not None:
		if enabled=='1':
			res.append((name,baseurl))
	return res
def parseRPMsrcSources(data):
	name=None
	baseurl=None
	enabled='1'
	res=[]
	for info in data:
		info=info.split('#',1)[0].strip()
		if len(info)==0:
			continue
		if info.startswith('['):
			if name is not None:
				if enabled=='1':
					res.append((name.split('-')[0],baseurl))
			name=info[1:-1]
			baseurl=None
			enabled='1'
		if info.startswith('baseurl'):
			baseurl=info.split('=',1)[1].strip()
		if info.startswith('enabled'):
			enabled=info.split('=',1)[1].strip()
	if name is not None:
		if name.endswith('-source'):
			if enabled=='1':
				res.append((name.split('-')[0],baseurl))
	return res
		
def getPrimaryFilePath(repoPath)->str:
	repomdPath=os.path.join(repoPath,"repomd.xml")
	if not os.path.isfile(repomdPath):
		return None
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

class SourcesListManager:
	def __init__(self):
		self.binaryConfigItems=dict()
		self.rpmURL=dict()
		#self.srcURL=dict()
		#db = dnf.dnf.Base()
		#self.arch=db.conf.substitutions['arch']
		#self.basearch=db.conf.substitutions['basearch']
		#self.releasever=db.conf.substitutions['releasever']
		conf=osInfo.conf
		if conf is not None:
			self.arch=conf['arch']
			self.basearch=conf['basearch']
			self.releasever=conf['releasever']
		else:
			self.arch="$arch"
			self.basearch="$basearch"
			self.releasever="$releasever"
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
					#srcs=parseRPMsrcSources(data)
					#for dist,sourceURL in srcs:
					#	sourceURL=sourceURL.replace('$contentdir',self.contentdir)
					#	sourceURL=sourceURL.replace('$releasever',self.releasever)
					#	sourceURL=sourceURL.replace('$arch',self.arch)
					#	sourceURL=sourceURL.replace('$basearch',self.basearch)
					#	self.srcURL[dist]=sourceURL
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
				dist=file.rsplit('-',1)[0]
				repoPath=os.path.join(distPath,'repodata')
				primaryFilePath=getPrimaryFilePath(repoPath)
				if primaryFilePath is not None:
					self.binaryConfigItems[dist]=[SourceConfigItem(dist,primaryFilePath,self.rpmURL[dist])]
		
		

	
	def getSpecificPackage(self,name,dist,version,release,arch)->SpecificPackage.SpecificPackage:
		if dist not in self.binaryConfigItems:
			#dist may be system or OS
			for configItemList in self.binaryConfigItems.values():
				for configItem in configItemList:
					specificPackage=configItem.getSpecificPackage(name,version,release,arch)
					if specificPackage is not None:
						return specificPackage
			return None
		for configItem in self.binaryConfigItems[dist]:
			specificPackage=configItem.getSpecificPackage(name,version,release,arch)
			if specificPackage is not None:
				return specificPackage
		return None
	def getAllPackages(self):
		res=[]
		for dist,binaryConfigItem in self.binaryConfigItems.items():
			for configItem in binaryConfigItem:
				res.extend(configItem.getAllPackages())
		return res
	#def getSpecificSrcPackage(self,name,dist,version,release,arch)->SpecificPackage.SpecificPackage:
		#for configItem in self.binaryConfigItems[dist]:
		#	specificPackage=configItem.getSpecificPackage(name,version,release,arch)
		#	if specificPackage is not None:
		#		return specificPackage
		#return None
	