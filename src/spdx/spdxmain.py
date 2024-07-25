
def spdxmain(packageName,packageFilePath,purlList):
	print("binary deb file at: "+packageFilePath)
	print("purl for: "+packageName)
	for purl in purlList:
		print(' '+purl)
