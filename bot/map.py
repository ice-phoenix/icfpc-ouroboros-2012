#!/usr/bin/env python2

from collections import defaultdict

import ex
import numpy as np

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
    TRAMP_A = ord('A')
    TRAMP_B = ord('B')
    TRAMP_C = ord('C')
    TRAMP_D = ord('D')
    TRAMP_E = ord('E')
    TRAMP_F = ord('F')
    TRAMP_G = ord('G')
    TRAMP_H = ord('H')
    TRAMP_I = ord('I')
    TARG_1 = ord('1')
    TARG_2 = ord('2')
    TARG_3 = ord('3')
    TARG_4 = ord('4')
    TARG_5 = ord('5')
    TARG_6 = ord('6')
    TARG_7 = ord('7')
    TARG_8 = ord('8')
    TARG_9 = ord('9')

def to_tramp(e):
    if e == "A":    return TileType.TRAMP_A
    elif e == "B":  return TileType.TRAMP_B
    elif e == "C":  return TileType.TRAMP_C
    elif e == "D":  return TileType.TRAMP_D
    elif e == "E":  return TileType.TRAMP_E
    elif e == "F":  return TileType.TRAMP_F
    elif e == "G":  return TileType.TRAMP_G
    elif e == "H":  return TileType.TRAMP_H
    elif e == "I":  return TileType.TRAMP_I
    else: return None

def to_targ(e):
    if e == "1":    return TileType.TARG_1
    elif e == "2":  return TileType.TARG_2
    elif e == "3":  return TileType.TARG_3
    elif e == "4":  return TileType.TARG_4
    elif e == "5":  return TileType.TARG_5
    elif e == "6":  return TileType.TARG_6
    elif e == "7":  return TileType.TARG_7
    elif e == "8":  return TileType.TARG_8
    elif e == "9":  return TileType.TARG_9
    else: return None

def is_tramp(t):
    return t == TileType.TRAMP_A or \
           t == TileType.TRAMP_B or \
           t == TileType.TRAMP_C or \
           t == TileType.TRAMP_D or \
           t == TileType.TRAMP_E or \
           t == TileType.TRAMP_F or \
           t == TileType.TRAMP_G or \
           t == TileType.TRAMP_H or \
           t == TileType.TRAMP_I

def is_targ(t):
    return t == TileType.TARG_1 or \
           t == TileType.TARG_2 or \
           t == TileType.TARG_3 or \
           t == TileType.TARG_4 or \
           t == TileType.TARG_5 or \
           t == TileType.TARG_6 or \
           t == TileType.TARG_7 or \
           t == TileType.TARG_8 or \
           t == TileType.TARG_9



class MoveType():
    UP, DOWN, LEFT, RIGHT, WAIT, ABORT = range(6)



class ResultType():
    OK, ABORTED, CANNOT_MOVE, DEAD = range(4)



class MoveEvent():
    def __init__(self, old, new, rock):
        self.old = old
        self.new = new
        self.rock = rock
        self.moved_rock = rock is not None

    def apply(self):
        if self.new in mvc.m.trampolines:
            self.new = mvc.m.trampolines[self.new]
            used_tramps = mvc.m.targets[self.new]
            for t in used_tramps:
                mvc.m.touch(t)
                mvc.v.set(t, TileType.EMPTY)
                mvc.m.trampolines.pop(t)
            mvc.m.targets.pop(self.new)

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
        mvc.m.moved_rocks.add(self.new)



def is_move_possible(dir, old, new, rock):
    old_tile = mvc.v.get(old)
    new_tile = mvc.v.get(new)
    rock_tile = mvc.v.get(rock) if rock is not None else None
    if old_tile == TileType.ROBOT:
        if new_tile == TileType.EMPTY or \
            new_tile == TileType.EARTH or \
            new_tile == TileType.LAMBDA or \
            new_tile == TileType.OLL or \
            is_tramp(new_tile):
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

        events = []

        for rock in current_unstable:
            deps = sorted(mvc.m.get_deps(rock))
            l, b, r, ls, rs = deps
            left, bottom, right, lside, rside = mvc.v.get_all(deps)
            if bottom == TileType.EMPTY:
                e = RockEvent(rock, b)
                events.append(e)
            elif bottom == TileType.ROCK and rside == TileType.EMPTY and right == TileType.EMPTY:
                e = RockEvent(rock, r)
                events.append(e)
            elif bottom == TileType.ROCK and lside == TileType.EMPTY and left == TileType.EMPTY:    
                e = RockEvent(rock, l)
                events.append(e)
            elif bottom == TileType.LAMBDA and rside == TileType.EMPTY and right == TileType.EMPTY:
                e = RockEvent(rock, r)
                events.append(e)

        for e in events: e.apply()

    def check_if_dead(self):
        robot = mvc.m.robot + w()
        for r in mvc.m.moved_rocks:
            if robot == r:
                return True
        if mvc.m.wetness > mvc.m.waterproof:
            return True
        return False

    def process(self, move):
        res = ResultType.OK

        if move == MoveType.WAIT:
            self.update()
            is_dead = self.check_if_dead()
            if is_dead:
                res = ResultType.DEAD
            mvc.m.next_turn()
            return res

        if move == MoveType.ABORT:
            return ResultType.ABORTED

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
        mvc.m.next_turn()
        return res

class Model():
    def __init__(self, raw_footer):
        self.robot = num(0,0)
        self.active_lambdas = set()
        self.picked_lambdas = set()
        self.unstable_rocks = set()
        self.moved_rocks = set()
        self.lift = num(0,0)
        self.lift_open = False

        self.updates = defaultdict(set)

        self.turn = 0

        tramps = {}
        targs = {}

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
                elif is_tramp(e):
                    tramps[e] = n
                elif is_targ(e):
                    targs[e] = n

        self.waterproof = 10
        self.flooding = 0
        self.water = 0

        self.trampolines = {}
        self.targets = defaultdict(set)

        footer = {}
        for l in raw_footer:
            l = l.split(" ")
            if l[0] == "Waterproof":
                self.waterproof = int(l[1])
            elif l[0] == "Flooding":
                self.flooding = int(l[1])
            elif l[0] == "Water":
                self.water = int(l[1])
            elif l[0] == "Trampoline":
                tramp = tramps[to_tramp(str(l[1]))]
                targ = targs[to_targ(str(int(l[3])))]
                self.trampolines[tramp] = targ
                self.targets[targ].add(tramp)

        self.water = self.water - 1

        self.wetness = 0

    def update_flood(self):
        if self.flooding == 0:
            return

        x, y = tup(self.robot)
        if y <= self.water:
            self.wetness = self.wetness + 1
        else:
            self.wetness = 0

        if self.turn % self.flooding == 0:
            self.water = self.water + 1

    def check_is_done(self):
        if len(self.active_lambdas) == 0:
            self.add_open_lift(self.lift)
            mvc.v.set(self.lift, TileType.OLL)

    def has_reached_lift(self):
        return True if len(self.active_lambdas) == 0 and \
                    self.robot == self.lift \
            else False

    def next_turn(self):
        self.turn = self.turn + 1
        self.moved_rocks = set()
        self.update_flood()
        self.check_is_done()

    def current_score(self):
        return 0 - self.turn + 25 * len(self.picked_lambdas)

    def score_on_abort(self):
        return 0 - self.turn + 50 * len(self.picked_lambdas)

    def score_on_lift(self):
        return 0 - self.turn + 75 * len(self.picked_lambdas)

    def add_robot(self, n):
        self.robot = n

    def move_robot(self, old, new):
        self.robot = new
        new_tile = mvc.v.get(new)
        if new_tile == TileType.LAMBDA:
            self.pick_lambda(new)

    def add_lambda(self, n):
        self.active_lambdas.add(n)

    def pick_lambda(self, n):
        if n in self.active_lambdas: self.active_lambdas.remove(n)
        self.picked_lambdas.add(n)

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
        res = res + "AL: " + str([tup(e) for e in self.active_lambdas]) + "\n\n"
        res = res + "PL: " + str([tup(e) for e in self.picked_lambdas]) + "\n\n"
        res = res + "UR: " + str([tup(e) for e in self.unstable_rocks]) + "\n\n"
        res = res + "DD: " + str([str(tup(k)) + "->" + str([tup(e) for e in v]) for k, v in self.updates.items()]) + "\n\n"
        res = res + "TR: " + str([str(tup(k)) + "->" + str(tup(v)) for k, v in self.trampolines.items()]) + "\n\n"
        res = res + "TA: " + str([str(tup(k)) + "->" + str([tup(e) for e in v]) for k, v in self.targets.items()]) + "\n\n"
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
                elif to_tramp(e) is not None: 
                    parsed_map[n] = to_tramp(e)
                elif to_targ(e) is not None:
                    parsed_map[n] = to_targ(e)
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
            if y == (mvc.m.water if mvc.m is not None else -1):
                res = res + "*\n"
            else:
                res = res + "\n"
        return res



class MapReader():
    def __init__(self, input, output):
        lines = input.readlines()

        map_lines = []
        footer = []
        is_footer = False
        for l in lines:
            if l != "\n":
                if not is_footer: map_lines.append(l)
                else: footer.append(l)
            else: is_footer = True

        map_lines = [s.strip() for s in map_lines]
        width = max([len(s) for s in map_lines])
        height = len(map_lines)
        map_lines = [s.ljust(width) for s in map_lines]

        self.width = width
        self.height = height
        self.raw_map = map_lines
        self.raw_footer = footer

    def get_view(self):
        return View(self.width, self.height, list(reversed(self.raw_map)))
