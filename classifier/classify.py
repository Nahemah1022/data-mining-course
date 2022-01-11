import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB

names = [
    "Nearest Neighbors",
    "Decision Tree",
    "Naive Bayes",
    "Linear SVM",
    "Random Forest",
]

classifiers = [
    KNeighborsClassifier(3),
    tree.DecisionTreeClassifier(max_depth=5),
    GaussianNB(),
    SVC(kernel="linear", C=0.025),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
]

df = pd.read_csv("./rule.csv")

Y = df["Y"]
X = df.drop(labels='Y', axis=1)
training_rate = 0.8

total_rows = len(df.index)
pos = int(total_rows * training_rate)

trainingX = X.iloc[:pos, :].to_numpy()
testingX = X.iloc[pos:, :].to_numpy()
# print(trainingX.shape, testingX.shape)

trainingY = Y.iloc[:pos].to_numpy()
testingY = Y.iloc[pos:].to_numpy()
# print(trainingY.shape, testingY.shape)

for name, clf in zip(names, classifiers):
    clf.fit(trainingX, trainingY)
    training_score = clf.score(trainingX, trainingY)
    testing_score = clf.score(testingX, testingY)

    # if (name == "Decision Tree"):
    #     tree.plot_tree(clf)
    #     plt.show()

    print(name, training_score, testing_score)
