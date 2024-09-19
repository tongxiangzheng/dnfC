import os
import sys
DIR = os.path.split(os.path.abspath(__file__))[0]
from .rpm import SyftAnalysis_src

class ExternalDependency:
	name:str
	version:str
	# gitLink:str
	purl:str
	def __init__(self,name,version,purl):
		self.name = name
		self.version = version
		self.purl = purl
		# self.gitLink = gitLink
		
def srcmain(packageName,packageFilePath,dependsList,sbomType='spdx',saveSbomPath='/tmp/dnfC/src'):
	print("binary rpm file at: "+packageFilePath)
	print("depends for: "+packageName)
	for depends in dependsList:
		print(depends)
	ExternalDependencies=getExternalDependencies(dependsList)
	# resPath=packageFilePath+".spdx.json"
	if sbomType == 'spdx':
		resPath = saveSbomPath+packageName+".spdx.json"
	if sbomType == 'cyclonedx':
		resPath = saveSbomPath+packageName+".cyclonedx.json"
	SyftAnalysis_src.scan_rpm_src(packageFilePath,resPath,ExternalDependencies,sbomType)
	return resPath
#获取外部依赖
def getExternalDependencies(dependsList):
	
	ExternalDependencies = []
	
	print("解析")
	
	for depends in dependsList:
		name = depends['name']
		version = depends['version']
		purl = depends['purl']
		#gitLink = ''
		#if 'gitLink' in depends:
		#	gitLink = str(depends['gitLink'])
		Dependency = ExternalDependency(
			name = name,
			version= version,
			purl=purl
			#gitLink= gitLink
		)
		ExternalDependencies.append(Dependency)
		#print("require:",require)
		print("name:",name)
		print("version",version)
		print("purl",purl)
		#print('gitLink',gitLink)

	return ExternalDependencies