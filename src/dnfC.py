import sys
import os
import getNewInstall
import SourcesListManager
import nwkTools
from loguru import logger as log
from spdx.spdxmain import spdxmain 
def downloadPackage(selectedPackage):
	return nwkTools.downloadFile(selectedPackage.repoURL+'/'+selectedPackage.fileName,'/tmp/aptC/packages',selectedPackage.fileName.rsplit('/',1)[1])
	
def main(command,options,packages):
	sourcesListManager=SourcesListManager.SourcesListManager()
	packageProvides=dict()
	for selectedPackageName in packages:
		selectedPackage,willInstallPackages=getNewInstall.getNewInstall(selectedPackageName,options,sourcesListManager)
		continue
		if selectedPackage is None:
			continue
		selectedPackageName=selectedPackage.fullName
		packageProvides[selectedPackageName]=willInstallPackages
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
def parseCommand(args):
	command=None
	options=[]
	packages=[]
	for arg in args:
		if arg.startswith('-'):
			options.append(arg)
		else:
			if command is None:
				command=arg
			else:
				packages.append(arg)
	return command,options,packages
def user_main(args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='-s':
			errcode=core(args)
			break
	if errcode is None:
		command,options,packages=parseCommand(args)
		if command=='install' or command=='reinstall':
			if main(command,options,packages) is False:
				errcode=1
	if errcode is None:
		errcode=core(args)

	if exit_code:
		sys.exit(errcode)
	return errcode

if __name__ == '__main__':
	user_main(sys.argv[1:],True)