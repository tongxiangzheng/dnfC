import os
import json
import spdxReader
cnt=0
for file in os.listdir("./src"):
	if not os.path.isfile("./binary/"+file):
		#print("")
		#print(file+" not in binary")
		continue
	cnt+=1
	srcres=dict()
	binres=dict()
	with open("./src/"+file) as f:
		spdxObj=json.load(f)
		res=spdxReader.parseSpdxObj(spdxObj)
		for s in res:
			srcres[s.name]=s
	with open("./binary/"+file) as f:
		spdxObj=json.load(f)
		res=spdxReader.parseSpdxObj(spdxObj)
		for s in res:
			binres[s.name]=s
	needOutput=False
	for s in srcres.values():
		if s.name not in binres:
			needOutput=True
			break
	for s in binres.values():
		if s.name not in srcres:
			needOutput=True
			break
	if needOutput is False:
		continue
	print("")
	print(file)
	print("src:")
	for s in srcres.values():
		if s.name not in binres:
			print(s.name,s.version,s.release)
	print("--")
	print("binary:")
	for s in binres.values():
		if s.name not in srcres:
			print(s.name,s.version,s.release)


print(f"check {cnt} pairs")