import numpy as np
import pandas as pd
import csv
import os
import re
from scipy import sparse
import matplotlib.pyplot as plt
import networkx as nx

NUM_ITERATE = 3
EPSILON = 1e-5
DAMPING_FACTOR_1 = 0.5
DAMPING_FACTOR_2 = 0.1
DAMPING_FACTOR_3 = 1e-5
DS_PATH = './dataset/'
OUTPUT_PATH = './output/PageRank/'

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

def show_figure(fig1, fig2, fig3, pr1, pr2, pr3, cnt1, cnt2, cnt3, indexes):
    fig1.set_xticks(indexes)
    fig1.set_title(f'converged iteration: {cnt1}')
    fig1.bar(
        np.array(indexes), 
        pr1.tolist()[0], 
        label=f'damping factor = {DAMPING_FACTOR_1}',
        color='blue', width=0.4, align='center'
    )
    fig2.set_xticks(indexes)
    fig2.set_title(f'converged iteration: {cnt2}')
    fig2.bar(
        np.array(indexes), 
        pr2.tolist()[0], 
        label=f'damping factor = {DAMPING_FACTOR_2}',
        color='red', width=0.4, align='center'
    )
    fig3.set_xticks(indexes)
    fig3.set_title(f'converged iteration: {cnt3}')
    fig3.bar(
        np.array(indexes), 
        pr3.tolist()[0], 
        label=f'damping factor = {DAMPING_FACTOR_3}',
        color='green', width=0.4, align='center'
    )

if __name__ == '__main__':
    filelist = [
        file for file in sorted(os.listdir(DS_PATH)) 
        # if re.compile('(graph_([1-6])|sample-in-paper).txt').match(file)
    ]
    fig, axs = plt.subplots(len(filelist), 4, figsize=(10, 7))
    fig.tight_layout()
    for ax, file in zip(axs.ravel().reshape(-1, 4), filelist):
        ax[0].set_title(file)
        adj, index_dict = build_adjacency(os.path.join(DS_PATH, file))
        nx.draw(nx.DiGraph(adj), node_size=150, ax=ax[0], with_labels=True, arrows=True)

        n = adj.shape[0]
        pr1 = pr2 = pr3 = np.full(n, 1/n, dtype=float)
        cnt1 = cnt2 = cnt3 = 0
        adj = np.divide(adj, adj.sum(axis=1), out=np.zeros_like(adj), where=adj.sum(axis=1) != 0)

        new_pr1 = DAMPING_FACTOR_1 / n + (1 - DAMPING_FACTOR_1) * (pr1 * adj)
        while(np.absolute(new_pr1 - pr1).mean() > EPSILON):
            pr1 = new_pr1
            new_pr1 = DAMPING_FACTOR_1 / n + (1 - DAMPING_FACTOR_1) * (pr1 * adj)
            # print(np.absolute(new_pr1 - pr1).mean())
            cnt1 = cnt1 + 1
        pr1 = new_pr1

        new_pr2 = DAMPING_FACTOR_2 / n + (1 - DAMPING_FACTOR_2) * (pr2 * adj)
        while(np.absolute(new_pr2 - pr2).mean() > EPSILON):
            pr2 = new_pr2
            new_pr2 = DAMPING_FACTOR_2 / n + (1 - DAMPING_FACTOR_2) * (pr2 * adj)
            cnt2 = cnt2 + 1
        pr2 = new_pr2

        new_pr3 = DAMPING_FACTOR_3 / n + (1 - DAMPING_FACTOR_3) * (pr3 * adj)
        while(np.absolute(new_pr3 - pr3).mean() > EPSILON):
            pr3 = new_pr3
            new_pr3 = DAMPING_FACTOR_3 / n + (1 - DAMPING_FACTOR_3) * (pr3 * adj)
            cnt3 = cnt3 + 1
        pr3 = new_pr3

        np.savetxt(f'{OUTPUT_PATH}{file[:-4]}_PageRank.txt', pr1)

        show_figure(ax[1], ax[2], ax[3], pr1, pr2, pr3, cnt1, cnt2, cnt3, [*range(pr1.shape[1])])
        handles, labels = ax[1].get_legend_handles_labels()
        handles2, labels2 = ax[2].get_legend_handles_labels()
        handles3, labels3 = ax[3].get_legend_handles_labels()

    fig.legend(handles, labels, loc=(0.3, 0.95))
    fig.legend(handles2, labels2, loc=(0.55, 0.95))
    fig.legend(handles3, labels3, loc=(0.78, 0.95))
    plt.subplots_adjust(top=0.9)
    plt.show()
