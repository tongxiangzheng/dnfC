import loadConfig
import requests
import json
def queryCVE(spdxObj,dnfConfigure:loadConfig.dnfcConfigure):
	url=dnfConfigure.querycveURL
	try:
		response = requests.post(url, json=spdxObj)
	except requests.exceptions.ConnectionError as e:
		print("failed to query CVE: Unable to connect: "+url)
		return None
	except Exception as e:
		print(f'failed to query CVE: {e}')
		return None
	if response.status_code == 200:
		return response.json()
	else:
		print(f'failed to query CVE: Request failed with status code {response.status_code}')
		return None
	
def queryCVECli(args):
	dnfConfigure=loadConfig.loadConfig()
	if dnfConfigure is None:
		print('ERROR: cannot load config file in /etc/dnfC/config.json, please check config file ')
		return False
	if len(args)==0:
		print("usage: dnf queryCVE <spdxfile>")
		return False
	spdxPath=args[0]
	
	with open(spdxPath,"r") as f:
		spdxObj=json.load(f)
	cves=queryCVE(spdxObj,dnfConfigure)
	haveOutput=False
	if cves is not None:
		for projectName,cves in cves.items():
			if len(cves)==0:
				continue
			haveOutput=True
			print("package: "+projectName)
			print(" have cve:")
			for cve in cves:
				print(" "+cve['name']+", score: "+str(cve['score']))
	else:
		haveOutput=True
	if haveOutput is False:
		print("All packages have no CVE")
	return False