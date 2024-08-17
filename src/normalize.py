#对字符串中的特殊字符进行替换

def normalReplace(s:str)->str:
	s=s.replace('~','-tilde-')
	s=s.replace('+','-plus-')
	s=s.replace('_','-underline-')
	return s

def reNormalReplace(s:str)->str:
	s=s.replace('-tilde-','~')
	s=s.replace('-plus-','+')
	s=s.replace('-underline-','_')
	return s