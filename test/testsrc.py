import autotest_src
testName="cracklib"
with open("openEulerinfo.txt") as f:
	data=f.readlines()
res=[]
for info in data:
	if info.startswith("#"):
		continue
	info=info.split(' ')
	name=info[0].strip()
	if name!=testName:
		continue
	fullName=info[1].strip()
	version=info[2].strip()
	if len(info)>3:
		release=info[3].strip()
	else:
		release=None
	autotest_src.autotest_src(testName,fullName,version,release,checkExist=False)
	break