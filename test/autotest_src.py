import sys
import os
import time
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import dnfC
import normalize
from subprocess import PIPE, Popen
def autotest_src(name,fullname,version,release,checkExist=True):
	if checkExist:
		if os.path.isfile("./src/"+normalize.normalReplace(f"{fullname}.spdx.json")):
			return 0
		if not os.path.isfile("./binary/"+normalize.normalReplace(f"{fullname}.spdx.json")):
			return 0
	print(name,version,release)
	version=version.split(':')[-1]
	if release is None:
		srcLink=f"https://mirrors.aliyun.com/openeuler/openEuler-24.03-LTS/source/Packages/{name}-{version}.src.rpm"
		srcFile=f"./source/{name}-{version}.src.rpm"
	else:
		srcLink=f"https://mirrors.aliyun.com/openeuler/openEuler-24.03-LTS/source/Packages/{name}-{version}-{release}.src.rpm"
		srcFile=f"./source/{name}-{version}-{release}.src.rpm"
	if not os.path.isfile(srcFile):
		p = Popen("wget "+srcLink, shell=True, stdout=PIPE, stderr=PIPE,cwd="./source")
		stdout, stderr = p.communicate()
	
	if not os.path.isfile(srcFile):
		print("error: no src file")
		return 1
	else:
		return dnfC.user_main(["scansrc",srcFile,"--genspdx=./src"], exit_code=False)

if __name__ == "__main__":
	with open("openEulerinfo.txt") as f:
		data=f.readlines()
	checked=set()
	for info in data:
		if info.startswith("#"):
			continue
		info=info.split(' ')
		name=info[0].strip()
		fullname=info[1].strip()
		if name in checked:
			continue
		checked.add(name)
		version=info[2].strip()
		if len(info)>3:
			release=info[3].strip()
		else:
			release=None
		#autotest_deb(name,version,release)
		if autotest_src(name,fullname,version,release) != 0:
			print(name,version,release)
			#break
