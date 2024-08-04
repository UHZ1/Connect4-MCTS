#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include "cbitboard.h"
#include "xoroshiro128p.h"


void init_board(Board *b)
{
  b->player = 0;
  b->winner = -2;
  b->s0 = clock();
  b->s1 = clock();
  b->boards[0] = b->boards[1] = 0;
  for (u8 i = 0; i < COLS; ++i)
    b->heights[i] = i * 7;
}

void move(Board *b, u8 col)
{
  u64 pos = 1llu << b->heights[col];
  b->boards[b->player] |= pos;
  b->heights[col]++;
  b->player ^= 1;
}

void undo_move(Board *b, u8 col)
{
  b->player ^= 1;
  b->heights[col]--;
  b->boards[b->player] ^= 1llu << b->heights[col];
}

u32 legal_moves(Board *b)
{
  u64 brd = b->boards[0] | b->boards[1];
  u32 moves = 0, size = 0;
  for (u8 i = 5; i <= 47; i += COLS)
  {
    if (!(brd & (1llu << i)))
    {
      moves |= (u64)(i / COLS) << size * 3;
      size++;
    }
  }
  return (size << 21) | moves;
}

u32 get_move(Board *b)
{
  u32 info = legal_moves(b);
  u32 moves = info & ((1llu << 21) - 1);
  u8 size = info >> 21;
  u8 x = next(&b->s0, &b->s1) % size;
  return (moves >> 3 * x) & 7;
}

s8 is_terminal(Board *b)
{
  u64 brd = b->boards[b->player ^ 1];

  if ((brd & (brd >> 1) & (brd >> 2) & (brd >> 3)) ||
      (brd & (brd >> 6) & (brd >> 12) & (brd >> 18)) ||
      (brd & (brd >> 7) & (brd >> 14) & (brd >> 21)) ||
      (brd & (brd >> 8) & (brd >> 16) & (brd >> 24)))
    b->winner = b->player ^ 1;
  else if (((b->boards[0] | b->boards[1]) & 141845657554976) == 141845657554976)
    b->winner = 2;
  else
    b->winner = 3;
  return b->winner;
}

s8 swap_is_terminal(Board *b, u8 col)
{
  undo_move(b, col);
  b->player ^= 1;
  move(b, col);
  s8 res = is_terminal(b);
  undo_move(b, col);
  b->player ^= 1;
  move(b, col);
  return res;
}

void print(Board *b)
{
  for (s8 i = ROWS - 1; i > -1; --i)
  {
    for (u8 j = i; j < i + 49; j += COLS)
    {
      //         >>:(
      u64 mask = 1llu << j;
      if (b->boards[0] & mask)
        printf("0 ");
      else if (b->boards[1] & mask)
        printf("1 ");
      else
        printf(". ");
    }
    printf("\n");
  }
}
