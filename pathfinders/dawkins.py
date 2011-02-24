#!/usr/bin/env python2

"""
Genetic algorithm for 'Simple Maze Game written in Python'
Chris Merck

Object: To reach the right-hand side of the screen.
"""

import random
import copy

# directions
up = (0,-1)
down = (0,1)
left = (-1,0)
right = (1,0)

# base-pairs 
A = up
T = down
G = left
C = right
basepairs = [A, T, G, C]
dnalen = 200

class Indiv:
	def __init__(self,maze):
		self.dna = [random.sample(basepairs,1)[0] for i in xrange(dnalen)]
		self.maze = maze
		self.bestx = 0
		self.hist = []
		self.lastx = 0
		self.lasty = 0

	def Run(self):
		p1 = self.maze.player

		p1.ResetHistory()
		self.bestx = 0
		for bp in self.dna:
			p1.Move(*bp)
			if p1.xpos > self.bestx:
				self.bestx = p1.xpos

		self.hist = p1.hist
		self.lastx = p1.xpos
		self.lasty = p1.ypos

	def Fitness(self):
		# first run in a maze!
		return self.bestx

	def Mutate(self,strength):
		avg_point_mutations = 1
		avg_swaps = 10
		avg_deletions = 3

		# perform point mutations
		npoint = int(random.random()*strength*avg_point_mutations)
		for n in xrange(npoint):
			i = random.randint(0,dnalen-1)
			self.dna[i] = random.sample(basepairs,1)[0]

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
			self.dna[j] = random.sample(basepairs,1)[0]


class Population:
	def __init__(self,size,maze):
		self.pop = []
		self.maze = maze
		for i in xrange(size):
			self.pop.append(Indiv(maze))

	def Evolve(self):
		# evaluate fitnesses
		print "(",
		for i in self.pop:
			i.Run()
			print i.Fitness(),
		print ")"

		# sort by fitness
		self.pop.sort(key=lambda i: -i.Fitness())

		# FIXME HACK: for visualization, we cram the 9th-best run's history
		#   back into Maze's "Player" before the screen is drawn
		p1 = self.maze.player
		superman = self.pop[9]
		p1.hist = superman.hist
		p1.xpos = superman.lastx
		p1.ypos = superman.lasty

		# survival of the fittest and reproduction
		for i in xrange(len(self.pop)/2):
			j = i+len(self.pop)/2
			self.pop[j] = copy.deepcopy(self.pop[i])

		for i in self.pop:
			i.Mutate(1)

