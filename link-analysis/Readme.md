# Project 3: Link Analysis

###### tags: `Data Mining`

除了提供的 `graph_*` 以及 `ibm-5000` 資料之外，我還另外加入了 HITS 的 paper 中使用的實驗資料（命名為 `sample-in-paper`），以下表格簡述其 metadata
|                 | nodes | edges |
| --------------- | ----- |:-----:|
| graph_1         | 6     |   5   |
| graph_2         | 5     |   5   |
| graph_3         | 4     |   6   |
| graph_4         | 7     |  18   |
| graph_5         | 469   | 1102  |
| graph_6         | 1228  | 5220  |
| sample-in-paper | 15    |  22   |
| ibm-5000        | 836   | 4798  |

## 一、實作細節
*以下將逐一說明實作 HITS、PageRank、SimRank 三個演算法的細節*

### HITS
首先將 txt 檔讀入，並由 numpy 建立 adjacency matrix，產生結果如下：
```bash
# adjacency matrix of graph_1
[[0 1 0 0 0 0]
 [0 0 1 0 0 0]
 [0 0 0 1 0 0]
 [0 0 0 0 1 0]
 [0 0 0 0 0 1]
 [0 0 0 0 0 0]]
```
建立兩個 $n \times 1$ 的 numpy array 分別作為 authority 跟 hubness，再不斷迭代計算直到收斂
```python=
auths = hubs = np.ones(adj.shape[0], dtype=float)
while(not is_converged()):
    # assign new value
    new_auths = hubs * adj
    new_hubs = auths * adj.transpose()

    # normalization
    auths = new_auths / new_auths.sum()
    hubs = new_hubs / new_hubs.sum()
```
最後將值輸出成檔案
```python=
np.savetxt(f'{OUTPUT_PATH}{file[:-4]}_HITS_authority.txt', auths)
np.savetxt(f'{OUTPUT_PATH}{file[:-4]}_HITS_hub.txt', hubs)
```

### PageRank
同樣先建立出 adjacency matrix，並對每一個 row 做 normalization，這個動作代表代表每個 node 當前的 PR 值將經由其 out-going edge 等量流出
```python=
adj = build_adjacency()
adj = adj / adj.sum(axis=1)
```
再建立一個 $n \times 1$ 的 numpy array 存放 pagerank，初始值皆為 $\frac{1}{n}$
```python=
pr = np.full(n, 1/n, dtype=float)
```
根據要求的公式，不斷 update pagerank 值到收斂為止
$$
PR(P_i)=\frac{d}{n}+(1-d)\sum_{l_{i,j}\in E}\frac{PR(P_j)}{Outdegree(P_j)}
$$
```python=
while(not is_converged()):
    damping = DAMPING_FACTOR / n
    pr = damping + (1 - DAMPING_FACTOR) * (pr * adj)
```
最後將值輸出成檔案
```python=
np.savetxt(f'{OUTPUT_PATH}{file[:-4]}_PageRank.txt', pr)
```

### SimRank
實做以下公式：
$$
S(a,b)=\frac{C}{|I(a)||I(b)|}\sum^{|I(a)|}_{i=1}\sum^{|I(b)|}_{j=1}S(I_i(a),I_j(b))
$$

由下方公式遞迴函式，對任兩個 node 計算 `sim_score`，並再值小於一定 threshold 後終止遞迴
```python=
def sim_score(adj, a, b):
    if (a == b):
        return 1    

    ia = np.asarray(adj[:, a]).reshape(-1)
    ib = np.asarray(adj[:, b]).reshape(-1)

    if (ia.sum() * ib.sum() == 0):
        return 0

    sim = 0
    for i in np.where(ia == 1)[0]:
        for j in np.where(ib == 1)[0]:
            sim += sim_score(adj, i, j, d+1)

    sim *= C / (ia.sum() * ib.sum())
    return sim
```

## 二、結果分析

### HITS
![](https://i.imgur.com/f2YLq3N.png)

- `graph_1.txt`：
單一 path 的 graph，可以發現若一個 node 不具有 in-edge/out-edge，則 authority/hubness 值將會直接歸零，這可能會造成我們衡量上的一些 bias。
- `graph_2.txt`:
形成一個 loop 的 graph，因此每個 node 會向下傳遞/由上接收的 authority/hubness 值是相同的，因此結果是一個 authority/hubness 值都完全平衡的狀態。
- `graph_3.txt`:
對每個 node 可以觀察到以下現象：
    - authority 值與 in-degree 正相關
    - hubness 值與 out-degree 正相關
這符合我們最初對 authority、hubness 將要分別代表其可信度、重要性的期待。
- `graph_4.txt`、`sample_in_paper`:
可以觀察到，若 in-edge 連接到的 node 之 authority/hubness 值明顯突出，則該 node 本身的 hubness/authority 值也會跟著被明顯拉高，這也符合我們最初對 authority、hubness 將要分別代表其可信度、重要性的期待，例如 `sample-in-paper.txt` 圖中 node 12 的 authority 值就是被 node 11 明顯突出的 hubness 值給拉高的。

然而 HITS 這種 mutually reinforcing 的機制也造成了他在一些特殊的資料上會失去效果，例如若刻意在 graph 中置入一個 fully connected 的 sub-graph，將會造成整個 graph 的 authority/hubness 值往該 sub-graph 處傾斜，這容易成為有心人士操作其結果的手段。

### PageRank
*最終輸出結果使用的 `damping_factor=0.15`, `epsilon=1e-5`*

![](https://i.imgur.com/AsoE0si.png)

- `graph_1.txt`：
單一 path 的 graph，可以發現 pagerank 會傾向往下游傳遞分數，但也容易造成分數全都塞在下游而無法流出的狀況，這可以透過提升 damping factor 來增加隨機跳出的比例，因此從結果也可以觀察到 damping factor 較高者較不容易有分數塞在下游的狀況。
- `graph_2.txt`：
一個完全封閉的環，由於 pagerank 值只會由 out-edge 等量流出，因此完全對稱的環會造成所有 node 的值都相等，並在第一個 iteration 就直接是收斂的結果。
- `graph_3.txt`：
可以觀察到與 HITS 中的 authority 相同的是，pagerank 分數跟 in-degree 數量成正比，且在這種對稱的 graph 中 damping factor 大小並不會影響結果。
- `graph_4.txt`、`sample_in_paper`:
在這種較複雜的 graph 中，大致上可以看出位於**匯流點**的 node 之 pagerank 分數會較高，且越高的 dampling factor 會使 node 之間的 pagerank 分數趨向平衡。

### SimRank
*最終輸出結果使用的 `decay factor=0.6`*
![](https://i.imgur.com/vBrPqqq.png)
上圖由左至右的 Decay Factor 分別是 `0.9`、`0.3`、`0.02`

- `graph_1.txt`、`graph_2.txt`:
由於 SimRank 是由找出任兩 node 的 in-edge 指向共同 node 數量來衡量，而在這兩份資料中不存在任兩 node 有共同的 parent，因此除了與自身的 SimRank 是 `1` 之外，其餘 pairs 結果皆為 `0`。
- 其他：
可以觀察到兩 node 若在同一距離存在共同 parent 的數量越多，則 SimRank 分數越高，且分數與 Decay Factor 成負相關，這反映出 Decay Factor 的遞減效果。

## 三、效能分析

|                 | nodes | edges |    HITS    |  PageRank  |  SimRank  |
| --------------- |:-----:|:-----:|:----------:|:----------:|:---------:|
| graph_1         |   6   |   5   | 0.894 sec  | 1.011 sec  | 1.018 sec |
| graph_2         |   5   |   5   | 0.933 sec  | 1.004 sec  | 1.014 sec |
| graph_3         |   4   |   6   | 0.941 sec  | 1.037 sec  | 0.987 sec |
| graph_4         |   7   |  18   | 1.003 sec  | 1.038 sec  | 0.937 sec |
| graph_5         |  469  | 1102  | 2.921 sec  | 2.768 sec  | 2min 1sec |
| graph_6         | 1228  | 5220  | 10.050 sec | 11.768 sec |     -     |
| sample-in-paper |  15   |  22   | 1.129 sec  | 1.200 sec  | 1.438 sec |
| ibm-5000        |  836  | 4798  | 4.6891 sec | 16.883 sec |     -     |

可以看出執行時間基本上跟 nodes、edges 數量成正相關，特別是 SimRank 的執行時間而劇烈成長，原因是 SimRank 演算法是透過遞迴的方式不斷往回尋找共同 parent，一旦 node、edge 數量增加，在每一次遞迴中需要考慮的可能性數量也會遽增。

## 四、結論

如同前面討論到的 HITS 跟 PageRank 演算法各有其優劣，但若要用在搜尋引擎上的話，HITS 有個致命的缺點是，沒辦法考慮到搜尋引擎本身的 query 內容與 nodes 之間的相關性，這也造成 HITS 雖然公式上非常漂亮，但卻不實用，相較之下 PageRank 則比較實際，因此才被主流搜尋引擎廣大採用。
