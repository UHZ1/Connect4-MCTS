import random
import copy

ROWS = 6
COLS = 7
BSIZE = 42

class Board:
  def __init__(self, t):
    self.mostRecentPos = -100000
    self.pieces = 0
    self.cur_pl = t + 1
    self.turn = t
    self.b = [0 for _ in range(BSIZE)]
    self.winner = 0

  def print(self):
    s = ''
    for i in range(BSIZE):
      s += str(int(self.b[i])) + ' '
      if (i + 1) % COLS == 0:
        s += '\n'
    print(s)

  def updateTurn(self, mrp):
    self.turn = not self.turn
    self.cur_pl = self.turn + 1
    self.pieces += 1
    self.mostRecentPos = mrp

  def getLegalMoves(self):
    return [i for i in range(COLS) if not self.b[i]]

  def isLegalMove(self, where):
    return not self.b[where % COLS]

  def getLegalMove(self):
    moves = self.getLegalMoves()
    assert(len(moves))
    move = random.randint(0, len(moves) - 1)
    return moves[move]

  # may go wrong
  def dropPiece(self, where):
    while self.b[where + 35]:
      where -= COLS
      assert(where + 35 >= 0)
    self.b[where + 35] = self.cur_pl
    self.updateTurn(where + 35)

  def checkDraw(self):
    self.winner = 0
    return self.pieces == BSIZE

  def _validMove(self, dx, dy):
    move = (self.mostRecentPos // COLS + dx) * COLS + ((self.mostRecentPos % COLS) + dy)
    if move < 0 or move >= BSIZE:
      return False
    cond = self.b[move] == self.b[self.mostRecentPos]
    cond2 = None

    if dx and dy:
      cond2 = move // COLS - dx == self.mostRecentPos // COLS and (move % COLS) - dy == self.mostRecentPos % COLS
    elif not dx and dy:
      cond2 = move // COLS == self.mostRecentPos // COLS
    else:
      cond2 = move % COLS == self.mostRecentPos % COLS

    return cond and cond2

  def _pythonLambdasAreAnnoying(self, total, dx, dy):
    cnt, ndx, ndy, = 1, dx, dy
    while cnt < 4 and self._validMove(ndx, ndy):
      total += 1
      cnt += 1
      ndx += dx
      ndy += dy
    return total

  def _checkConsecutive(self, dx, dy):
    total = self._pythonLambdasAreAnnoying(1, dx, dy)
    if total > 3:
      return True
    total = self._pythonLambdasAreAnnoying(total, -dx, -dy)
    return total > 3

  # faster straight line checks
  def checkWin(self):
    self.winner = (not self.turn) + 1
    return self._checkConsecutive(0, 1) or self._checkConsecutive(1, 0) or self._checkConsecutive(1, 1) or self._checkConsecutive(-1, 1)

  # faster diagonal checks
  def _checkWin(self):
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    for dx, dy in directions:
      score = 0
      for dir in [1, -1]:
        for dist in range(1, 4):
          x, y = self.mostRecentPos // COLS, self.mostRecentPos % COLS
          nx, ny = x + dx * dir * dist, y + dy * dir * dist
          if 0 <= nx < ROWS and 0 <= ny < COLS and self.b[nx * COLS + ny] == self.b[self.mostRecentPos]:
            score += 1
          else:
            break
      if score >= 3:
        self.winner = (not self.turn) + 1
        return True
    return False

  def game(self):
    while not self._checkWin() and not self.checkDraw():
      move = int(input("Mover player " + str(self.cur_pl) + ": "))
      self.dropPiece(move)
      self.print()
    print("Winner " + str(self.winner))

  def sim(self):
    cp = copy.deepcopy(self)
    while not cp.checkWin() and not cp.checkDraw():
      move = cp.getLegalMove()
      cp.dropPiece(move)
    return cp.winner
