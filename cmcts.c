#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "cmcts.h"
#include "cbitboard.h"
#include "xoroshiro128p.h"

#define s2 1.4142135623730951
typedef int_fast32_t s32;

u64 my_next(Node *n)
{
  return next(&n->b.s0, &n->b.s1) % n->children_size;
}

double my_log(double x)
{
  if (!x)
    return INFINITY;
  return log(x);
}

void delete_tree(Node *r)
{
  if (r->children)
  {
    for (int i = 0; i < r->children_size; ++i)
      delete_tree(&r->children[i]);
    free(r->children);
  }
}

u8 run(Board *b)
{
  Node root = {0};
  root.children = NULL;
  root.b = *b;
  root.info = 0;

  u32 iter = 0;
  unsigned long selection_time = 0, expansion_time = 0,
         simulation_time = 0, backprop_time = 0,
         start, end, sstart = clock(), bytes_malloced = 0;

  while (1)
  {
    if (clock() - sstart >= 3000000)
    {
      printf("Iterations in 3 seconds: %u Bytes malloc'd: %lu\nSelection time: %.3f Expansion time: %.3f\n", iter, bytes_malloced, selection_time/1000000.0, expansion_time/1000000.0);
      printf("Simulation time: %.3f Backprop time: %.3f\n", simulation_time/1000000.0, backprop_time/1000000.0);
      break;
    }
    iter++;

    start = clock();
    Node *node = &root;
    while (node->children)
    {
      if (node->children[0].info & 1)
        node = &node->children[my_next(node)];
      else
      {
        Node *s = &node->children[0];
        for (int i = 1; i < node->children_size; ++i)
        {
          if (node->children[i].uct > s->uct)
            s = &node->children[i];
        }
        node = s;
      }
    }
    end = clock();
    selection_time += end - start;

    // expansion
    start = clock();
    Node *leaf = node;
    if (is_terminal(&node->b) == 3)
    {
      u32 info = legal_moves(&node->b);
      u32 moves = info & 0x1fffff;
      node->children_size = info >> 21;
      node->children = malloc(sizeof(Node) * node->children_size);
      bytes_malloced += sizeof(Node) * node->children_size;
      node->info |= 1;
      for (int i = 0; i < node->children_size; ++i)
      {
        node->children[i].b = node->b;
        node->children[i].info = ((moves >> 3 * i) & 7) << 1;
        move(&node->children[i].b, (moves >> 3 * i) & 7);

        if (is_terminal(&node->children[i].b) < 2)
        {
          leaf = &node->children[i];
          leaf->score = INFINITY;
        }
        else if (swap_is_terminal(&node->children[i].b, (moves >> 3 * i) & 7) < 2)
        {
          leaf = &node->children[i];
          leaf->score = INFINITY;
        }
        else
          leaf = &node->children[my_next(node)];
      }
    }
    end = clock();
    expansion_time += end - start;

    // simulation
    start = clock();
    s32 score = 0;
    for (int i = 0; i < 10000; ++i)
    {
      Board b = leaf->b;
      while (is_terminal(&b) == -2)
        move(&b, get_move(&b));

      if (b.winner == (leaf->b.player ^ 1))
        score++;
      else if (b.winner == 2)
        score += 0;
      else
        score--;
    }
    end = clock();
    simulation_time += end - start;

    // backpropagation
    start = clock();
    while (leaf->root)
    {
      leaf->score += score;
      score *= -1;
      leaf->visits++;
      leaf->uct = 1.0*leaf->score/leaf->visits + s2 * my_log(sqrt(leaf->root->visits)/leaf->visits);
      leaf = leaf->root;
    }
    end = clock();
    backprop_time += end - start;
  }
  Node *max = &root.children[0];
  for (int i = 1; i < root.children_size; ++i)
    if (root.children[i].visits > max->visits)
      max = &root.children[i];
  u8 val = max->info & (7 << 1);
  delete_tree(&root);
  return val;
}
