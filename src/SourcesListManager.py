import os
import RepoFileManager
import SpecificPackage
from loguru import logger as log
class sourceConfigItem:
	def __init__(self,url,dist,channel):
		self.url=url
		self.url_without_prefix=url.split('//')[1].split('/')[0]
		self.dist=dist
		self.channel=channel
		self.repoFiles=dict()
		with os.popen("dpkg --print-architecture") as f:
			self.arch=f.read().strip()
	def getFilePath(self):

		return '/var/lib/apt/lists/'+self.url_without_prefix+'_ubuntu_dists_'+self.dist+'_'+self.channel+"_binary-"+self.arch+"_Packages"
	def getGitLink(self,name,arch):
		#abandon
		log.warning("abandon")
		repoPath=self.getFilePath()
		if repoPath not in self.repoFiles:
			self.repoFiles[repoPath]=RepoFileManager.RepoFileManager(self.url,repoPath,"ubuntu",self.dist)
		return self.repoFiles[repoPath].getGitLink(name)
	def getSpecificPackage(self,name,version,release)->SpecificPackage.SpecificPackage:
		repoPath=self.getFilePath()
		if repoPath not in self.repoFiles:
			self.repoFiles[repoPath]=RepoFileManager.RepoFileManager(self.url,repoPath,"ubuntu",self.dist)
		return self.repoFiles[repoPath].queryPackage(name,version,release)


def parseRPMSources(data,binaryConfigItems,srcConfigItems):
	Types=None
	URIs=None
	Suites=[]
	Components=[]
	for info in data:
		info=info.split('#',1)[0].strip()
		if len(info)==0:
			if Types is None:
				continue
			configItems=[]
			for dist in Suites:
				for channel in Components:
					configItems.append(sourceConfigItem(URIs,dist,channel))
				if Types=='deb':
					binaryConfigItems[dist]=configItems
				elif Types=='deb-src':
					srcConfigItems[dist]=configItems
		if info.startswith('Types:'):
			Types=info.split(':',1)[1].strip()
		if info.startswith('URIs:'):
			URIs=info.split(':',1)[1].strip()
		if info.startswith('Suites:'):
			Suites=info.split(':',1)[1].strip().split(' ')
		if info.startswith('Components:'):
			Components=info.split(':',1)[1].strip().split(' ')
		

class SourcesListManager:
	def __init__(self):
		self.binaryConfigItems=dict()
		self.srcConfigItems=dict()
		sourcesd='/etc/yum.repos.d'
		for file in os.listdir(sourcesd):
			filePath=os.path.join(sourcesd, file)
			if file.endswith('.sources') and os.path.isfile(filePath):
				with open(filePath) as f:
					data=f.readlines()
					parseRPMSources(data,self.binaryConfigItems,self.srcConfigItems)
	
	def setGitLink(self,name,arch,dist):
		#abandon
		log.warning("abandon")
		for configItem in self.binaryConfigItems[dist]:
			res=configItem.getGitLink(name,arch)
			if res is not None:
				return res
		return None
	def getSpecificPackage(self,name,dist,version,release)->SpecificPackage.SpecificPackage:
		for configItem in self.binaryConfigItems[dist]:
			specificPackage=configItem.getSpecificPackage(name,version,release)
			if specificPackage is not None:
				return specificPackage
		return None
	def getSpecificSrcPackage(self,name,dist,version,release)->SpecificPackage.SpecificPackage:
		for configItem in self.binaryConfigItems[dist]:
			specificPackage=configItem.getSpecificPackage(name,version,release)
			if specificPackage is not None:
				return specificPackage
		return None
	
	def getBinaryDebPackage(self,packageInfo):
		pass
