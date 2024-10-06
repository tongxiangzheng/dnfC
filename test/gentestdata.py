import os,sys
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import RepoFileManager

repoFileManager=RepoFileManager.RepoFileManager("./openEuler-appstream-primary.xml.zst","openEuler","24.03","")

packages=set()
for package in repoFileManager.getAllPackages():
	skipPrefix=["linux","gcc","llvm","texlive","language","dotnet","ceph"]
	skip=False
	for p in skipPrefix:
		if package.packageInfo.name.startswith(p):
			skip=True
			break
	if skip is True:
		continue
	if package.arch!="x86_64":
		continue
	if package.fullName in packages:
		continue
	packages.add(package.fullName)
	if package.packageInfo.release is None:
		print(package.packageInfo.name,package.fullName,package.packageInfo.version)
	else:
		print(package.packageInfo.name,package.fullName,package.packageInfo.version,package.packageInfo.release)