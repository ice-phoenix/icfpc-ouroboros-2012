#!/usr/bin/env python2

import heapq

from map import MoveType as MT
from map import TileType as TT

from map import w, h, num, tup  # don't initialize your own converter instance!!!


# bot with aqua phobia
class BotState():
    OBLIVIOUS = 0
    SWIMMING = 1


class Swimmer():
    def __init__(self, m, v):
        self.m = m
        self.v = v
        self.state = BotState.OBLIVIOUS
        self.path = list()

    # gets the next bot move
    def next_move(self):

        (rx, ry) = tup(self.m.robot)

        # if path is empty, go to oblivious state
        if not self.path:
            self.state = BotState.OBLIVIOUS

        if self.m.water >= ry:
            if self.m.wetness == self.m.waterproof:  # abort before death
                return MT.ABORT

            elif self.state != BotState.SWIMMING:
                self.state = BotState.SWIMMING
                self.find_escape_path()
                if not self.path:  # abort if found nothing
                    return MT.ABORT
                else:
                    self.path.reverse()  # reverse path because it's faster to pop list
                    self.path.pop()
                return self.to_move(self.path.pop())

            elif self.state == BotState.SWIMMING:
                return self.to_move(self.path.pop())

        else:
            return MT.WAIT

    # converts adjacent tile to a move command
    def to_move(self, tile):
        (tx, ty) = tup(tile)
        (x, y) = tup(self.m.robot)

        if tx < x:
            return MT.LEFT
        if tx > x:
            return MT.RIGHT
        if ty < y:
            return MT.DOWN
        if ty > y:
            return MT.UP

    # finds the best escape path out of water
    def find_escape_path(self):
        best_path = list()

        for surface in self.above_water():
            p = self.dijkstra(self.m.robot, surface)
            if p and len(p) < len(best_path) or not best_path:
                best_path = p

        self.path = best_path

    # gets all tiles just above water
    def above_water(self):
        above = set()
        y = self.m.water + 1
        
        if y >= h():
            return above

        for x in range(w()):
            t = num(x, y)
            if self.walkable(t):
                above.add(t)
        return above

    # finds shortest path to get to the surface
    # plagiarized from http://code.activestate.com/recipes/119466/
    def dijkstra(self, start, end):
        q = [(0, start, ())]  # a heap of (cost, path_head, path_rest)
        visited = set()       # visited tiles
        while True:
            (cost, tile, path) = heapq.heappop(q)
            if tile not in visited:
                visited.add(tile)
                if tile == end:
                    return list(self.flatten(path))[::-1] + [tile]
                path = (tile, path)
                for (tile2, cost2) in self.get_adjacent_tiles_cost(tile):
                    if tile2 not in visited:
                        heapq.heappush(q, (cost + cost2, tile2, path))

    # flattens linked list of form [0,[1,[2,[...]]]]
    @staticmethod
    def flatten(l):
        while len(l) > 0:
            yield l[0]
            l = l[1]

    # gets adjacent tiles with water-avoidance costs
    def get_adjacent_tiles_cost(self, tile):
        adj_set = set()

        # above
        if self.walkable(tile - w()):
            adj_set.add((tile - w(), 1))  # want to go up
        # below
        if self.walkable(tile + w()):
            adj_set.add((tile + w(), 4))  # don't want to go under
        # left
        if self.walkable(tile - 1):
            adj_set.add((tile - 1, 2))    # don't care about side steps
        # right
        if self.walkable(tile + 1):
            adj_set.add((tile + 1, 2))    # don't care about side steps

        return adj_set

    # checks if tile is walkable
    def walkable(self, tile):
        (x, y) = tup(tile)
        tile_type = self.v.get(tile)
        return 0 <= x < w() and \
            0 <= y < h() and \
            tile_type != TT.WALL and \
            tile_type != TT.ROCK and \
            tile_type != TT.CLL
