#!/usr/bin/env python2

from map import MoveType as MT


# always abort
class Quitter():
    def __init__(self, m, v):
        pass

    @staticmethod
    def next_move():
        return MT.ABORT
