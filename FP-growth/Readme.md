# Project 1: FP-growth

###### tags: `Data Mining`


## 一、開發環境：
* OS: Ubuntu 20.04.1
* CPU: AMD Ryzen™ 7 3700X
* Ｍemory: 32GB
* Disk: Micron Crucia MX500 (Read: 560M / Write :510M)
* Programming Language: C++11

透過以下指令可執行程式：
```
make
./fp-growth data/dataset.txt 0.5 0.5
```

---

## 二、程式碼實作邏輯
### Apriori Algorithm
1. 將 input file parse 成每個 transaction ID 作為 key，對應到全部所屬 item 所組成之集合的多個 itemset
2. 找出 frequent 1 itemset
3. 利用 frequent k itemset 下去排列組合，找出所有 k+1 itemset 的 candidates
4. 將沒有通過 minimum support 的 candidates 移除，產生 frequent k+1 itemset

### FP-growth
1. 將 input file parse 成每個 transaction ID 作為 key，對應到全部所屬 item 所組成之集合的多個 itemset
2. 用 linked list 結構作為 node，為每個 itemset 建立一條 path，搭建出初始的 FP tree
    - 每個 transaction 對應到的 itemset 依照總 frequency 降序排序
    - 將其中不滿足 minimum support 的 items 全部移除
3. 開始對 header table 中的每個 item 做 mining
    - 將所有出現該 item 的節點之 prefix pattern 視為新的 transaction itemset
    - 利用這些 itemset 回到第 2 點搭建出 conditional FP tree
    - 繼續向下遞迴，直到 header table 為空為止

## 三、演算法比較

|            |       Brute-force       |                         Apriori Algorithm                          |         FP-growth         |
| ---------- |:-----------------------:|:------------------------------------------------------------------:|:-------------------------:|
| 時間複雜度 | 隨 itemset 長度指數成長 | 不必列舉所有可能，平均而言略優於 Brute-force，但整體依然是指數成長 | 僅隨 itemset 長度線性成長 |
| 記憶體 |同右|需列舉出所有 candidates 存於變數後，再透過 minimum support 篩選，記憶體使用量較大|無須暫存candidates ，生成 FP tree 就好|
|Scan 次數|同右|每個 candidate 都要 scan 一次|僅生成 FP tree 時 scan 一次即可|

---

### 相同 item 數量、不同 min-sup 下的比較

可以看到無論 minimum support 的大小，FP-growth 的效能都優於 Apriori，原因就如同上方的比較，FP-growth 的各項表現都較為出色

在 Apriori 的數據中可以觀察到在 min-sup 線性遞減至 0.015 時，執行時間開始劇烈上升，這也如同前面所分析的，frequent 1-item 的數量雖然只會隨 min-sup 線性遞增，但其可排列組合出的 n-item candidates 數量卻是指數遞增的，才會造成執行時間飆升，而 FP-growth 的時間成長就相對較為平緩

| min-sup | Apriori | FP-growth |
| ------- | ------- | --------- |
| 0.010   | 239.30s | 64.00s    |
| 0.015   | 51.09s  | 13.07s    |
| 0.020   | 17.00s  | 6.54s     |
| 0.025   | 9.13s   | 0.19s     |
| 0.030   | 7.58s   | 0.08s     |
| 0.035   | 7.45s   | 0.07s     |
| 0.040   | 7.49s   | 0.06s     |

*2021 Testing Dataset: 25000 items*

---

### 相同 min-sup、不同 item 數量下的比較

兩者都可以看出執行時間隨著 item 數量增加而明顯成長，但 Apriori 的成長斜率明顯高於 FP-growth，這代表 item 數量 Apriori 演算法的影響較大

| item 數 | Apriori | FP-growth |
| ------- | ------- | --------- |
| 15000   | 13.82s  | 5.46s     |
| 10000   | 11.76s  | 4.24s     |
| 20000   | 17.21s  | 6.74s     |
| 25000   | 19.44s  | 7.51s     |
| 30000   | 22.83s  | 8.48s     |
| 35000   | 25.54s  | 9.23s     |
| 40000   | 28.62s  | 10.04s    |

*min-sup 固定 0.02*

## 結論

從上方的演算法及實驗結果中，可以觀察出整體而言 FP-growth 演算法的執行效能明顯優於 Apriori，其最關鍵性的差異是在於 Apriori 對於 item 數量非常敏感，數量稍增就會使需要產生的 candidates 數量激增，而 FP-growth 則透過只觀察 node 的 prefix pattern 來避免過多不必要的 candidates 列舉，也透過建立 FP-tree 來避免不斷重複 scan 資料表，因此整體效能較高。
