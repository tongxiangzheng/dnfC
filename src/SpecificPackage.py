import sys
import os
DIR = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(DIR,"lib"))
from collections import defaultdict
from loguru import logger as log
from PackageInfo import PackageInfo
def compareVersion(version1,version2):
	# -1: version1<version2 0:version1==version2 1:version1>version2
	v1=version1.split('.')
	v2=version2.split('.')
	for i in range(min(len(v1),len(v2))):
		if v1[i].isdigit():
			v1i=int(v1[i])
		else:
			v1i=v1[i]
		if v2[i].isdigit():
			v2i=int(v2[i])
		else:
			v2i=v2[i]
		if v1i<v2i:
			return -1
		if v1i>v2i:
			return 1
	#if len(v1)!=len(v2):
	#	log.warning("version cannot compare, v1: "+version1+" v2: "+version2)
	return 0
def firstNumber(rawstr)->str:
	res=""
	for c in rawstr:
		if c.isdigit() is True or c == '.':
			res+=c
		else:
			break
	if res.endswith('.'):
		res=res[:-1]
	return res
class PackageEntry:
	def __init__(self,name:str,flags:str,version:str,release:str):
		self.name=name
		self.flags=flags
		if version is not None:
			version=firstNumber(version.split(':')[-1])
		self.version=version
		if release is not None:
			releasenew=firstNumber(release)
			if releasenew!=0:
				release=releasenew
		self.release=release
	def checkMatch(self,dist):
		if self.flags is None or dist.flags is None:
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
	def dump(self):
		res=self.name
		if self.flags=='EQ':
			res+=' = '
		elif self.flags=='LE':
			res+=' <= '
		elif self.flags=='LT':
			res+=' < '
		elif self.flags=='GE':
			res+=' >= '
		elif self.flags=='GT':
			res+=' > '
		
		if self.version is not None:
			res+=self.version
		if self.release is not None:
			res+='-'+self.release
		return res
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
			#print(package.fullName)
			provideEntry=info[1]
			#print('-'+provideEntry.dump())
			for entry in entrys:
				#print(' '+entry.dump())
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
				versionEntry=res[0].getSelfEntry()
				res2=res[0]
				for r in res[1:]:
					if(name!=r.packageInfo.name):
						# log.warning("failed to decide require package for: "+entry.name)
						# for r1 in res:
						# 	log.info(" one of provider is: "+r1.fullName)
						return res2
					if compareVersion(versionEntry.version,r.getSelfEntry().version)==-1:
						versionEntry=r.getSelfEntry()
						res2=r
				return res2
		#TODO:check res[0][1] is match
		return res[0]
def getDependes(package,dependesSet:set):
	if package in dependesSet:
		return
	dependesSet.add(package)
	for p in package.requirePointers:
		getDependes(p,dependesSet)	

		
def defaultCVEList():
	return 0
class Counter:
	def __init__(self):
		self.cnt=0
	def getId(self)->int:
		self.cnt+=1
		return self.cnt
class SpecificPackage:
	def __init__(self,packageInfo:PackageInfo,fullName:str,provides:list,requires:list,arch:str,status="uninstalled",repoURL=None,fileName=""):
		self.packageInfo=packageInfo
		if packageInfo.version=="":
			print(fullName,packageInfo.name)
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
		self.registerProvided=False
		self.haveFoundRequires=False
	def addProvidesPointer(self,package):
		#无需手动调用，addRequirePointer自动处理
		self.providesPointers.append(package)
	def addRequirePointer(self,package):
		self.requirePointers.append(package)
		package.addProvidesPointer(self)
	def registerProvides(self,entryMap:EntryMap)->None:
		if self.registerProvided is True:
			return
		self.registerProvided=True
		for provide in self.providesInfo:
			entryMap.registerEntry(provide,self)
	def getSelfEntry(self):
		return PackageEntry(self.fullName,"EQ",self.packageInfo.version,self.packageInfo.release)
	def findRequires(self,entryMap:EntryMap)->None:
		if self.haveFoundRequires is True:
			return
		self.haveFoundRequires=True
		requirePackageSet=set()
		requires=dict()
		for require in self.requiresInfo:
			if require.name not in requires:
				requires[require.name]=[]
			requires[require.name].append(require)
		for requireName,requireList in requires.items():
			res=entryMap.queryRequires(requireName,requireList)
			if res is not None and res not in requirePackageSet:
				self.addRequirePointer(res)
				requirePackageSet.add(res)