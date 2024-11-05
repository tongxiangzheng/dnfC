import sys
import os
import traceback
import wget
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import dnfC
import normalize
from subprocess import PIPE, Popen
def autotest_src(name,fullname,version,release,checkExist=True):
	if checkExist:
		if os.path.isfile(f"./src/{name}/"+normalize.normalReplace(f"{fullname}.spdx.json")):
			return 0
		# if not os.path.isfile(f"./binary/{name}/"+normalize.normalReplace(f"{fullname}.spdx.json")):
		# 	return 0
	print(name,version,release)
	#if name<"colord":
	#	return 
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
		#print(srcLink)
		#wget.download(srcLink,out=srcFile)
		#os.system("wget "+srcLink)
	
	if not os.path.isfile(srcFile):
		print("error: no src file")
		return 1
	else:
		try:
			if not os.path.isdir(f"./src/{name}"):
				os.mkdir(f"./src/{name}")
			res=dnfC.user_main(["scansrc",srcFile,f"--genspdx=./src/{name}"], exit_code=False)
			if res==1:
				os.system(f"rm {srcFile}")
			return res
		except Exception:
			traceback.print_exc()
			return 1
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
		if autotest_src(name,fullname,version,release) != 0:
			print(name,version,release)
			#break
