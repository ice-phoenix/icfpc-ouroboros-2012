icfpc-ouroboros-2012
====================

Grand Strategy
==============

Simulate the future using several simple local strategies and return the best move.

Local Strategies
================

1. **Greedy**: try to move towards a spot that's nearest to all lambdas
2. **Quitter**: always abort
3. **Lazy**: always wait
4. **Swimmer**: if in water, get out; if not, wait

Bots we didn't have time to implement:

5. **Driven**: heads for the nearest lambda, then the lambda nearest to that lambda, and so on.
6. **TrampLover** (heh): heads straight for the trampoline that teleports you to the largest cluster of lambdas
7. **Beeline**: heads straight for the exit
8. **Nondeterministic**: moves pseudorandomly
