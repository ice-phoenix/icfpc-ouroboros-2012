import heapq

from map import MoveType as MT
from map import w, h, num, tup    #don't initialize your own instance of converter!
from map import TileType

# bot with aquaphobia

class BotState():
    OBLIVIOUS = 0
    SWIMMING  = 1

class Swimmer():

    def __init__(self):
        self.state = BotState.OBLIVIOUS
        self.path  = list()
        pass

    def next_move(self, m, v):
        self.m = m
        self.v = v

        (rx, ry) = tup(self.m.robot)

        if not self.path:  # if path is empty, reset to oblivious state
            self.state = BotState.OBLIVIOUS

        if self.m.water >= ry:
            if self.m.wetness == self.m.waterproof:
                return MT.ABORT                     # abort before death
            elif self.state != BotState.SWIMMING:
                self.find_escape_path()

                if not self.path:                   # abort if found nothing
                    return MT.ABORT
                else:
                    self.path.reverse()             # reverse because it's faster to pop list
                    self.path.pop()
                self.state = BotState.SWIMMING
                return self.to_move(self.path.pop())
            elif self.state == BotState.SWIMMING:
                return self.to_move(self.path.pop())
        else:
            return MT.WAIT

    # convert adjacent tile to movement command
    def to_move(self, tile):
        
        (tx, ty) = tup(tile)
        ( x,  y) = tup(self.m.robot)

        if tx < x:
            return MT.LEFT
        if tx > x:
            return MT.RIGHT
        if ty < y:
            return MT.DOWN
        if ty > y:
            return MT.UP

    def find_escape_path(self):
        best_path = list()

        for surface in self.above_water():
            p = self.dijkstra(self.m.robot, surface)
            if p and len(p) < len(best_path) or not(best_path):
                best_path = p

        self.path = best_path

    # get all tiles above water
    def above_water(self):
        above = set()
        y = self.m.water + 1
        
        if y >= h():
            return None

        for x in range(w()):
            t = num(x, y)
            if self.walkable(t):
                above.add(t)
        return above

    # find shortest path to get to surface
    # plagiarized from http://code.activestate.com/recipes/119466/
    def dijkstra(self, start, end):
       q = [(0, start, ())]  # Heap of (cost, path_head, path_rest).
       visited = set()       # Visited tiles.
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

    def flatten(self, L):       # Flatten linked list of form [0,[1,[2,[]]]]
       while len(L) > 0:
          yield L[0]
          L = L[1]

    def get_adjacent_tiles_cost(self, tile):

       adj_set = set()

       # above
       if self.walkable(tile - w()):
           adj_set.add((tile - w(), 1))

       # below
       if self.walkable(tile + w()):
           adj_set.add((tile + w(), 4))

       # left
       if self.walkable(tile - 1):
           adj_set.add((tile - 1, 2))

       # right
       if self.walkable(tile + 1):
           adj_set.add((tile + 1, 2))

       return adj_set

    def walkable(self, tile):
        (x, y) = tup(tile)
        return True if x < w() and x >= 0 and y < h() and y >= 0 and\
                       self.v.get(num(x, y)) != TileType.WALL    and\
                       self.v.get(num(x, y)) != TileType.ROCK    and\
                       self.v.get(num(x, y)) != TileType.CLL        \
                    else False
