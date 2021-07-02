# Compute top-k nearest neighbor words for each word in wordvecs model
# Current algorithm is naive with O(n^2) comparisons,
# O(log k) per comparison to maintain top-k list

import numpy as np
from heapq import *
import sys

K = 10  # top-k words
M = 100  # matmul comp chunk size

def main():
    MODEL_PATH = sys.argv[1]

    with open(MODEL_PATH) as f:
        model_lines = f.readlines()

    N = len(model_lines)  # number of words
    assert N % M == 0  # for my bad indexing later
    words = [""] * N  # word index
    DIM = len(model_lines[0].strip().split()) - 1
    assert DIM >= 50  # make sure we got rid of first line of fasttext format
    vecs = np.empty((N, DIM))  # words indexed by row

    for i in range(N):
        line = model_lines[i].strip().split()
        words[i] = line[0]
        v = np.array(line[1:], dtype=np.float)
        vecs[i,] = v / np.linalg.norm(v)  # normalize vecs


    # too much memory to store all vector distances, so compute in chunks
    for si in range(0, N, M):
        # compute all dot products (cos similarities) for words [si, si+M] vs all other words
        sims = vecs @ vecs[si:(si+M),].T

        for i in range(M):
            # create (sim, index) key-value pairs, excluding word i itself
            pairs = [(sims[j,i], j) for j in range(N) if j != si+i]

            # maintain top-k largest similarities using a *min* heap
            # continuously remove min element, at the end we have all the max elements
            top_pairs = []
            for pair in pairs:
                if len(top_pairs) < K:  # heap isn't full yet
                    heappush(top_pairs, pair)
                elif pair > top_pairs[0]:
                    heapreplace(top_pairs, pair)

            nearest_words = [words[pair[1]] for pair in nlargest(K, top_pairs)]
            print(words[si+i], " ".join(map(str, nearest_words)))

main()