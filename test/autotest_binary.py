import sys
import os
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import normalize
import dnfC
def autotest_binary(infos,checkExist=True):
	if checkExist:
		for info in infos:
			if os.path.isfile("./binary/"+normalize.normalReplace(f"{info[0]}.spdx.json")):
				return 0
	print("-------")
	packages=["genspdx"]
	for name,version,release in infos:
		print(name,version,release)
		if release is not None:
			packages.append(f"{name}-{version}-{release}")
		else:
			packages.append(f"{name}-{version}")
	packages.append("binary")
	#for info in packages:
	#	print(info,end=' ')
	#print("")
	return dnfC.user_main(packages)

if __name__ == "__main__":
	with open("openEulerinfo.txt") as f:
		data=f.readlines()
	nameMap=dict()
	for info in data:
		if info.startswith("#"):
			continue
		info=info.split(' ')
		name=info[0].strip()
		fullName=info[1].strip()
		version=info[2].strip()
		if len(info)>3:
			release=info[3].strip()
		else:
			release=None
		if name not in nameMap:
			nameMap[name]=[]
		nameMap[name].append((fullName,version,release))
	for name,infos in nameMap.items():
		if autotest_binary(infos)!=0:
			print(infos)
			break
		
		#autotest_src(name,version,release)
