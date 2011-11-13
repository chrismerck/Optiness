#!/usr/bin/env python2

"""
Optiness command line UI

Darren Alton
"""

import sys, getopt

# Optiness driver, which handles game and brain modules
import common

# default game and solver to use
game_mod_name, brain_mod_name = ('maze', 'sagan')
game_args, brain_args = ({}, {})

scale = 1                          # we may want to make the display output bigger
output = 'output/last_run.pickle'  # default value for the output pickle



def usage():
	return """
todo: help.  for now, here's a list of game and brain modules:
{}
{}
""".format( list(common.util.ListGames()),
            list(common.util.ListBrains()) )



if __name__ == "__main__":
	# parse command line arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hg:b:s:o:", ["help", "game=", "brain=", "scale=", "output="])

		for o,a in opts:
			if o in ('-h', '--help'):
				print usage()
				sys.exit(0)
			elif o in ('-g', '--game'):
				subargs = a.split(';')
				game_mod_name = subargs[0]
				for i in subargs[1:]:
					key,val = i.split(':')
					game_args[key] = val
			elif o in ('-b', '--brain'):
				subargs = a.split(';')
				brain_mod_name = subargs[0]
				for i in subargs[1:]:
					key,val = i.split(':')
					brain_args[key] = val
			elif o in ('-s', '--scale'):
				scale = int(a)
			elif o in ('-o', '--output'):
				output = a
	except getopt.GetoptError, err:
		print str(err), usage()
		sys.exit(2)

	# run optiness with parsed arguments
	driver = common.Driver(game_mod_name, brain_mod_name, game_args, brain_args, scale)
	driver.Run()
	driver.Save(output)
