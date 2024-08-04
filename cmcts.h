#pragma once

#include "cbitboard.h"

typedef struct Node
{
  struct Node *root;
  struct Node *children;
  u8 children_size;
  Board b;
  // 00000000
  // 1st bit: 1/0 expanded
  // 2-4 bit: simulated move
  u8 info;
  u64 score, visits;
  double uct;
} Node;

Node *create_node(Node *root, Board *state, u8 col);
u8 run(Board *b);
