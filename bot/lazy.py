from map import MoveType as MT

# always wait

class Lazy():
    def __init__(self):
        pass

    def next_move(self, m, v):
        return MT.WAIT
