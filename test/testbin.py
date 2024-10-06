import autotest_binary

testName="evolution-data-server"
with open("jammyinfo.txt") as f:
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
	res.append((fullName,version,release))
autotest_binary.autotest_binary(res,checkExist=False)
