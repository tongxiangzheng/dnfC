import os
import sys
DIR = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(DIR,"rpm"))
import BinaryRpmAnalysis

class ExternalDependency:
	name:str
	version:str

	def __init__(self,name,version):
		self.name = name
		self.version = version

def spdxmain(packageName,packageFilePath,purlList):
	print("binary deb file at: "+packageFilePath)
	print("purl for: "+packageName)
	for purl in purlList:
		print(' '+purl)
	ExternalDependencies=getExternalDependencies(purlList)
	BinaryRpmAnalysis.binaryRpmScan(packageFilePath,packageFilePath+".spdx.json",ExternalDependencies)

#获取外部依赖
def getExternalDependencies(purlList):
	
	ExternalDependencies = []
	
	print("解析")
	#都是purl链接
	for purl in purlList:
		
		#获取dependency实例数组
	   
		purlComponent =  parse_purl(purl)
		name =purlComponent['name']
		version =  purlComponent['version']
		Dependency = ExternalDependency(
			name = name,
			version= version
		)
		ExternalDependencies.append(Dependency)
		print("require:",require)
		print("name:",name)
		print("version",version)
   
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