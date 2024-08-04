from numpy import zeros, array
from random import randint

ROWS = 6
COLS = 7

"""
 +---------------------+
 | 6 13 20 27 34 41 48 |
 | 5 12 19 26 33 40 47 |
 | 4 11 18 25 32 39 46 |
 | 3 10 17 24 31 38 45 |
 | 2  9 16 23 30 37 44 |
 | 1  8 15 22 29 36 43 |
 | 0  7 14 21 28 35 42 |
 +---------------------+
1  -> Player 1 Won
0  -> Player 0 Won
-1 -> Tie
-2 -> Game hasn't ended
"""

class bitboard:
  def __init__(self):
    self.heights = array([0,  7, 14, 21, 28, 35, 42])
    self.boards = zeros(2, dtype=int)
    self.player = 0
    self.winner = -2

  def move(self, col):
    pos = 1 << self.heights[col]
    self.boards[self.player] |= pos
    self.heights[col] += 1
    self.player ^= 1

  def undo_move(self, col):
    self.player ^= 1
    self.heights[col] -= 1
    pos = 1 << self.heights[col]
    self.boards[self.player] ^= pos

  def legal_moves(self):
    brd = self.boards[0] | self.boards[1]
    moves = size = 0
    for i in range(5, 49, COLS):
      if not (1 << i) & brd:
        moves |= (i // COLS) << size * 3
        size += 1
    return moves, size

  def is_legal_move(self, mv):
    return not ((1 << mv * 7 + 5) & (self.boards[0] | self.boards[1]))

  def gen_legal_moves(self):
    brd = self.boards[0] | self.boards[1]
    for i in range(5, 49, COLS):
      if not (1 << i) & brd:
        move = i // COLS
        yield move

  def get_move(self):
    moves, size = self.legal_moves()
    x = randint(0, size - 1)
    return (moves >> 3 * x) & 7

  def is_terminal(self):
    brd = self.boards[self.player ^ 1]
    self.winner = self.player ^ 1
    # vertical
    if brd & (brd >> 1) & (brd >> 2) & (brd >> 3):
      return self.player ^ 1
    # diagonal left
    if brd & (brd >> 6) & (brd >> 12) & (brd >> 18):
      return self.player ^ 1
    # horizontal
    if brd & (brd >> 7) & (brd >> 14) & (brd >> 21):
      return self.player ^ 1
    # diagonal right
    if brd & (brd >> 8) & (brd >> 16) & (brd >> 24):
      return self.player ^ 1
    # draw
    if (self.boards[0] | self.boards[1]) & 141845657554976 == 141845657554976:
      self.winner = -1
      return -1;
    self.winner = -2
    return -2

  def swap_is_terminal(self, col):
    self.undo_move(col)
    self.player ^= 1
    self.move(col)
    res = self.is_terminal()
    self.undo_move(col)
    self.player ^= 1
    self.move(col)
    return res

  def print(self):
    for i in range(ROWS-1, -1, -1):
      for j in range(i, i + 49, COLS):
        mask = 1 << j
        if self.boards[0] & mask:
          print("0", end=' ')
        elif self.boards[1] & mask:
          print("1", end=' ')
        else:
          print(".", end=' ')
      print()

