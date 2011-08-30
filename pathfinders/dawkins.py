#!/usr/bin/env python2

"""
Genetic algorithm for 'Simple Maze Game written in Python'
Chris Merck

Object: To reach the right-hand side of the screen.
"""

# supported games for this solver, just 'maze' for now
supported_games = [ 'maze' ]

import random
import copy


dnalen = 300


class Brain:
	name = 'dawkins'

	def __init__(self, game, popsize = 30):
		if game.name not in supported_games:
			raise Exception('solver "%s" does not play game "%s"' % (name, game.name))

		self.game = game
		self.pop = Population(popsize, game)

	def Step(self):
		# we deviate a bit from the biblical record here
		self.pop.Evolve()
		return self.game.Draw()

	def Event(self, evt):
		pass


class Indiv:
	def __init__(self, game):
		self.game = game
		self.dna = [random.choice(self.game.valid_inputs) for i in xrange(dnalen)]
		self.hist = []
		self.lastx = 0
		self.lasty = 0

	def Run(self):
		self.game.Reset()
		for bp in self.dna:
			self.game.Input(bp)

	def Mutate(self,strength):
		avg_point_mutations = 1
		avg_swaps = 10
		avg_deletions = 3

		# perform point mutations
		npoint = int(random.random()*strength*avg_point_mutations)
		for n in xrange(npoint):
			i = random.randint(0,dnalen-1)
			self.dna[i] = random.choice(self.game.valid_inputs)

		# perform swap mutations
		nswap = int(random.random()*strength*avg_swaps)
		for n in xrange(nswap):
			i = random.randint(0,dnalen-2)
			j = i+1 # for now we just swap with next base
			tmp = self.dna[i]
			self.dna[i] = self.dna[j]
			self.dna[j] = tmp

		# perform "deletions" (actually MOVEs to end)
		ndeletions = int(random.random()*strength*avg_deletions)
		for n in xrange(ndeletions):
			i = random.randint(0,dnalen-2)
			j = dnalen-1

			# delete ith base, shifting left
			for k in xrange(i,j):
				self.dna[i]=self.dna[i+1]

			# add a random base at the end to maintain length
			self.dna[j] = random.choice(self.game.valid_inputs)

# TODO: continue working on making "game" a unit rather than having hooks into "player"
class Population:
	def __init__(self, size, game):
		self.pop = []
		self.game = game
		for i in xrange(size):
			self.pop.append(Indiv(game))

	def Evolve(self):
		# evaluate fitnesses
		print "(",
		for i in self.pop:
			i.Run()
			print i.game.Fitness(),
		print ")"

		# sort by fitness
		self.pop.sort(key=lambda i: -i.game.Fitness())

		# survival of the fittest and reproduction
		for i in xrange(len(self.pop)/2):
			j = i+len(self.pop)/2
			self.pop[j] = copy.deepcopy(self.pop[i])

		for i in self.pop:
			i.Mutate(1)


