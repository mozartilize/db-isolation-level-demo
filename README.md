# db-isolation-level-demo

This is coding experience for my reading of Designing Data-Intensive Application's Transaction chapter.

The repo implements solutions for "write skew" anomaly.

>Write skew can occur if two transactions read the same objects, and then update some of those objects (different transactions may update different objects).

Martin Kleppmann gives 4 examples about "write skew":
1. Meeting room booking system
2. Multiplayer game: moving pieces to the same spot
3. Claiming a username
4. Preventing double-spending: check user's remaining money or points before spend

The second and third examples are easy to prevent by using a unique constrain. The others aren't because of empty result of `SELECT ... FOR UPDATE` query.

We could either use:
- Materializing conficts: create indicator records for the lock attach to
- Serialize isolation level
