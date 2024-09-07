import sys
import os
DIR = os.path.split(os.path.abspath(__file__))[0]
import getNewInstall
import SourcesListManager
import nwkTools
import requests
from loguru import logger as log
import normalize
import json
import loadConfig
from spdx.spdxmain import spdxmain
#from spdx.spdxmain import spdxmain
def downloadPackage(selectedPackage):
	return nwkTools.downloadFile(selectedPackage.repoURL+'/'+selectedPackage.fileName,'/tmp/dnfC/packages',normalize.normalReplace(selectedPackage.fileName.rsplit('/',1)[1]))

def queryCVE(spdxObj,dnfConfigure:loadConfig.dnfcConfigure):
	url=dnfConfigure.serverURL
	try:
		response = requests.post(url, json=spdxObj)
	except requests.exceptions.ConnectionError as e:
		print("failed to query CVE: Unable to connect: "+url)
		return {}
	except Exception as e:
		print(f'failed to query CVE: {e}')
	if response.status_code == 200:
		return response.json()
	else:
		print(f'failed to query CVE: Request failed with status code {response.status_code}')
		return {}
def main(args,genSpdx=True,saveSpdxPath=None,genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=False):
	assumeNo=False
	for option in args:
		if option=='--assumeno':
			assumeNo=True
		if option.startswith('--genspdx'):
			genSpdx=True
			saveSpdxPath=option.split('=',1)[1]
		if option.startswith('--gencyclonedx'):
			genCyclonedx=True
			saveCyclonedxPath=option.split('=',1)[1]
	sourcesListManager=SourcesListManager.SourcesListManager()
	selectedPackages_willInstallPackages=getNewInstall.getNewInstall(args,sourcesListManager,dumpFileOnly)
	if len(selectedPackages_willInstallPackages)==0:
		return True
	dnfConfigure=loadConfig.loadConfig()
	if dnfConfigure is None:
		print('ERROR: cannot load config file in /etc/dnfC/config.json, please check config file ')
		return False
	for selectedPackage,willInstallPackages in selectedPackages_willInstallPackages.items():
		selectedPackageName=selectedPackage.fullName
		depends=dict()
		project_packages=dict()
		for p in willInstallPackages:
			depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
			if p.packageInfo.name not in project_packages:
				project_packages[p.packageInfo.name]=[]
			project_packages[p.packageInfo.name].append(p.fullName)
		dependsList=list(depends.values())
		packageFilePath=downloadPackage(selectedPackage)
		if dumpFileOnly is True:
			if genSpdx is True:
				spdxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'spdx',saveSpdxPath)
			if genCyclonedx is True:
				cyclonedxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'cyclonedx',saveCyclonedxPath)
			continue
		spdxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'spdx',saveSpdxPath)
		if genCyclonedx is True:
			cyclonedxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'cyclonedx',saveCyclonedxPath)
		with open(spdxPath,"r") as f:
			spdxObj=json.load(f)
		cves=queryCVE(spdxObj,dnfConfigure)
		for projectName,cves in cves.items():
			if len(cves)==0:
				continue
			print("package: ",end='')
			first=True
			for packageName in project_packages[projectName]:
				if first is True:
					first=False
				else:
					print(", ",end='')
				print(packageName,end='')
			print(" have cve:")
			for cve in cves:
				print(" "+cve)
	if assumeNo is True or dumpFileOnly is True:
		return False
	
	print('Are you true to continue? (y/n)')
	userinput=input()
	if userinput=='y':
		return True
	else:
		print('abort')
	return False


def core(args,setyes=False):
	cmd="/usr/bin/dnf"
	setyes=False
	for arg in args:
		cmd+=" "+arg
		if arg=='-y':
			setyes=False
	if setyes is True:
		cmd+=" -y"
	return os.system(cmd)

def user_main(args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='--assumeno' or arg=='-y':
			errcode=core(args)
			break
	if errcode is None:
		for arg in args:
			if arg=='install':
				if main(args) is True:
					errcode=core(args,setyes=True)
				else:
					errcode=0
				break
	if errcode is None:
		errcode=core(args)

	if exit_code:
		sys.exit(errcode)
	return errcode

if __name__ == '__main__':
	user_main(sys.argv[1:],True)