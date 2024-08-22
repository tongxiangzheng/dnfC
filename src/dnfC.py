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

def queryCVE(spdxObj,aptConfigure:loadConfig.aptcConfigure):
	url=aptConfigure.serverURL
	response = requests.post(url, json=spdxObj)
	if response.status_code == 200:
		return response.json()
	else:
		log.warning(f'Request failed with status code {response.status_code}')
		return {}
def main(args):
	sourcesListManager=SourcesListManager.SourcesListManager()
	selectedPackages_willInstallPackages=getNewInstall.getNewInstall(args,sourcesListManager)
	if len(selectedPackages_willInstallPackages)==0:
		return True
	aptConfigure=loadConfig.loadConfig()
	if aptConfigure is None:
		print('ERROR: cannot load config file in /etc/dnfC/config.json, please check config file ')
		return False
	for selectedPackage,willInstallPackages in selectedPackages_willInstallPackages.items():
		selectedPackageName=selectedPackage.fullName
		depends=dict()
		for p in willInstallPackages:
			depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
		dependsList=list(depends.values())
		packageFilePath=downloadPackage(selectedPackage)
		spdxPath=spdxmain(selectedPackageName,packageFilePath,dependsList)
		with open(spdxPath,"r") as f:
			spdxObj=json.load(f)
		cves=queryCVE(spdxObj,aptConfigure)
		for packageName,cves in cves.items():
			if len(cves)==0:
				continue
			print(packageName+" have cve:")
			for cve in cves:
				print(" "+cve)
	return False


def core(args):
	cmd="/usr/bin/dnf"
	setyes=False
	for arg in args:
		cmd+=" "+arg
		if arg=='-y':
			setyes=True
	if setyes is False:
		cmd+=" -y"
	return os.system(cmd)
def user_main(args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='--assumeno':
			errcode=core(args)
			break
	if errcode is None:
		for arg in args:
			if arg=='install':
				if main(args) is False:
					errcode=1
				break
	if errcode is None:
		errcode=core(args)

	if exit_code:
		sys.exit(errcode)
	return errcode

if __name__ == '__main__':
	user_main(sys.argv[1:],True)