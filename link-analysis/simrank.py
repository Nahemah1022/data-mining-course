import numpy as np
import pandas as pd
import csv
import os
import re
from tqdm import trange
from scipy import sparse
import matplotlib.pyplot as plt
import networkx as nx

DEPTH = 2
C1 = 0.9
C2 = 0.4
C3 = 0.02
DS_PATH = './dataset/'
OUTPUT_PATH = './output/SimRank/'

def build_adjacency(path):
    if ('ibm' in path):
        df = pd.read_csv(path, delim_whitespace=True, header=None, usecols=[1, 2])
        src = df.values
    else:
        with open(path) as f:
            src = [list(map(float, rec)) for rec in csv.reader(f, delimiter=',')]

    arr = np.array(src)
    itemset = set(list(arr[:, 0]) + list(arr[:, 1]))
    index_dict = { k: v for v, k in enumerate(itemset) }

    adj = sparse.lil_matrix((len(itemset), len(itemset)), dtype=float)
    for [i, j] in src:
        adj[index_dict[i], index_dict[j]] = 1

    return adj.todense(), index_dict

def sim_score(adj, c, a, b, d):
    if (d > DEPTH):
        return 0

    if (a == b):
        return 1    

    ia = np.asarray(adj[:, a]).reshape(-1)
    ib = np.asarray(adj[:, b]).reshape(-1)

    if (ia.sum() * ib.sum() == 0):
        return 0

    sim = 0
    for i in np.where(ia == 1)[0]:
        for j in np.where(ib == 1)[0]:
            sim += sim_score(adj, c, i, j, d+1)

    sim *= c / (ia.sum() * ib.sum())
    return sim

if __name__ == '__main__':
    filelist = [
        file for file in sorted(os.listdir(DS_PATH)) 
        if re.compile('(graph_([1-5])|sample-in-paper).txt').match(file)
    ]
    fig, axs = plt.subplots(len(filelist), 4, figsize=(10, 7))
    fig.tight_layout()
    for ax, file in zip(axs.ravel().reshape(-1, 4), filelist):
        ax[0].set_title(file)
        adj, index_dict = build_adjacency(os.path.join(DS_PATH, file))
        nx.draw(nx.DiGraph(adj), node_size=150, ax=ax[0], with_labels=True, arrows=True)

        n = adj.shape[0]
        print(f'file: {file}, nodes: {n}')
        result = []
        for i in range(n):
            row = [sim_score(adj, C1, i, j, 1) for j in range(n)]
            result.append(row)

        ax[1].matshow(np.array(result, dtype=float), cmap=plt.cm.Blues)
        np.savetxt(f'{OUTPUT_PATH}{file[:-4]}_SimRank.txt', np.array(result, dtype=float))

        result = []
        for i in range(n):
            row = [sim_score(adj, C2, i, j, 1) for j in range(n)]
            result.append(row)

        ax[2].matshow(np.array(result, dtype=float), cmap=plt.cm.Greys)

        result = []
        for i in range(n):
            row = [sim_score(adj, C3, i, j, 1) for j in range(n)]
            result.append(row)

        ax[3].matshow(np.array(result, dtype=float), cmap=plt.cm.Greens)

    plt.subplots_adjust(top=0.9)
    plt.show()
