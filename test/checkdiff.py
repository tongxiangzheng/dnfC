with open("resbin.txt") as f:
	bindata=f.readlines()
with open("ressrc.txt") as f:
	srcdata=f.readlines()

binres=dict()
packageName=""
for item in bindata:
	if item.startswith("% "):
		dep=set()
		for p in item[1:].strip().split(" "):
			dep.add(p)
		binres[packageName]=dep
	elif item.startswith("%"):
		packageName=item[1:].split(" ",1)[0]

srcres=dict()
packageName=""
for item in srcdata:
	if item.startswith("% "):
		dep=set()
		for p in item[1:].strip().split(" "):
			dep.add(p)
		srcres[packageName]=dep
	elif item.startswith("%"):
		packageName=item[1:].split(" ",1)[0]
for packageName,bindep in binres.items():
	if packageName not in srcres:
		print("bin: "+packageName+" ")
		for d in bindep:
			print(" "+d,end="")
		print("")
		continue
	srcdep=srcres[packageName]
	for d in bindep:
		if d not in srcdep:
			print("bin: "+packageName+" "+d)
	for d in srcdep:
		if d not in bindep:
			print("src: "+packageName+" "+d)
for packageName,srcdep in srcres.items():
	if packageName not in binres:
		print("src: "+packageName+" ")
		for d in srcdep:
			print(" "+d,end="")
		print("")
		