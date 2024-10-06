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
import scanSrc
import scanDnf
#from spdx.spdxmain import spdxmain


def runDnf(args,setyes=False):
	cmd="/usr/bin/dnf"
	setyes=False
	for arg in args:
		if arg=='-y':
			setyes=False
			cmd+=" "+arg
		elif arg.startswith('--genspdx'):
			pass
		elif arg.startswith('--gencyclonedx'):
			pass
		else:
			cmd+=" "+arg
	if setyes is True:
		cmd+=" -y"
	return os.system(cmd)

def user_main(args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='-y':
			errcode=runDnf(args)
			break
	if errcode is None:
		if args[0]=='install':
			if scanDnf.scanDnf(args) is True:
				errcode=runDnf(args,setyes=True)
			else:
				errcode=0
		elif args[0]=='genspdx':
			if len(args)<3:
				print("unknown usage for apt genspdx")
				return 1
			scanDnf.scanDnf(args[1:-1],genSpdx=True,saveSpdxPath=args[-1],genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=True)
			return 0
		elif args[0]=='gencyclonedx':
			if len(args)<3:
				print("unknown usage for apt gencyclonedx")
				return 1
			scanDnf.scanDnf(args[1:-1],genSpdx=False,saveSpdxPath=None,genCyclonedx=True,saveCyclonedxPath=args[-1],dumpFileOnly=True)
			return 0
		elif args[0]=='scansrc':
			errcode=scanSrc.scansrc(args[1:])
	if errcode is None:
		errcode=runDnf(args)

	if exit_code:
		sys.exit(errcode)
	return errcode

#if __name__ == '__main__':
#	user_main(sys.argv[1:],True)