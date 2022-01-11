# Project2 : Classification

###### tags: `Data Mining`

## 程式執行
### 生成資料集
```
python abs_generator.py
```

### 分類
```
python classify.py
```

---

**📈 分析流程：**
在本次專案中，我將設計一套 absolutely right rule 去產出足量的資料，並選擇 [scikit-learn](https://scikit-learn.org/) 當中提供的數種 classifier 去對資料做分類，再依據 classifier 的準確率表現來回頭調整 rule 中的各種屬性，由此分析這些 classifier 在面對各種屬性的資料時的適配性。

## 一、Absolutely Right Rules

針對這次專案，我所設計的 absolutely right rule 是參考台灣的[兵役徵召規則](https://mms.taichung.gov.tw/Newsoldier/List_2)，其中為成年男性的多項身體數值定義了免役的判定指標，我從中挑選了幾個較具有代表性的指標來組成 absolutely right rule，**只要任一指標未通過及符合免役資格**，規則如下表所示（以下簡稱為 base rule）：

|          | 身高           | 視力         | 智能 | 扁平足          | 氣胸   | 心律不整 | 自閉症 |
| -------- | -------------- | ------------ | ------ | ------------- | ------ | -------- | ------ |
| 數值範圍 | 140~220 | 2.0~0 | 180~60 | 0 or 1 | 0 or 1 | 0 or 1   | 0 or 1 |
| 役男條件 | 155<x1<196 | x2 > 0.1     | x3 > 85 | x4 = 0 | x5 = 0 | x6 = 0   | x7 = 0 |

由此 base rule 去產生役男/免役 (positive/negitive) 資料約各半的 dataset，用 `pandas.DataFrame.describe()` 的格式大致如下：

```shell
$ python abs_gengrator.py

      col_0  col_1  col_2  col_3  col_4  col_5  col_6  Y
0       184    0.7    115      0      0      0      0  1
1       219    0.4     68      0      0      0      0  0
2       212    1.8    164      0      0      0      0  0
3       193    1.0    125      0      0      0      0  1
4       186    0.1    110      0      0      0      0  1
...     ...    ...    ...    ...    ...    ...    ... ..
9995    165    1.3    177      0      0      0      0  1
9996    183    1.0    146      0      0      0      0  1
9997    179    1.1    136      0      0      0      0  1
9998    172    1.7    112      0      0      0      0  1
9999    172    0.8    160      0      0      0      0  1

[10000 rows x 8 columns]
```

## 二、Classifiers

選用以下八種 [scikit-learn](https://scikit-learn.org/) 提供的 classifier，並將上述產生的資料 80% 做為 training data、20% 作為 testing data，效果如下：

|                     | Hyperparameters                              | Accuracy(training/testing) |
| ------------------- | -------------------------------------------- | -------------------------- |
| K Nearest Neighbors | k = 3                                        | 0.98/0.99                  |
| Decision Tree       | max_depth = 5                                | 1.00/1.00                  |
| Random Forest       | max_depth=5, n_estimators=10, max_features=1 | 1.00/1.00                  |
| Naive Bayes         |                                              | 0.89/0.84                  |
| Linear SVM          | C=0.0025                                     | 0.63/0.65                  |


可以看出大部分 classifier 的表現各有優劣，以下將逐一探究每個 classifier 在這個 dataset 上表現得好/壞之原因，並會嘗試修改 base rule、重新生成不同屬性的 dataset 後再測試來驗證原因是否正確。

### 1. K Nearest Neighbors (KNN)

KNN 會找出與其最近的 K 個資料點來共同決定資料類別，因此在空間中**同類別資料的分佈越密集，KNN 的表現就會越好**，而因為 base rule 所產生的資料類別必定是切確的(deterministic)，會直接將資料空間一分為二，所以只要資料涵蓋度足夠，KNN 的表現勢必會相當不錯，只有在靠近邊界處才會出現誤判。
然而 KNN 的缺點在於**無法判斷 attribute 的重要程度**，若有與 classifaction rule 完全無關 (irrelevant) 的 attribute 存在，KNN 也會把資料在這個維度上的距離視作與其他重點 attributes 同等重要的資訊，進而造成誤判，以下將實驗插入 7 個數值完全隨機的 attributes 後對 accuracy 的影響。

```shell
$ python abs_generator.py --irrelevant 7


      col_0  col_1  col_2  col_3  col_4  ...  col_10  col_11  col_12  col_13  Y
0       186    0.7     76      0      0  ...       5     121      17     144  0
1       176    0.1    155      0      0  ...      69     174      96      69  1
2       210    1.1    117      0      0  ...     156      66     183     183  0
3       197    0.8    133      0      0  ...     168     143       6     118  0
4       175    0.5    162      0      0  ...      84      28      90      88  1
...     ...    ...    ...    ...    ...  ...     ...     ...     ...     ... ..
9995    156    1.4    179      0      0  ...      80     169      10       5  1
9996    155    0.3    114      0      0  ...     112       8     180      30  1
9997    196    1.5    107      0      0  ...      87      51      28     133  1
9998    187    1.3    165      0      0  ...     157      49     167      67  1
9999    157    0.1    178      0      0  ...      70      73      16     145  1
```
如上所示，`col_7` 到 `col_13` 是與 base rule 完全無關的亂數，在此 dataset 中 KNN 的表現如下：
- training data accuracy: 0.82
- testing data accuracy: 0.69

看得出來比原先下降了不少，由此可知 KNN 不擅長處理存在 irrelevant attributes 的 dataset。

---

### 2. Decision Tree

Decision tree 是透過選定某個 attribute 的值作為分歧點，來使資料類別盡可能被一分為二的演算法，換句話說，**只要資料類別有辦法被某個 attribute 的值完全一分為二，decision tree 就可以做到 100% 的準確率**，也不會像 KNN 一樣被無關的 attribute 影響。
而上述由 base rule 產生的資料每個 attribute 都存在明確的分割點，所以準確率才會高達 1.0，但**當 classifaction rule 的 attributes 彼此之間不完全獨立時，將很難有效地切割**，以下將實驗把 rule 設計成需要共同考慮多個 attributes 才能做分類後，觀察其對 accuracy 的影響。

#### 2-1. Attributes 之間部份相依

|          | 身高       | 體重          | 視力     | 智能    |
| -------- | ---------- | ------------- | -------- | ------- |
| 數值範圍 | 140~220    | 30~130        | 2.0~0    | 180~60  |
| 役男條件 | 155<x1<196 | ==16.5<BMI<31.5== | x2 > 0.1 | x3 > 85 |

將 base rule 擴張如上，新增體重一欄並以 BMI (須共同考慮到身高與體重兩個 attribute) 作為判斷標準，再將後方所有的 binary attribute 移除後，由此 rule 重新產生 dataset 後表現如下：
```sehll
$ python abs_generator.py --use_bmi True --binary 0
```
- training data accuracy: 0.93
- testing data accuracy: 0.96

可以看到 accuracy 已經不再是 100%，這表示存在不完全獨立的 attributes 確實會影響到 decision tree 的表現。

#### 2-2. Attributes 全部相依

為了進一步提高 attributes 之間的相依性，因此我將 rule 中的 binary attributes 加回來，再從只要滿足任一條件改為至少須滿足三項條件才可免役，如此一來 classifaction 就必須**同時考慮所有的 attributes** 才能夠正確判斷，重新產生 dataset 後表現如下：
```shell
$ python abs_generator.py --use_bmi True --dependent 3
```
- training data accuracy: 0.88
- testing data accuracy: 0.72

accuracy 再次降低了，這再次驗證上述說法之正確，attributes 之間的相依性越高，decision tree 的效果將會越差。

---

### 3. Random Forest

Decision tree 除了上述問題之外，從其對上述最後一個 rule 之 accuracy 在 training 與 testing data 之間有明顯的落差，可看出其存在 overfitting 的問題，而 random forest 透過由多個 decision tree 各只使用一部分的 training data 再共同決定分類結果，來避免整體 overfitting 於 training data 上，這邊同樣使用 scikit-learn 的 random forest 套件於上述 dataset 表現如下：
- training data accuracy: 0.90
- testing data accuracy: 0.90

雖然沒有在 training accuracy 上有明顯的進步，但與 testing accuracy 之間的落差確實下降了許多，這代表 random forest 確實有避免 overfitting 的功效。

---

### 4. Naive Bayes

Navie bayes 是完全將 attribute 發生的機率視作獨立事件後，找出屬於該類別之機率最高者的算法，在 base rule 中由於 attributes 之間是完全互相獨立的，因此 naive bayes 的表現相當不錯，即便仿照上方 KNN 的作法加入了一些 irrelevant attributes 表現依舊不錯，這是因為 irrelevant attributes 對於所屬類別的機率貢獻會完全相同，並不會對最後的類別判斷有影響。
然而，假設 attributes 之間完全互相獨立也是 navie bayes 最大的缺點，以下同樣會實驗把 rule 插入體重一欄並將 BMI 加入 classifaction rule 後觀察其對 accuracy 的影響。
- training data accuracy: 0.83
- testing data accuracy: 0.47

可以看到 accuracy 大幅降低了，驗證了 naive bayes 非常依賴 attributes 之間的獨立性。

---

### 5. Linear SVM

Linear SVM 的算法是找到線性邊界來盡可能使他與兩個群的整體距離最大化，但由於上方的 base rule 會將每個 attribute 獨立考慮，因此該邊界必定是非線性的，所以在此 linear SVM 的表現並不好，以下將實驗將 classifaction rule 改為 attribute 之間的線性組合後觀察其對 accuracy 的影響。

$$
300 < 身高 - 100 \times 視力 + 2 \times 智商 < 450
$$

將 rule 改為若落在上述公式的範圍內，則為 positive data，修改規則後表現如下：
```shell
$ python abs_generator.py --use_linear True
```
- training data accuracy: 0.91
- testing data accuracy: 0.98

accuracy 大幅上升了，這說明**若分群邊界是線性的，linear SVM 會表現的非常好**。

## 三、Summary

下方表格簡單整理了這次 project 有嘗試使用的模型及其優劣勢，可以看出分類模型各有優劣，並沒有哪一種模型的表現必定會最好，應要根據目前資料的特性去挑選合適的模型，因此在拿到要分類的資料時不妨先將這些主流模型全都試過一次，可以先根據其表現來對照這個表格，簡單歸納出資料的特性後再繼續後續的處理。

|               | 優勢                                        | 劣勢                                     |
| ------------- | ------------------------------------------- | ---------------------------------------- |
| KNN           | 簡單易用                                    | 無法判別 feature 的重要性                |
| Decision Tree | 自動找出有用的 feature                      | 容易 overfitting、不好處理非獨立 feature |
| Random Forest | 大幅改進了 decision tree overfitting 的問題 | 還是不好處理非獨立 feature               |
| Naive Bayes   | 自動找出有用的 feature                      | 不好處理非獨立 feature                   |
| Linear SVM    | 容易處理線性分類規則                        | boundary 非線性時無法分割                |
