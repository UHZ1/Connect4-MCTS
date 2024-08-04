#include <stdint.h>
#include "xoroshiro128p.h"

static inline uint64_t rotl(const uint64_t x, int k) {
	return (x << k) | (x >> (64 - k));
}

uint64_t next(uint64_t *s0, uint64_t *s1) {
	const uint64_t result = *s0 + *s1;

	*s1 ^= *s0;
	*s0 = rotl(*s0, 24) ^ *s1 ^ (*s1 << 16); // a, b
	*s1 = rotl(*s1, 37); // c

	return result;
}
