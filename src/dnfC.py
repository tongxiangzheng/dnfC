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
			errcode=runDnf(args)
			break
	if errcode is None:
		for arg in args:
			if arg=='install':
				if scanDnf.scanDnf(args) is True:
					errcode=runDnf(args,setyes=True)
				else:
					errcode=0
				break
			if arg=='scansrc':
				errcode=scanSrc.scansrc(args[1])
				break
	if errcode is None:
		errcode=runDnf(args)

	if exit_code:
		sys.exit(errcode)
	return errcode

#if __name__ == '__main__':
#	user_main(sys.argv[1:],True)