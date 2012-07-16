import sys
from map import Controller as C
from map import MapReader as MR
from map import MoveType as MT
from map import w, h, num, tup    #don't initialize your own instance of converter!
from map import TileType
from map import MoveType as MT

# Always try to move one of four adjacent squares and never wait. 

class Greedy():
    def __init__(self):
        pass

    def next_move(self, m, v):
        
        self.m = m
        self.v = v

        adj_tiles = self.get_adjacent_tiles()
        lambdas = self.get_all_lambdas()
       
        best_dist = sys.maxint + 1
        best_tile = None

        for (tx, ty) in adj_tiles:
            dist = 0
            for (lx, ly) in lambdas:
                dist += self.get_man_dist((tx, ty), (lx, ly)) # use sum dist to all lambdas as heuristic for how bad this position is
            if dist < best_dist:
                best_dist = dist
                best_tile = (tx, ty)
        
        assert best_tile != None, 'GreedyBot doesn\'t know where to go!'

        (rx, ry) = tup(self.m.robot)
        (tx, ty) = best_tile

        if rx > tx:
            return MT.LEFT
        
        if rx < tx:
            return MT.RIGHT

        if ry > ty:
            return MT.DOWN

        if ry < ty:
            return MT.UP

    def get_adjacent_tiles(self):
        (rx, ry) = tup(self.m.robot)
        
        list_pos = set()
        if self.walkable(rx-1, ry): #left
            list_pos.add((rx-1, ry))
        if self.walkable(rx+1, ry): #right
            list_pos.add((rx+1, ry)) 
        if self.walkable(rx, ry-1): #down
            list_pos.add((rx, ry-1))
        if self.walkable(rx, ry+1): #up
            list_pos.add((rx, ry+1)) 

        return list_pos

    def walkable(self, x, y):
        return True if x < w() and x >= 0 and y < h() and y >= 0 and\
                       self.v.get(num(x, y)) != TileType.WALL    and\
                       self.v.get(num(x, y)) != TileType.ROCK    and\
                       self.v.get(num(x, y)) != TileType.CLL        \
                    else False

    def get_all_lambdas(self):
        list_lambdas = set()
        for i in range(h() * w()):
           if self.v.get(i) == TileType.LAMBDA:
               list_lambdas.add(tup(i))
        return list_lambdas
           
    def get_man_dist(self, (x1, y1), (x2, y2)):
        return abs(x1-x2) + abs(y1-y2)
