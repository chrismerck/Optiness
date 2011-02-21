


"""
A Simple Maze Game written in Python
Chris Merck

Object: To reach the right-hand side of the screen.
"""

import pygame
import random
import copy

xmax = 100
ymax = 80
scale = 10
pxmax = xmax*scale
pymax = ymax*scale

screen = pygame.display.set_mode((pxmax,pymax))
running = 1

wall_color = (180,85,20)
floor_color = (0,0,0)

# tile types:
floor = 0
wall = 1

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
	dna = []
	hist = []
	bestx = 0

	def Init(self):
		self.dna = []
		self.dna = [random.sample(basepairs,1)[0] for i in range(dnalen)]

	def Run(self,maze):
		x = 1
		y = ymax/2
		self.hist = [(x,y)]
		self.bestx = x

		for bp in self.dna:
			nx = x + bp[0]
			ny = y + bp[1]

			if maze.world[nx][ny] == floor:
				x = nx
				y = ny
				self.hist.append((x,y))
			
			if x>self.bestx:
				self.bestx=x

	def Fitness(self):
		# first run in a maze!
		return self.bestx

	def Draw(self):
		for coord in self.hist:
			x = coord[0]
			y = coord[1]
			rect = pygame.Rect(x*scale,y*scale,scale,scale)
			pygame.draw.rect(screen,(200,200,200),rect)

	def Mutate(self,strength):
		for i in range(dnalen):
			if random.random()<strength:
				self.dna[i] = random.sample(basepairs,1)[0]

class Population:
	pop = []
	maze = 0

	def __init__(self,size):
		self.Init(size)

	def Init(self,size):
		for i in range(size):
			indiv = Indiv()
			indiv.Init()
			self.pop.append(indiv)

	def SetMaze(self,maze):
		self.maze = maze

	def Evolve(self):
		if self.maze == 0:
			print "Population Error: Maze not set."
			exit()

		# evaluate fitnesses
		print "(",
		for i in self.pop:
			i.Run(self.maze)
			print i.Fitness(),
		print ")"

		# sort by fitness
		self.pop.sort(key=lambda i: -i.Fitness())

		# survival of the fittest and reproduction
		for i in range(len(self.pop)/2):
			j = i+len(self.pop)/2
			self.pop[j] = copy.deepcopy(self.pop[i])

		for i in self.pop:
			i.Mutate(.01)

	def Draw(self):
		self.pop[9].Draw()
		

class Maze:
	world = [[]]

	def __init__(self,seed):
		self.Make(seed)

	def Make(self,seed):

		# God does not play dice
		random.seed(seed)

		# all wall tiles at first
		self.world = [[wall for i in range(ymax)] for j in range(xmax)]

		# start on left side in the middle
		x = 1
		y = ymax/2

		self.world[x][y]=floor

		# wander around until we hit the right side,
        #  but leaving a border of wall around the outside
		t = 0
		while True:
			if random.randint(0,1)==1:
				step = 1
			else:
				step = -1

			if random.randint(0,1)==1:
				x+=step
			else:
				y+=step

			if x==0:
				x=1
			if y==0:
				y=1
			if x==xmax-1:
				x=xmax-2
				return
			if y==ymax-1:
				y=ymax-2


			self.world[x][y]=floor
			t+=1

	def Draw(self):
		for x in range(xmax):
			for y in range(ymax):
				if self.world[x][y] == wall:
					color = wall_color
				else:
					color = floor_color
				rect = pygame.Rect(x*scale,y*scale,scale,scale)
				pygame.draw.rect(screen,color,rect)


maze = Maze(1)
pop = Population(30)
pop.SetMaze(maze)
dude = Indiv()
dude.Init()
dude.Run(maze)

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running=0

	pop.Evolve()

	maze.Draw()
	pop.Draw()
	pygame.display.flip()


