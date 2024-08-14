#对字符串中的特殊字符进行替换

def normalReplace(s):
	s=s.replace('~','-tilde-')
	return s

def reNormalReplace(s):
	s=s.replace('-tilde-','~')
	return s