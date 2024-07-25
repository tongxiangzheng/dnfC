from collections import defaultdict
from loguru import logger as log
from PackageInfo import PackageInfo
import DscParser
def compareVersion(version1,version2):
	# -1: version1<version2 0:version1==version2 1:version1>version2
	v1=version1.split('.')
	v2=version2.split('.')
	for i in range(min(len(v1),len(v2))):
		if v1[i]<v2[i]:
			return -1
		if v1[i]>v2[i]:
			return -1
	if len(v1)!=len(v2):
		log.warning("version cannot compare, v1: "+version1+" v2: "+version2)
	return 0
class PackageEntry:
	def __init__(self,name:str,flags:str,version:str,release:str):
		self.name=name
		self.flags=flags
		self.version=version
		self.release=release
	def checkMatch(self,dist):
		if self.flags is None:
			return True
		if dist.version is None:
			log.warning(self.name+" have problem: dist version is None")
			return True
		flags=self.flags
		if self.flags=='EQ' and dist.flags!='EQ':
			if dist.flags=='LE':
				flags='GE'
			elif dist.flags=='LT':
				flags='GT'
			elif dist.flags=='GE':
				flags='LE'
			elif dist.flags=='GT':
				flags='LT'
		if flags=='EQ':
			if compareVersion(dist.version,self.version)==0 and (self.release is None or dist.release is None or dist.release==self.release):
				return True
			else:
				return False
		elif flags=='LE':
			if compareVersion(dist.version,self.version)==-1 or (compareVersion(dist.version,self.version)==0 and (self.release is None or dist.release is None or dist.release<self.release)):
				return True
			else:
				return False
		elif flags=='LT':
			if compareVersion(dist.version,self.version)==-1 or (compareVersion(dist.version,self.version)==0 and (self.release is None or dist.release is None or dist.release<=self.release)):
				return True
			else:
				return False
		elif flags=='GE':
			if compareVersion(dist.version,self.version)==1 or (compareVersion(dist.version,self.version)==0 and (self.release is None or dist.release is None or dist.release>self.release)):
				return True
			else:
				return False
		elif flags=='GT':
			if compareVersion(dist.version,self.version)==1 or (compareVersion(dist.version,self.version)==0 and (self.release is None or dist.release is None or dist.release>=self.release)):
				return True
			else:
				return False
		
def defaultNoneList():
	return []
class EntryMap:
	def __init__(self):
		self.provideEntryPackages=defaultdict(defaultNoneList)
	def registerEntry(self,entry:PackageEntry,package):
		self.provideEntryPackages[entry.name].append((package,entry))
	def queryRequires(self,requireName:str,entrys:list):
		# requireName==entrys[i].name
		infoList=self.provideEntryPackages[requireName]
		res=[]
		for info in infoList:
			package=info[0]
			provideEntry=info[1]
			for entry in entrys:
				if entry.checkMatch(provideEntry):
					res.append(package)
		#print(" "+entry.name)
		#for r in res:
			#print("  "+r[0].fullName)
		if len(res)!=1:
			if len(res)==0:
				#log.warning("no package provide the require file: "+entry.name)
				return None
			else:
				res2=[]
				for r in res:
					if r.status=='installed':
						res2.append(r)
				if len(res2)==1:
					return res2[0]
				name=res[0].packageInfo.name
				version=res[0].packageInfo.version
				res2=res[0]
				for r in res[1:]:
					if(name!=r.packageInfo.name):
						log.warning("failed to decide require package for: "+entry.name)
						for r1 in res:
							log.info(" one of provider is: "+r1.fullName)
						return res2
					if compareVersion(version,r.packageInfo.version)==-1:
						version=r.packageInfo.version
						res2=r
				return res2
		#TODO:check res[0][1] is match
		return res[0]
def defaultCVEList():
	return 0
class Counter:
	def __init__(self):
		self.cnt=0
	def getId(self)->int:
		self.cnt+=1
		return self.cnt
class SpecificPackage:
	def __init__(self,packageInfo:PackageInfo,fullName:str,provides:list,requires:list,arch:str,source,status="uninstalled",repoURL=None,fileName=""):
		self.packageInfo=packageInfo
		self.fullName=fullName
		self.providesInfo=provides
		self.requiresInfo=requires
		self.status=status
		self.arch=arch
		self.providesPointers=[]
		self.requirePointers=[]
		self.repoURL=repoURL
		self.fileName=fileName
		self.getGitLinked=False
		self.source=source
	
	def setGitLink(self):
		if self.getGitLinked is True:
			return
		gitLink=DscParser.getGitLink(self)
		self.getGitLinked=True
		self.packageInfo.gitLink=gitLink