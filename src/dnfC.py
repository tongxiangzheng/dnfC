import sys
import os
import getNewInstall
import SourcesListManager
import nwkTools
from loguru import logger as log
from spdx.spdxmain import spdxmain 
def downloadPackage(selectedPackage):
	print(selectedPackage.repoURL)
	print(selectedPackage.fileName)
	return nwkTools.downloadFile(selectedPackage.repoURL+'/'+selectedPackage.fileName,'/tmp/dnfC/packages',selectedPackage.fileName.rsplit('/',1)[1])
	
def main(args):
	sourcesListManager=SourcesListManager.SourcesListManager()
	selectedPackages_willInstallPackages=getNewInstall.getNewInstall(args,sourcesListManager)
	for selectedPackage,willInstallPackages in selectedPackages_willInstallPackages.items():
		selectedPackageName=selectedPackage.fullName
		purls=set()
		for p in willInstallPackages:
			purls.add(p.packageInfo.dumpAsPurl())
		purlList=list(purls)
		packageFilePath=downloadPackage(selectedPackage)
		spdxObject=spdxmain(selectedPackageName,packageFilePath,purlList)

	return False


def core(args):
	cmd="/usr/bin/apt"
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