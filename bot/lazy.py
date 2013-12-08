#!/usr/bin/env python2

from map import MoveType as MT


# always wait
class Lazy():
    def __init__(self, m, v):
        pass

    @staticmethod
    def next_move():
        return MT.WAIT
