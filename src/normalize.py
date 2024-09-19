#对字符串中的特殊字符进行替换

def normalReplace(s:str)->str:
	s=s.replace('~','-tilde-')
	s=s.replace('+','-plus-')
	s=s.replace('_','-underline-')
	s=s.replace('@','-at-')
	s=s.replace('/','-slash-')
<<<<<<< HEAD
=======
	# s=s.replace('\','backslash')
>>>>>>> b3a5e7ecb30df5015c5a280c5a32269ef344bec7
	return s

def reNormalReplace(s:str)->str:
	s=s.replace('-tilde-','~')
	s=s.replace('-plus-','+')
	s=s.replace('-underline-','_')
	s=s.replace('-at-','@')
	s=s.replace('-slash-','/')
	return s