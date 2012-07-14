#!/usr/bin/env python2

from collections import defaultdict
import numpy as np

import ex

class MVC():
	def __init__(self, m, v, c):
		self.m = m
		self.v = v
		self.c = c

	@staticmethod
	def Link(m, v, c):
		global mvc
		mvc = MVC(m, v, c)



mvc = MVC(None, None, None)



class Converter():
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def tup(self, e):
		return (e % self.width, e / self.width)

	def num(self, x, y):
		return y * self.width + x



converter = Converter(1,1)

def w(): return converter.width
def h(): return converter.height
def num(x, y): return converter.num(x, y)
def tup(e): return converter.tup(e)



class TileType():
	ROBOT = ord('R')
	ROCK = ord('*')
	CLL = ord('C')
	EARTH = ord('.')
	WALL = ord('#')
	LAMBDA = ord('\\')
	OLL = ord('O')
	EMPTY = ord(' ')



class MoveType():
	UP, DOWN, LEFT, RIGHT, WAIT, ABORT = range(6)



class ResultType():
	OK, CANNOT_MOVE, DEAD = range(3)



class MoveEvent():
	def __init__(self, old, new, rock):
		self.old = old
		self.new = new
		self.rock = rock
		self.moved_rock = rock is not None

	def apply(self):
		mvc.m.move_robot(self.old, self.new)
		mvc.v.set(self.new, TileType.ROBOT)
		mvc.m.touch(self.old)
		mvc.v.set(self.old, TileType.EMPTY)
		if self.moved_rock:
			mvc.m.move_rock(self.new, self.rock)
			mvc.v.set(self.rock, TileType.ROCK)



class RockEvent():
	def __init__(self, old, new):
		self.old = old
		self.new = new

	def apply(self):
		mvc.m.touch(self.old)
		mvc.v.set(self.old, TileType.EMPTY)
		mvc.m.move_rock(self.old, self.new)
		mvc.v.set(self.new, TileType.ROCK)



def is_move_possible(dir, old, new, rock):
	old_tile = mvc.v.get(old)
	new_tile = mvc.v.get(new)
	rock_tile = mvc.v.get(rock) if rock is not None else None
	if old_tile == TileType.ROBOT:
		if new_tile == TileType.EMPTY or \
			new_tile == TileType.EARTH or \
			new_tile == TileType.LAMBDA:
			return 0
		if new_tile == TileType.ROCK and \
			rock_tile == TileType.EMPTY and \
			(dir == MoveType.LEFT or dir == MoveType.RIGHT):
			return 1
	return -1



class Controller():
	def __init__(self):
		pass

	def update(self):
		current_unstable = list(sorted(mvc.m.unstable_rocks))
		mvc.m.unstable_rocks = set()

		for rock in current_unstable:
			deps = sorted(mvc.m.get_deps(rock))
			l, b, r, ls, rs = deps
			left, bottom, right, lside, rside = mvc.v.get_all(deps)
			if bottom == TileType.EMPTY:
				e = RockEvent(rock, b)
				e.apply()
			elif bottom == TileType.ROCK and rside == TileType.EMPTY and right == TileType.EMPTY:
				e = RockEvent(rock, r)
				e.apply()
			elif bottom == TileType.ROCK and lside == TileType.EMPTY and left == TileType.EMPTY:	
				e = RockEvent(rock, l)
				e.apply()
			elif bottom == TileType.LAMBDA and rside == TileType.EMPTY and right == TileType.EMPTY:
				e = RockEvent(rock, r)
				e.apply()

	def check_if_dead(self):
		robot = mvc.m.robot + w()
		for r in mvc.m.unstable_rocks:
			if robot == r:
				return True
		return False

	def process(self, move):
		if move == MoveType.WAIT:
			self.update()
			return

		if move == MoveType.ABORT:
			return

		res = ResultType.OK

		old = mvc.m.robot
		old_x, old_y = tup(old)

		new = None
		rock = None

		if move == MoveType.UP:
			new = num(old_x, old_y + 1)
		elif move == MoveType.DOWN:
			new = num(old_x, old_y - 1)
		elif move == MoveType.LEFT:
			new = num(old_x - 1, old_y)
			rock = num(old_x - 2, old_y)
		elif move == MoveType.RIGHT:
			new = num(old_x + 1, old_y)
			rock = num(old_x + 2, old_y)

		move_mode = is_move_possible(move, old, new, rock);
		if move_mode == 1:
			e = MoveEvent(old, new, rock)
			e.apply()
		elif move_mode == 0:
			e = MoveEvent(old, new, None)
			e.apply()
		else:
			res = ResultType.CANNOT_MOVE

		self.update()
		is_dead = self.check_if_dead()
		if is_dead:
			res = ResultType.DEAD

		return res

class Model():
	def __init__(self):
		self.robot = num(0,0)
		self.lambdas = set()
		self.unstable_rocks = set()
		self.lift = num(0,0)
		self.lift_open = False

		self.updates = defaultdict(set)

		for y in range(h()):
			for x in range(w()):
				n = num(x,y)
				e = mvc.v.get(n)
				if e == TileType.ROBOT:
					self.add_robot(n)
				elif e == TileType.ROCK:
					self.add_rock(n)
				elif e == TileType.CLL:
					self.add_closed_lift(n)
				elif e == TileType.LAMBDA:
					self.add_lambda(n)
				elif e == TileType.OLL:
					self.add_open_lift(n)

	def add_robot(self, n):
		self.robot = n

	def move_robot(self, old, new):
		self.robot = new

	def add_lambda(self, n):
		self.lambdas.add(n)

	def add_rock(self, n):
		self.unstable_rocks.add(n)
		self.add_deps(n)

	def remove_rock(self, n):
		if n in self.unstable_rocks: self.unstable_rocks.remove(n)
		self.remove_deps(n)

	def move_rock(self, old, new):
		self.remove_rock(old)
		self.add_rock(new)

	def add_deps(self, n):
		deps = self.get_deps(n)
		for d in deps:
			self.updates[d].add(n)

	def remove_deps(self, n):
		deps = self.get_deps(n)
		for d in deps:
			if n in self.updates[d]: self.updates[d].remove(n)

	def touch(self, n):
		self.unstable_rocks = self.unstable_rocks.union(self.updates[n])

	def get_deps(self, n):
		x, y = tup(n)
		deps = []
		y_b = y - 1
		x_l = x - 1
		x_r = x + 1
		if y_b < 0:
			deps.append(-1)
		else:
			deps.append(num(x, y_b))
			if x_l > -1:
				deps.append(num(x_l, y_b))
				deps.append(num(x_l, y))
			if x_r < w():
				deps.append(num(x_r, y_b))
				deps.append(num(x_r, y))
		return sorted(deps)

	def add_open_lift(self, n):
		self.lift = n
		self.lift_open = True

	def add_closed_lift(self, n):
		self.lift = n
		self.lift_open = False

	def __str__(self):
		res = "Size: (" + str(converter.width) + "," + str(converter.height) + ")\n\n"
		res = res + "R: " + str(tup(self.robot)) + "\n\n"
		res = res + ("O: " if self.lift_open else "C: ") + str(self.lift) + "\n\n"
		res = res + "L: " + str([tup(e) for e in self.lambdas]) + "\n\n"
		res = res + "UR: " + str([tup(e) for e in self.unstable_rocks]) + "\n\n"
		res = res + "DD: " + str([str(tup(k)) + "->" + str([tup(e) for e in v]) for k, v in self.updates.items()])
		return res



class View():
	def __init__(self, width, height, raw_map):
		global converter
		converter = Converter(width, height)

		self.width = width
		self.height = height

		parsed_map = np.empty(width * height, dtype=int)
		for y in range(height):
			l = raw_map[y]
			for x in range(width):
				e = l[x]
				n = num(x,y)
				if e == "R":    parsed_map[n] = TileType.ROBOT
				elif e == "*":  parsed_map[n] = TileType.ROCK
				elif e == "L":  parsed_map[n] = TileType.CLL
				elif e == ".":  parsed_map[n] = TileType.EARTH
				elif e == "#":  parsed_map[n] = TileType.WALL
				elif e == "\\": parsed_map[n] = TileType.LAMBDA
				elif e == "O":  parsed_map[n] = TileType.OLL
				elif e == " ":  parsed_map[n] = TileType.EMPTY
				else:           raise ex.BotException("Unknown symbol <" + e + "> in map")

		self.map = parsed_map

	def get(self,n):
		return self.map[n]

	def set(self,n,t):
		self.map[n] = t

	def get_all(self,l):
		return [self.map[n] for n in l]

	def __str__(self):
		res = ""
		for y in range(self.height-1,-1,-1):
			for x in range(self.width):
				n = num(x,y)
				res = res + chr(self.map[n])
			res = res + "\n"
		return res



class MapReader():
	def __init__(self, input, output):
		map_lines = input.readlines()

		map_lines = [s.strip() for s in map_lines]
		width = max([len(s) for s in map_lines])
		height = len(map_lines)
		map_lines = [s.ljust(width) for s in map_lines]

		self.width = width
		self.height = height
		self.raw_map = map_lines

	def get_view(self):
		return View(self.width, self.height, list(reversed(self.raw_map)))
