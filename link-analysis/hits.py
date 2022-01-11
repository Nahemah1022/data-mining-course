import numpy as np
import pandas as pd
import csv
import os
import re
from tqdm import tqdm
from scipy import sparse
import matplotlib.pyplot as plt
import networkx as nx

NUM_ITERATE = 1000
DS_PATH = './dataset/'
OUTPUT_PATH = './output/HITS/'

def build_adjacency(path):
    if ('ibm' in path):
        df = pd.read_csv(path, delim_whitespace=True, header=None, usecols=[1, 2])
        src = df.values
    else:
        with open(path) as f:
            src = [list(map(int, rec)) for rec in csv.reader(f, delimiter=',')]

    arr = np.array(src)
    itemset = set(list(arr[:, 0]) + list(arr[:, 1]))
    index_dict = { k: v for v, k in enumerate(itemset) }

    adj = sparse.lil_matrix((len(itemset), len(itemset)), dtype=int)
    for [i, j] in src:
        adj[index_dict[i], index_dict[j]] = 1

    return adj.todense(), index_dict

def show_figure(fig, auths, hubs, indexes):
    fig.set_xticks(indexes)
    fig.bar(
        np.array(indexes)-0.2, 
        auths.tolist()[0], 
        label='authority',
        color='black', width=0.4, align='center'
    )
    fig.bar(
        np.array(indexes)+0.2, 
        hubs.tolist()[0], 
        label='hubness',
        color='green', width=0.4, align='center'
    )

if __name__ == '__main__':
    filelist = [
        file for file in sorted(os.listdir(DS_PATH)) 
        # if re.compile('(graph_([1-6])|sample-in-paper).txt').match(file)
    ]
    fig, axs = plt.subplots(len(filelist), 2, figsize=(8, 12))
    fig.tight_layout()
    for ax, file in zip(axs.ravel().reshape(-1, 2), filelist):
        ax[0].set_title(file)
        adj, index_dict = build_adjacency(os.path.join(DS_PATH, file))
        nx.draw(nx.DiGraph(adj), node_size=150, ax=ax[0], with_labels=True, arrows=True)

        auths = hubs = np.ones(adj.shape[0], dtype=float)

        tqdm_dldr = tqdm(
            [*range(NUM_ITERATE)],
            desc=f'{file} (nodes: {adj.shape[0]}, edges: {np.count_nonzero(adj)})'
        )

        for _ in tqdm_dldr:
            new_auths = hubs * adj
            new_hubs = auths * adj.transpose()

            auths = new_auths / new_auths.sum()
            hubs = new_hubs / new_hubs.sum()

        np.savetxt(f'{OUTPUT_PATH}{file[:-4]}_HITS_authority.txt', auths)
        np.savetxt(f'{OUTPUT_PATH}{file[:-4]}_HITS_hub.txt', hubs)

        show_figure(ax[1], auths, hubs, [*range(hubs.shape[1])])
        handles, labels = ax[1].get_legend_handles_labels()

    fig.legend(handles, labels)
    plt.subplots_adjust(top=0.95)
    plt.show()
