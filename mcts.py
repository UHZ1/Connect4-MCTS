from copy import deepcopy
from numpy import sqrt, log
import random

EXPL = 0.58578643762690485
COLS = 7

class Node:
  def __init__(self, rt, brd, mv=None):
    # keep track of the parent node
    self.root = rt

    # store all the possible legal moves from the current Board state
    self.children = []

    # the current connect 4 game board for this node
    self.board = deepcopy(brd)

    # which move has been added to this node's parent board state to get this node's board state
    self.simulatedMove = mv

    # the board state can either be a Win, Loss, Tie, or None (means keep playing to reach a state)
    self.state = None
    # some constructor stuff, don't want to drop a piece when the Root of the MCTS simulation is created
    if mv != None:
      self.board.dropPiece(mv)
      # check if the current Board state is a Win/Loss/Draw and update accordingly
      if self.board.checkWin() or self.board.checkDraw():
        # explanation in simulateGame() function
        self.state = 1 if ((not self.board.turn)+1) == self.board.winner else (0 if not self.board.winner else -1)

    # all the legal untried Moves we will randomly select to populate self.children with
    # this way we can keep track of them for simplicities sake
    self.untriedMoves = self.board.getLegalMoves()
    # randomize the moves
    random.shuffle(self.untriedMoves)
    # We want to have easy access to how many children this specific node should have
    # self.untriedMoves and self.children gets modified, so we have this variable to store the initial length of
    # legal Moves for the current board state
    # We don't have to worry about setting this to 0 if self.state != None
    self.targetLength = len(self.untriedMoves)

    # use these 3 variables to calculate the exploration/exploitation formula
    self.score = 0
    self.visits = 0
    self.uct = 0.0

# Helper function to select the best child from self.children based on a value
# Use 'f' as a lambda to select a value from the Node
def selectBestChild(node, f):
  val = -float("inf")
  ntr = None
  for i in range(len(node.children)):
    if f(node.children[i]) > val:
      ntr = node.children[i]
      val = f(ntr)
  assert(ntr) # make sure ntr actually exists and isn't None
  return ntr

# First Step of the MCTS Algorithm
# Our goal is to find a leaf node
# We select the most promising Node based on a Node's UCT score
# -> A leaf node has not been 'fully expanded', meaning its self.children does not contain all of the possible moves from
#    self.untriedMoves
# -> This is where self.targetLength is useful, so we can compare to len(self.children)
# Make sure to also check that node.targetLength is not zero, this means the board is at a terminal state
""" Visual Example with TicTacToe
Consider this Board State
  Board:
        x * *
        * o *
        o x *
  UCT: 32.34
  TerminalState: False
  Turn: o
  targetLength = 5
  untriedMoveIndexes = []
  Children:
    UCT: 21      UCT: 999     UCT: -23     UCT: 12.3    UCT: 43
    x o *        x * o        x * *        x * *        x * *
    * o *        * o *        o o *        * o *        * o o
    o x *        o x *        o x *        o x o        o x *

Notice that the Root Node is fully expanded because all of its children represent all the possible legal moves from
its board state.
After the selectWithUCT() call, the function will select and return the 2nd node with UCT: 999
"""
def selectWithUCT(node):
  # while the node is fully expanded
  while node.targetLength and node.targetLength == len(node.children):
    # select the node's most promising child accoding to its UCT score
    node = selectBestChild(node, lambda x: x.uct)
  # return the leaf node
  return node

# Second Step
# Here our Goal is to expand the selected node by making a move from self.untriedMoves to self.board
# One random move from self.untriedMoves is removed and placed on self.board
""" Visual Example with TicTacToe

Note: Handling terminal nodes is explain at the very end

Consider this Board State which we will expand
  TerminalState: False
  Turn: o
  untriedMoveIndexes = [8, 1, 5, 2, 3]
          o * *
          * x *
          o x *
        /
       /
      /
TerminalState: True (o has won the board)     This is the node we get as a result of the addToGameTree() function
Turn: x
untriedMoves = [5, 2, 8, 1]
    o * *
    o x *
    o x *
"""
def addToGameTree(node):
  # constructor handles all the work
  nn = Node(node, node.board, node.untriedMoves.pop())
  # add the new node to the children of the node passed in
  node.children.append(nn)
  # return the new node
  return nn

# Third Step
# Our Goal is to randomly playout the current board state as many times as possible to estimate how good the new move is
# We simulate a game, check if the player who won is the same player as in the Board State who made the move
#   +1 for a win
#   -1 for a loss
#   0 for a draw
# Return the score
def simulateGame(node, iter):
  res = 0
  for _ in range(iter):
    tmp = node.board.sim()
    # This line is specific to my implementation. After each call to Board.dropPiece(), the turn is automatically switched
    # no matter if the move results in a win/loss/tie.
    # Note that Board.sim() returns 1 if Player 1 won, or 2 if Player 2 won, or 0 for a tie.
    # We must check if the (previous turn + 1) from Node.Board is equal to what Board.sim() returns (1 or 2)
    # Because remember, the player turn is switched before we check for a win or draw
    res += 1 if ((not node.board.turn)+1) == tmp else (0 if not tmp else -1) # (Board.turn is a boolean: 0 or 1)
  return res

# Fourth Step
# Our goal is to trace the path we took to get to our current node all the way back up to the Root Node of the
# MCTS function and to update the 3 Variables as we go:
#   -> Node.score:  the TOTAL simulation score of the node (we use += )
#   -> Node.visits: the TOTAL amount of times this node has been picked (we use +=)
#   -> Node.UCT:    the CURRENT UCT score based off of Node.score and Node.visits (we use =)
#     -> the UCT score will change often
def updatePath(node, res):
  while node:
    node.visits += 1
    node.score += res
    # We make sure to multiply the score by -1, becuase a really good move for us is a really bad move for the enemy
    # and vice versa. In the future, we would like to make that move, but our enemy will NOT want to pick its move.
    # !! -> "move" here is talking about Node.simulatedMove
    res *= -1
    if node.root:
      node.uct = node.score / node.visits + EXPL * sqrt(log(node.root.visits) / node.visits)
    node = node.root
# The Final Fifth Step
# Our goal is to run the MCTS simulation x amount of times, then return the most favorable move based on this algorithm
""" How to Handle Terminal Cases

Remember a Terminal Node has ended in either a Tie, Win, or Loss.

Place 1.
- Here we check if the selected Node's state is None.
- Remember in the constructor, we checked if the simulatedMove resulted in a Tie, Win, or Loss. Else, we left it None.
- So if Node.state is not None, we want to call the updatePath function right away. Why?
  -> No point in expanding this node with addToGameTree because the game has already ended. We cannot make anymore moves
  -> No point in simulating this node with simulateGame because we already know the result.
- Then we skip to the next iteration

- Remember why we don't have to worry about setting self.targetMoves to 0 for a terminal state?
- Because setting self.State != None is enough, so addToGameTree will never be evaluated!
"""
def run(state, iter, simIter):
  root = Node(None, state, None)
  root.visits = 1
  for _ in range(iter):
    node = selectWithUCT(root)
    # Place 1
    if node.state != None:
      updatePath(node, node.state * 1000)
      continue
    node = addToGameTree(node)
    res = simulateGame(node, simIter)
    updatePath(node, res)
  # We choose the most promising move based on how many times that Node was visited.
  return selectBestChild(root, lambda x: x.visits).simulatedMove


"""
Techniques to implement:
  - Parallelization: MCTS is inherently parallelizable, meaning it can take advantage of multiple processing cores to perform multiple simulations simultaneously. This can significantly speed up the algorithm. There are several strategies for parallelizing MCTS, including leaf parallelization (running multiple simulations from the same leaf node), root parallelization (running multiple MCTS instances from the root), and tree parallelization (dividing the tree among multiple processors).
  - Early Stopping: In some cases, it may be beneficial to stop the search early if a certain condition is met. For example, if a simulation reaches a state that is known to be a winning state, the algorithm can stop the simulation and backpropagate the result immediately.
  - Move Ordering: Similar to pruning, move ordering involves prioritizing certain actions over others based on some heuristic. The idea is to explore the most promising actions first, which can lead to faster convergence.
  - Rapid Action Value Estimation (RAVE): RAVE is a technique that accelerates the learning of action values by leveraging the results of all simulations passing through a node, not just those that select the action leading to that node. This can lead to faster and more accurate value estimates.
  - Domain Knowledge Injection: If some domain knowledge is available, it can be used to guide the search process. This could be in the form of a heuristic function, a learned model, or any other form of knowledge that can help to estimate the value of states or actions.
  - Double Progressive Widening (DPW): DPW is a technique used to handle continuous action and state spaces. It involves progressively increasing the number of children of a node for both states and actions as more simulations are run.
  - Pruning: In the context of MCTS, pruning is the process of removing branches from the search tree that are not likely to be selected for expansion. This is done to reduce the computational complexity of the algorithm and to focus the search on the most promising parts of the tree. Pruning in MCTS can be done using various strategies, such as:
  - Progressive Widening: This strategy involves gradually increasing the number of children of a node as more simulations are run.
  - Heuristic Pruning: This strategy involves using a heuristic function to estimate the potential of a node, and pruning those nodes that have a low estimated potential.
  - Caching: Caching in MCTS involves storing the results of previous simulations in a cache (a data structure), so that if the same position is encountered again in the future, the algorithm can simply look up the result in the cache instead of having to perform the simulation again. This can significantly speed up the MCTS algorithm.
"""
