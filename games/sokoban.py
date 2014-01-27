#!/usr/bin/env python2

"""
A block pushing game written in Python
Darren Alton

Based on Maze by Chris Merck

Object: To push all the blocks into holes.
"""

import pygame
import random
import os

from skeleton_game import Game

wall_color = (100,50,50)
floor_color = (150,150,150)
hole_color = (100,100,100)
player_color = (250,250,250)
box_color = (200,150,0)
boxhole_color = (150,100,0)

# tile types:
floor = 0
wall = 1

# '#' denotes a wall
# '@' denotes a man (max 1)
# '`' denotes a box
# '^' denotes a hole
# '*' denotes a box already on a hole

def _valid_mapfile(fname):
    if os.path.isfile(fname):
        x = open(fname, 'r').read()
        return type(x) is str \
            and x.count('@') == 1 and x.count('^') == x.count('`') \
            and set(x).issubset(set('#@`^* \n'))
    return False

defaultargs = { 'map': 'data/wikipedia.org_wiki_Sokoban.txt' }
validargs = { 'map': _valid_mapfile }

def manhattan_distance((x1, y1), (x2, y2)):
    return abs(x1 - x2) + abs(y1 - y2)

class Sokoban(Game):
    name = 'sokoban'

    def __init__(self, args = {}):
        Game.__init__(self, args, defaultargs, validargs)

        self.inputs = { 'hat0_up':    0b0001,
                        'hat0_down':  0b0010,
                        'hat0_left':  0b0100,
                        'hat0_right': 0b1000 }

        # parse map
        lines = open(self.args['map'], 'r').read().strip('\n').split('\n')
        self.w, self.h = (max(len(l) for l in lines), len(lines))

        # all floor tiles at first
        # world[x][y] corresponds to lines[y][x] here.
        self.world = [[floor for i in xrange(self.h)] for j in xrange(self.w)]

        # generating the surface as we go along too
        self.surf = pygame.Surface((self.w, self.h))
        self.surf.fill(floor_color)

        self.boxes = set()
        self.holes = set()
        for y in xrange(self.h):
            for x in xrange(len(lines[y])):
                char = lines[y][x]
                xy = (x, y)
                if char == '#':
                    self.world[x][y] = wall
                    self.surf.set_at(xy, wall_color)
                elif char == '@':
                    self.xpos, self.ypos = xy
                elif char == '`':
                    self.boxes.add(xy)
                elif char == '^':
                    self.holes.add(xy)
                    self.surf.set_at(xy, hole_color)
                elif char == '*':
                    self.boxes.add(xy)
                    self.holes.add(xy)
                    self.surf.set_at(xy, hole_color)
        self.holes = frozenset(self.holes)

    def Draw(self):
        ret = self.surf.copy()
        ret.set_at((self.xpos, self.ypos), player_color)
        for box in self.boxes:
            if box in self.holes:
                ret.set_at(box, boxhole_color)
            else:
                ret.set_at(box, box_color)
        return ret

    def TrappedBox(self, (x, y)):
        if (x, y) in self.holes:
            return False
        neighbors = [
            [(not self.EmptySquare(x+i, y+j)) for j in (-1, 0, 1)]
                for i in (-1, 0, 1)
        ]
        NW = neighbors[0][0]
        N  = neighbors[1][0]
        NE = neighbors[2][0]
        E  = neighbors[2][1]
        SE = neighbors[2][2]
        S  = neighbors[1][2]
        SW = neighbors[0][2]
        W  = neighbors[0][1]
        return (N and ((NW and W) or (NE and E))) \
            or (S and ((SW and W) or (SE and E)))

    def Heuristic(self):
        if any(self.TrappedBox(box) for box in self.boxes):
            return float('inf')
        return sum(
            min(
                manhattan_distance(hole, box) for box in self.boxes
            ) for hole in self.holes
        )

    def EmptySquare(self, x, y):
        "True iff (x, y) is in-bounds and a valid position for a man or a box"
        return 0 <= x < self.w and 0 <= y < self.h \
            and self.world[x][y] == floor and (x, y) not in self.boxes

    def Input(self, n):
        if n == 0:  return

        nx, ny = (self.xpos, self.ypos) # new player position
        px, py = (self.xpos, self.ypos) # pushed block position, if applicable

        if n & 0b0011: # vertical
            if n & 0b0001: # up
                ny -= 1
                py -= 2
            else: # down
                ny += 1
                py += 2
        else: # horizontal
            if n & 0b0100: # left
                nx -= 1
                px -= 2
            else: # right
                nx += 1
                px += 2

        if (nx, ny) in self.boxes and self.EmptySquare(px, py):
            self.xpos = nx
            self.ypos = ny
            self.boxes.remove((nx, ny))
            self.boxes.add((px, py))
        # if we didn't run into a wall or out of bounds, that's our new position
        elif self.EmptySquare(nx, ny):
            self.xpos = nx
            self.ypos = ny

    def HumanInputs(self):
        return self.inputs

    def ValidInputs(self):
        return self.inputs.values()

    def Freeze(self):
        return (self.xpos, self.ypos, frozenset(self.boxes))

    def Thaw(self, data):
        self.xpos, self.ypos, self.boxes = data
        self.boxes = set(self.boxes)

    def Victory(self):
        return self.boxes == self.holes



LoadedGame = Sokoban
