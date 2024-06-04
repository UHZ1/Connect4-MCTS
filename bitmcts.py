from copy import deepcopy
from numpy import empty, log, sqrt
from random import randint

EXPL = 0.58578643762690485
COLS = 7
ROWS = 6

class Node:
  def __init__(self, rt, brd, mv=None):
    self.root = rt
    self.board = deepcopy(brd)
    self.target_size, self.untried_moves = brd.legal_moves()
    self.untried_size = self.target_size
    self.children = empty(self.target_size, dtype=object)
    self.children_size = 0
    self.turn = brd.player
    self.simulated_move = mv
    self.state = None
    # not root check
    if mv != None:
      self.board.move(mv)
      if self.board.is_terminal() != -2:
        # 0/1 winner, -1 tie, not possible to lose
        self.state = 1 if self.board.winner != -1 else -1
    self.score = 0
    self.visits = 0
    self.uct = -float("inf")
    # shuffle untried moves
    for i in range(self.untried_size-1, 0, -1):
      x = randint(0, i)
      mask_x = self.untried_moves & (127 << x * COLS)
      mask_i = self.untried_moves & (127 << i * COLS)
      diff = abs(x * COLS - i * COLS)
      g, l = max(mask_x, mask_i), min(mask_x, mask_i)
      self.untried_moves ^= mask_x | mask_i
      self.untried_moves |= ((g >> diff) | (l << diff))

def select_best_child(node, f):
  val = -float("inf")
  ntr = None
  for i in range(node.children_size):
    if f(node.children[i]) > val:
      ntr = node.children[i]
      val = f(ntr)
  assert(ntr)
  return ntr

def select_with_uct(node):
  while node.target_size and node.target_size == node.children_size:
    node = select_best_child(node, lambda x: x.uct)
  return node

def add_to_game_tree(node):
  mv = ((node.untried_moves & (127 << (node.untried_size-1) * COLS)) >> (node.untried_size-1) * COLS) - 1
  nn = Node(node, node.board, mv)
  node.children[node.children_size] = nn
  node.children_size += 1
  node.untried_size -= 1
  return nn

def simulate_game(node, iter):
  res = 0
  cp = deepcopy(node.board)
  for _ in range(iter):
    while cp.is_terminal() == -2:
      mv = cp.get_move()
      cp.move(mv)
    res += 1 if cp.winner == node.turn else (0 if cp.winner == -1 else -1)
  return res

def update_path(node, res):
  while node:
    node.visits += 1
    node.score += res
    res *= -1
    if node.root:
      node.uct = node.score / node.visits + 0.58578643762690485 * sqrt(log(node.root.visits) / node.visits)
    node = node.root

def task(state, iter, simIter):
  root = Node(None, state, None)
  root.visits = 1
  for _ in range(iter):
    node = select_with_uct(root)
    if node.state != None:
      update_path(node, node.state * 1000)
    else:
      node = add_to_game_tree(node)
      res = simulate_game(node, simIter)
      update_path(node, res)
  return select_best_child(root, lambda x: x.visits).simulated_move

def run(state, iter, simIter):
  pass
