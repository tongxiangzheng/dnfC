import json
import os
class dnfcConfigure:
	def __init__(self,configObj):
		self.serverURL=configObj['server']['url']


def checkConfig(configObj)->bool:
	if 'server' not in configObj:
		return False
	server=configObj['server']
	if 'url' not in server:
		return False
	return True
def loadConfig():
	if not os.path.isfile('/etc/dnfC/config.json'):
		return None
	with open('/etc/dnfC/config.json',"r") as f:
		configObj=json.load(f)
	if checkConfig(configObj) is False:
		return None
	return dnfcConfigure(configObj)