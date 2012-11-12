#!/usr/bin/env python2

from map import MoveType as MT

# always abort

class Quitter():
    def __init__(self):
        pass

    def next_move(self, m, v):
        return MT.ABORT
