from sys import argv
from cPickle import load

if __name__ == "__main__" and len(argv) > 1:
	p = load(open(argv[1]))
	if type(p) == dict:
		if len(argv) > 2:
			for i in argv[2:]:
				print repr(p[i])
		else:
			print 'keys:',
			for i in p:
				print i,
	else:
		print p
