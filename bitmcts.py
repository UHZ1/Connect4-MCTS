from bitboard import bitboard
from numpy import array, copy, sqrt, log, random
from time import time, perf_counter

s2 = sqrt(2)

class Node:
  __slots__ = ('root', 'board', 'children', 'move', 'wins', 'visits', 'uct')

  def __init__(self, root, board, move):
    self.root = root
    self.board = board
    self.children = None   # turn to numpy
    self.move = move
    self.wins = 0
    self.visits = 0
    self.uct = 0.0

def make_copy(board):
  b = bitboard()
  b.heights = copy(board.heights)
  b.boards = copy(board.boards)
  b.player = board.player
  b.winner = board.winner
  return b

def make_child(root, move):
  b = make_copy(root.board)
  b.move(move)
  return Node(root, b, move)

def calc_uct(leaf):
  return leaf.wins/leaf.visits + s2 * my_log(sqrt(leaf.root.visits)/leaf.visits)

def my_log(x):
  if x == 0:
    return float('inf')
  return log(x)

def run(board):

  root = Node(None, board, None)
  root.visits += 1

  selection_time = 0
  expansion_time = 0
  simulation_time = 0
  backprop_time = 0

  iter = 0
  sstart = time()

  while True:

    if time() - sstart >= 3:
      print(f"Iterations in 3 seconds: {iter}")
      print(f"Selection time: {selection_time:.6f} Expansion time: {expansion_time:.6f}")
      print(f"Simulation time: {simulation_time:.6f} Backprop time: {backprop_time:.6f}")
      break
    iter += 1

    # selection
    start = perf_counter()
    node = root
    while node.children:
      if None in {x.uct:0 for x in node.children} or iter % 68 == 0:
        node = random.choice(node.children)
      else:
        node = max(node.children, key=lambda x: x.uct)
    end = perf_counter()
    selection_time += (end - start)

    # expansion
    start = perf_counter()
    leaf = node
    if node.board.is_terminal() == -2:
      node.children = []
      for move in node.board.gen_legal_moves():
        node.children.append(make_child(node, move))
        if node.children[-1].board.is_terminal() >= 0:
          leaf = node.children[-1]
          leaf.wins += float('inf')
        elif node.children[-1].board.swap_is_terminal(move) >= 0:
          leaf = node.children[-1]
          leaf.wins += float('inf')
        else:
          leaf = random.choice(node.children)

    end = perf_counter()
    expansion_time += (end - start)

    # simulation
    start = perf_counter()
    score = 0
    for _ in range(25):
      b = make_copy(leaf.board)
      while b.is_terminal() == -2:
        b.move(b.get_move())
      if b.winner == (leaf.board.player ^ 1):
        score += 1
      elif b.winner == -1:
        score += 0
      else:
        score -= 1
    end = perf_counter()
    simulation_time += (end - start)

    start = perf_counter()
    while leaf.root:
      leaf.wins += score
      score *= -1
      leaf.visits += 1
      leaf.uct = calc_uct(leaf)
      leaf = leaf.root
    end = perf_counter()
    backprop_time += (end - start)

  return max(root.children, key=lambda x: x.visits).move
