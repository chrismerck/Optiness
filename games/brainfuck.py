#!/usr/bin/env python2

"""
A straightforward brainfuck interpreter in Python
Darren Alton

Object: To code a brainfuck program that prints a given string.
"""

from skeleton_game import Game

import pygame

defaultargs = { 'output': 'foo' }
validargs =   { 'output': lambda x: type(x) is str }

class Brainfuck(Game):
    name = 'brainfuck'

    def __init__(self, args = {}):
        Game.__init__(self, args, defaultargs, validargs)

        self.program = ''
        self.current_output = ''
        self.desired_output = self.args['output']

        # , is omitted because it could just produce a BF implementation of cat
        self.inputs = { 'hat0_up':    '+',
                        'hat0_down':  '-',
                        'hat0_left':  '<',
                        'hat0_right': '>',
                        0: '.',
                        1: '[',
                        2: ']' }

        pygame.font.init()
        self.pg_font = pygame.font.Font(None, 16)


    def Heuristic(self):
        # if we have a ] before [, never fixed by appending more opcodes...
        if not self.ValidProgram(self.program):
            return float('inf')

        try:
            output = self.InterpretBF(self.program)
        except: # runtime errors are obviously dead ends~
            print self.program
            return float('inf')

        # if we've gone too far, dead end
        if len(output) > len(self.desired_output):
            return float('inf')

        # count the number of characters that still need to be printed
        characters_remaining = len(self.desired_output)
        for i in xrange(len(output)):
            # if we've printed an incorrect character, dead end
            if output[i] != self.desired_output[i]:
                return float('inf') # TODO: allow \b backspaces?  \n gets messy
            characters_remaining -= 1
        return characters_remaining

    def Input(self, n):
        self.program += n
        self.current_output = None

    def HumanInputs(self): return self.inputs
    def ValidInputs(self): return self.inputs.values()

    def Freeze(self):
        return self.program
    def Thaw(self, data):
        self.program = data
        self.current_output = None

    # check for bracket balance, being forgiving about the end of the program
    def ValidProgram(self, subprog):
        balance = 0
        for i in xrange(len(subprog)):
            if   subprog[i] == '[': balance += 1
            elif subprog[i] == ']': balance -= 1
            if balance < 0:         return False
        return True

    # implicitly closes open brackets, just like the TI-83
    def BracketedSubstring(self, subprog):
        balance = 0
        has_nonbracket = False
        for i in xrange(len(subprog)):
            if subprog[i] == '[':
                balance += 1
            elif subprog[i] == ']':
                balance -= 1
            else:
                has_nonbracket = True
            if balance < 0:
                return subprog[:i]
        if has_nonbracket:
            return subprog
        return "" # performance hack, since [[][][[]]] and [] are equivalent

    def InterpretBF(self, prog):
        if '.' not in prog: return '' # shortcut!
        self.tape = [0]
        self.position = 0
        if self.current_output is None:
            self.current_output = self.InterpretBFSub(prog)
        return self.current_output

    def InterpretBFSub(self, prog):
        output = ''
        pc = 0
        while pc < len(prog):
            opcode = prog[pc]
            pc += 1
            if opcode == '.':   output += chr(self.tape[self.position])
            elif opcode == '+':
                self.tape[self.position] += 1
                self.tape[self.position] &= 0xFF
            elif opcode == '-':
                self.tape[self.position] -= 1
                self.tape[self.position] &= 0xFF
            elif opcode == '>':
                self.position += 1
                if len(self.tape) <= self.position:
                    self.tape.append(0)
            elif opcode == '<':
                if self.position == 0:
                    self.tape.insert(0, 0)
                else:
                    self.position -= 1
            elif opcode == '[':
                loop_body = self.BracketedSubstring(prog[pc:])
                iter_count = 0 # FIXME when halting problem is solved
                while self.tape[self.position] and iter_count < 0x100:
                    output += self.InterpretBFSub(loop_body)
                    iter_count += 1
                pc += len(loop_body) + 1
        return output

    def Draw(self):
        screen = Game.Draw(self)
        surf_pgm = self.pg_font.render(self.program, False, (255,255,255))
        screen.blit(surf_pgm, (8,8))
        if self.current_output and len(self.current_output) > 1:
            surf_out = self.pg_font.render(self.current_output[:len(self.desired_output)], False, (255,255,255))
            screen.blit(surf_out, (8,108))
        return screen

LoadedGame = Brainfuck
