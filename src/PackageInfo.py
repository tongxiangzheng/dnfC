import json
import normalize
class PackageInfo:
	def __init__(self,osType:str,dist:str,name:str,version:str,release:str,arch:str,gitLink=None):
		self.osType=osType
		self.dist=dist
		self.name=name
		self.gitLink=gitLink
		self.arch=arch
		id=version.find('p')
		if id==-1:
			self.update=None
			self.version=version
		else:
			self.update=version[id:]
			self.version=version[0:id]
			#print(version,self.version,self.update)
		self.release=release
	def dump(self):
		info={'osType':self.osType,'dist':self.dist,'name':self.name,'version':self.version,'release':self.release}
		if self.update is not None:
			info['update']=self.update
		if self.gitLink is not None:
			info['gitLink']=self.gitLink
		return json.dumps(info)
	def dumpAsDict(self):
		release=""
		if self.release is not None:
			release="-"+self.release
			if self.update is not None:
				release+='p'+self.update
		version=self.version+release
		info={'name':normalize.normalReplace(self.name),'version':normalize.normalReplace(version),'purl':self.dumpAsPurl()}
		if self.gitLink is not None:
			info['gitLink']=self.gitLink
		return info

	def dumpAsPurl(self):
		osKind="rpm"
		release=""
		if self.release is not None:
			release="-"+self.release
			if self.update is not None:
				release+='p'+self.update
		if self.gitLink is None:
			return normalize.normalReplace('pkg:'+osKind+'/'+self.osType+'/'+self.name+'@'+self.version+release+'.'+self.dist)
		else:
			return normalize.normalReplace('pkg:'+osKind+'/'+self.osType+'/'+self.name+'@'+self.version+release+'.'+self.dist+"&"+"gitLink="+self.gitLink)

def loadPackageInfo(jsonInfo):
	osType=jsonInfo['osType']
	if osType=='deb':
		gitLink=jsonInfo['gitLink']
	else:
		gitLink=None
	dist=jsonInfo['dist']
	name=jsonInfo['name']
	version=jsonInfo['version']
	if 'update' in jsonInfo:
		version=version+'p'+jsonInfo['update']
	release=jsonInfo['release']
	return PackageInfo(osType,dist,name,version,release,gitLink)

def loadPurl(purlStr):
	info=purlStr.split(':')[1]
	info_extra=info.split('?')
	info=info_extra[0].split('/')
	osType=info[1]
	name=info[2].split('@')[0]
	version_dist=info[2].split('@')[1]
	version_release=version_dist.split('-')
	version=version_release[0]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=""
	if len(version_dist)>1:
		dist=version_dist[1]
	gitLink=""
	if len(info_extra)>1:
		extraInfo=info_extra[1]
		for extra in extraInfo.split('&'):
			ei=extra.split('=')
			if ei[0]=='gitLink':
				gitLink=ei[1]
	return PackageInfo(osType,dist,name,version,release,gitLink)