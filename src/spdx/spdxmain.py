import os
import sys
DIR = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(DIR,"rpm"))
import BinaryRpmAnalysis

class ExternalDependency:
	name:str
	version:str
	gitLink:str
	def __init__(self,name,version):
		self.name = name
		self.version = version
		self.gitLink = gitLink

def spdxmain(packageName,packageFilePath,dependsList):
	print("binary deb file at: "+packageFilePath)
	print("depends for: "+packageName)
	for depends in dependsList:
		print(depends)
	ExternalDependencies=getExternalDependencies(dependsList)
	resPath=packageFilePath+".spdx.json"
	BinaryRpmAnalysis.binaryRpmScan(packageFilePath,resPath,ExternalDependencies)
	return resPath
#获取外部依赖
def getExternalDependencies(dependsList):
	
	ExternalDependencies = []
	
	print("解析")
	
	for depends in dependsList:
		name = depends['name']
		version = depends['version']
		gitLink = ''
		if 'gitLink' in depends:
			gitLink = str(depends['gitLink'])
		Dependency = ExternalDependency(
			name = name,
			version= version,
			gitLink= gitLink
		)
		ExternalDependencies.append(Dependency)
		#print("require:",require)
		print("name:",name)
		print("version",version)
		print('gitLink',gitLink)

	return ExternalDependencies

def parse_purl(purl):
	"""
	解析一个 purl 链接,返回各个组件。
	"""
	# 匹配 purl 的正则表达式
	purl_pattern = r"^pkg:(?P<type>\w+)\/(?P<namespace>[^@]+)\/(?P<name>[^@]+)(?:@(?P<version>.+))?(?:\?(?P<qualifiers>.+))?(?:#(?P<subpath>.+))?"

	match = re.match(purl_pattern, purl)
	if not match:
		raise ValueError("Invalid purl format: {}".format(purl))

	# 提取各个组件
	components = match.groupdict()

	return components