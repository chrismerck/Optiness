#!/usr/bin/env python2

"""
Genetic algorithm for 'Simple Maze Game written in Python'
Chris Merck

Object: To reach the right-hand side of the screen.
"""


import random

from skeleton_solver import Brain

dnalen = 300

class Indiv:
	def __init__(self, game):
		self.game = game
		self.init_state = self.game.Freeze()
		self.dna = [random.choice(self.game.ValidInputs()) for i in xrange(dnalen)]
		self.fitness = float("inf")

	def Run(self):
		self.game.Thaw(self.init_state)
		steps = 0
		for bp in self.dna:
			self.game.Input(bp)
			steps += 1
			if self.game.Victory(): return steps
		self.fitness = self.game.Heuristic()
		return -1

	# for sorting based on fitness
	def __le__(self, other):
		return self.fitness <= other.fitness

	def Copy(self, other):
		self.dna = other.dna[:]
		self.fitness = other.fitness

	def Mutate(self,strength):
		avg_point_mutations = 1
		avg_swaps = 10
		avg_deletions = 3

		# perform point mutations
		npoint = int(random.random()*strength*avg_point_mutations)
		for n in xrange(npoint):
			i = random.randint(0,dnalen-1)
			self.dna[i] = random.choice(self.game.ValidInputs())

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
			self.dna[j] = random.choice(self.game.ValidInputs())

class Dawkins(Brain):
	name = 'dawkins'

	def __init__(self, game, popsize = 30):
		Brain.__init__(self, game)
		self.pop = [Indiv(game) for i in xrange(popsize)]
		self.input_string = (float("inf"), [])

	def Step(self):
		# we deviate a bit from the biblical record here

		# evaluate fitnesses
		print "(",
		for i in self.pop:
			win_steps = i.Run()
			if win_steps > -1:
				if win_steps < self.input_string[0]:
					self.input_string = (win_steps, i.dna)
			print i.fitness,
		print ")"

		self.pop.sort() # sort by fitness

		# survival of the fittest and reproduction
		for i in xrange(len(self.pop)/2):
			j = i+len(self.pop)/2
			self.pop[j].Copy(self.pop[i])

		self.pop[0].Run()
		yield self.game.Draw()

		for i in self.pop:
			i.Mutate(1)

	def Path(self):
		return self.input_string[1]


LoadedBrain = Dawkins
