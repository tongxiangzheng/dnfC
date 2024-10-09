import sys
import os
DIR = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(DIR,"lib"))
from collections import defaultdict
from loguru import logger as log
from PackageInfo import PackageInfo
def splitDigitAndChar(rawstr)->list:
	res=[]
	if len(rawstr)==0:
		return res
	r=rawstr[0]
	if r.isdigit() is True:
		t="digit"
	else:
		t='char'
	for i in range(1,len(rawstr)):
		c=rawstr[i]
		if c.isdigit() is True:
			t2="digit"
		else:
			t2='char'
		if t!=t2:
			if t=='digit':
				res.append(int(r))
			else:
				res.append(r)
			r=""
			t=t2
		r+=c
	if t=='digit':
		res.append(int(r))
	else:
		res.append(r)
	return res
def compareVersion(version1,version2):
	# -1: version1<version2 0:version1==version2 1:version1>version2
	v1=version1.split('.')
	v2=version2.split('.')
	for i in range(min(len(v1),len(v2))):
		v1l=splitDigitAndChar(v1[i])
		v2l=splitDigitAndChar(v2[i])
		for j in range(min(len(v1l),len(v2l))):
			v1i=v1l[j]
			v2i=v2l[j]
			if type(v1i)!=type(v2i):
				return 0
			if v1i<v2i:
				return -1
			if v1i>v2i:
				return 1
		if len(v1l)<len(v2l):
			return -1
		if len(v1l)>len(v2l):
			return 1
	if len(v1)<len(v2):
		return -1
	if len(v1)>len(v2):
		return 1
	return 0
def compareEntry(a,b):
	r=compareVersion(a.version,b.version)
	if r!=0:
		return r
	if a.release is None or b.release is None:
		return 0
	return compareVersion(a.release,b.release)
class PackageEntry:
	def __init__(self,name:str,flags:str,version:str,release:str):
		self.name=name
		self.flags=flags
		self.version=version
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
			if compareEntry(dist,self)<=0:
				return True
			else:
				return False
		elif flags=='LT':
			if compareEntry(dist,self)==-1:
				return True
			else:
				return False
		elif flags=='GE':
			if compareEntry(dist,self)>=0:
				return True
			else:
				return False
		elif flags=='GT':
			if compareEntry(dist,self)==1:
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
	def queryRequires(self,packageName,requireName:str,entrys:list,mustInstalled:bool):
		# requireName==entrys[i].name
		infoList=self.provideEntryPackages[requireName]
		res=[]
		for info in infoList:
			package=info[0]
			if mustInstalled is True:
				if package.status=='uninstalled':
					continue
			provideEntry=info[1]
			isMatch=True
			for entry in entrys:
				if entry.checkMatch(provideEntry):
					continue
				else:
					isMatch=False
			if isMatch is True:
				res.append(package)
		#print(" "+entry.name)
		#for r in res:
			#print("  "+r[0].fullName)
		if len(res)<=1 or mustInstalled is True:
			return res
		name_versionEntry=dict()
		for r in res:
			name=r.fullName
			if name not in name_versionEntry:
				name_versionEntry[name]=(r.getSelfEntry(),r)
			else:
				if compareEntry(name_versionEntry[name][0],r.getSelfEntry())==-1:
					name_versionEntry[name]=(r.getSelfEntry(),r)
		if len(name_versionEntry)==1:
			return [name_versionEntry[res[0].fullName][1]]
		if requireName in name_versionEntry:
			return [name_versionEntry[requireName][1]]
		log.warning("failed to decide require package for: "+entry.name+" in pacakge: "+packageName)
		for r1 in res:
			log.info(" one of provider is: "+r1.fullName)
		log.info(" select: "+name_versionEntry[res[0].fullName][1].fullName)
		return [name_versionEntry[res[0].fullName][1]]

debugMode=False

def getDependes_dfs(package,dependesSet:set,entryMap,includeInstalled):
	if package in dependesSet:
		return
	if includeInstalled is False and package.status=='installed':
		return
	if package.status=='uninstalled':
		package.status='willInstalled'
	dependesSet.add(package)
	package.findRequires(entryMap)
	if debugMode is True and includeInstalled is True:
		print("%"+package.fullName,package.packageInfo.version,package.packageInfo.release,package.status)
		print("%",end="")
		for p in package.requirePointers:
			print(" "+p.fullName,end="")
		print("")
	for p in package.requirePointers:
		getDependes_dfs(p,dependesSet,entryMap,includeInstalled)	
def getDependsPrepare(entryMap,package):
	depset=set()
	getDependes_dfs(package,depset,entryMap,False)
	return depset
def getDepends(entryMap,package,depset):
	getDependes_dfs(package,depset,entryMap,True)
	return depset
		
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
		provides.append(PackageEntry(fullName,"EQ",packageInfo.version,packageInfo.release))
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
		return self.providesInfo[-1]
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
			res=entryMap.queryRequires(self.fullName,requireName,requireList,True)
			for r in res:
				if r not in requirePackageSet:
					self.addRequirePointer(r)
					requirePackageSet.add(r)
		if self.status=="installed":
			return
		for requireName,requireList in requires.items():
			res=entryMap.queryRequires(self.fullName,requireName,requireList,True)
			for r in res:
				if r not in requirePackageSet:
					self.addRequirePointer(r)
					requirePackageSet.add(r)
	def dump(self):
		print(self.fullName,self.packageInfo.version,self.packageInfo.release,self.status)
		for p in self.requirePointers:
			print(" "+p.fullName,end="")
		print("")
	def getNameVersion(self):
		res=self.fullName+"-"+self.packageInfo.version
		if self.packageInfo.release is not None:
			res+="-"+self.packageInfo.release
		return res