from sys import argv
from cPickle import load

def show_data(p, keys=[]):
	if type(p) == dict:
		if len(keys):
			if len(keys) == 1 and keys[0] == '.':
				print '{', '\n  '.join([ '{}:\t{}'.format(i, repr(p[i])) for i in p ]), '}'
			else:
				show_data(p[keys[0]], keys[1:])
		else:
			print 'keys: ', ' '.join(p)
	else:
		print p

if __name__ == "__main__" and len(argv) > 1:
	show_data( load( open(argv[1]) ), argv[2:] )
