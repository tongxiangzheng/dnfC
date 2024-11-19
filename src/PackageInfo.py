import json
import normalize
class PackageInfo:
	def __init__(self,osType:str,dist:str,name:str,version:str,release:str,arch:str):
		self.osType=osType
		self.dist=dist
		self.name=name
		self.arch=arch
		self.version=version
		self.release=release

	def dumpAsDict(self):
		release=""
		if self.release is not None:
			release="-"+self.release
		version=self.version+release
		info={'name':normalize.normalReplace(self.name),'version':normalize.normalReplace(version),'purl':self.dumpAsPurl()}
		if self.arch is not None:
			info['arch']=self.arch
		return info

	def dumpAsPurl(self):
		osKind="rpm"
		release=""
		if self.release is not None:
			release="-"+self.release
		extraInfos=dict()
		if self.arch is not None and self.arch!="":
			extraInfos['arch']=self.arch
		extraInfoRaw=''
		is_first=True
		for item,value in extraInfos.items():
			if is_first is True:
				extraInfoRaw+='?'
				is_first=False
			else:
				extraInfoRaw+='&'
			extraInfoRaw+=item+'='+value
		
		return 'pkg:'+osKind+'/'+self.osType+'/'+normalize.normalReplace(self.name)+'@'+normalize.normalReplace(self.version+release)+'.'+normalize.normalReplace(self.dist)+extraInfoRaw
		
def loadPurl(purlStr):
	info=purlStr.split(':',1)[1]
	info_extra=info.split('?')
	info=info_extra[0].split('/')
	osType=info[1]
	name=info[2].split('@')[0]
	version_dist=info[2].split('@')[1].rsplit('.',1)
	version_release=version_dist[0].split('-')
	version=version_release[0]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=""
	if len(version_dist)>1:
		dist=version_dist[1]
	arch=""
	if len(info_extra)>1:
		extraInfo=info_extra[1]
		for extra in extraInfo.split('&'):
			ei=extra.split('=')
			if ei[0]=='arch':
				arch=ei[1]
	return PackageInfo(osType,dist,name,version,release,arch)