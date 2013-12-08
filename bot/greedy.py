#!/usr/bin/env python2

import sys

from map import MoveType as MT
from map import TileType as TT

from map import w, h, num, tup  # don't initialize your own converter instance!!!


# always try to move to one of four adjacent squares and not to wait
class Greedy():
    def __init__(self, m, v):
        self.m = m
        self.v = v

    def next_move(self):

        adj_tiles = self.get_adjacent_tiles()
        lambdas = self.get_all_lambdas()
       
        best_dist = sys.maxint
        best_tile = None

        for (direction, tx, ty) in adj_tiles:
            dist = 0
            # use sum of dist to all lambdas as a heuristic for how bad this position is
            for (lx, ly) in lambdas:
                dist += self.get_manh_dist((tx, ty), (lx, ly))
            if dist < best_dist:
                best_dist = dist
                best_tile = (direction, tx, ty)
        
        assert best_tile is not None, "GreedyBot doesn't know where to go!"

        (direction, tx, ty) = best_tile
        
        return direction

    # returns a set of tuples: (direction, tile x, tile y)
    def get_adjacent_tiles(self):    
        (rx, ry) = tup(self.m.robot)
        
        adj_set = set()

        if self.walkable(rx-1, ry):           # left
            adj_set.add((MT.LEFT,  rx-1, ry))
        if self.walkable(rx+1, ry):           # right
            adj_set.add((MT.RIGHT, rx+1, ry))
        if self.walkable(rx, ry-1):           # down
            adj_set.add((MT.DOWN,  rx, ry-1))
        if self.walkable(rx, ry+1):           # up
            adj_set.add((MT.UP,    rx, ry+1))

        return adj_set

    # checks if tile is walkable
    def walkable(self, x, y):
        tile = self.v.get(num(x, y))
        return 0 <= x < w() and \
            0 <= y < h() and \
            tile != TT.WALL and \
            tile != TT.ROCK and \
            tile != TT.CLL

    # gets all active lambdas
    def get_all_lambdas(self):
        list_lambdas = set()
        for i in range(h() * w()):
            if self.v.get(i) == TT.LAMBDA:
                list_lambdas.add(tup(i))
        return list_lambdas

    @staticmethod
    def get_manh_dist((x1, y1), (x2, y2)):
        return abs(x1-x2) + abs(y1-y2)
