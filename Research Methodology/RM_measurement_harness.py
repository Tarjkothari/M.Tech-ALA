"""Measurement harness: skip list vs red-black tree vs splay tree.
Dependent variable: nodes inspected per successful search (machine independent),
secondary: microseconds per search (Python wall-clock)."""
import csv, platform, random, sys, time
sys.path.insert(0, "/home/claude/ads")
from skiplist import SkipList
from trees import RedBlackTree, SplayTree, SNode


class CountingRB(RedBlackTree):
    def search_count(self, key):
        x, c = self.root, 0
        while x is not self.NIL:
            c += 1                                   # one node inspected
            if key == x.key:
                return c
            x = x.left if key < x.key else x.right
        return c


class CountingSplay(SplayTree):
    visits = 0

    def _splay(self, t, key):                        # same algorithm, with an inspection counter
        if t is None:
            return None
        N = SNode(None)
        l = r = N
        while True:
            self.visits += 1
            if key < t.key:
                if t.left is None:
                    break
                self.visits += 1
                if key < t.left.key:
                    y = t.left
                    t.left, y.right = y.right, t
                    t = y
                    if t.left is None:
                        break
                r.left = t
                r, t = t, t.left
            elif key > t.key:
                if t.right is None:
                    break
                self.visits += 1
                if key > t.right.key:
                    y = t.right
                    t.right, y.left = y.left, t
                    t = y
                    if t.right is None:
                        break
                l.right = t
                l, t = t, t.right
            else:
                break
        l.right, r.left = t.left, t.right
        t.left, t.right = N.right, N.left
        return t


def build(structure, keys, seed):
    if structure == "SkipList":
        s = SkipList(p=0.5, seed=seed)
        for k in keys:
            s.insert(k, k)
    elif structure == "RedBlack":
        s = CountingRB()
        for k in keys:
            s.insert(k)
    else:
        s = CountingSplay()
        for k in keys:
            s.insert(k)
    return s


def run_queries(structure, s, queries):
    t0 = time.perf_counter()
    if structure == "SkipList":
        s.steps = 0
        for q in queries:
            s.search(q)
        nodes = s.steps
    elif structure == "RedBlack":
        nodes = 0
        for q in queries:
            nodes += s.search_count(q)
    else:
        s.visits = 0
        for q in queries:
            s.search(q)
        nodes = s.visits
    dt = time.perf_counter() - t0
    return nodes / len(queries), dt / len(queries) * 1e6


def make_data(rep, n, Q):
    rng = random.Random(1000 + rep)
    keys = rng.sample(range(1, 10 ** 6), n)
    hot = rng.sample(keys, max(1, n // 100))
    uni = [rng.choice(keys) for _ in range(Q)]
    skew = [rng.choice(hot) if rng.random() < 0.9 else rng.choice(keys) for _ in range(Q)]
    return keys, {"uniform": uni, "skewed": skew}


def main(reps=30, n=5000, Q=3000, out="rm_experiment_data.csv"):
    rows = []
    for rep in range(1, reps + 1):
        keys, wl = make_data(rep, n, Q)
        for order, ks in (("random", keys), ("sorted", sorted(keys))):
            for structure in ("SkipList", "RedBlack", "Splay"):
                for wname, queries in wl.items():
                    s = build(structure, ks, seed=rep * 7 + 1)
                    nodes, us = run_queries(structure, s, queries)
                    rows.append([rep, structure, order, wname, n, Q, round(nodes, 4), round(us, 3)])
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["replication", "structure", "insertion_order", "workload", "n_keys", "n_queries", "mean_nodes_per_search", "us_per_search"])
        w.writerows(rows)
    print("rows:", len(rows), "| python", platform.python_version(), "|", platform.system(), platform.machine())


if __name__ == "__main__":
    main()
