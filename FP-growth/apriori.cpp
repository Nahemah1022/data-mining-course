#include <stdio.h>
#include <stdlib.h>
#include <set>
#include <map>
#include <vector>
#include <utility>

using namespace std;

map<int, set<int>> table;
set<int> one_itemset;

vector<set<int>> excluded_set;

void parse(char *filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        printf("File not found!\n");
        exit(1);
    }

    int tid, itid;
    while (fscanf(fp, "%d", &tid) != EOF) {
        fscanf(fp, "%d", &tid);
        fscanf(fp, "%d", &itid);
        table[tid].insert(itid);
        one_itemset.insert(itid);
    }
}

bool is_subset(set<int> *containee, set<int> *container) {
    set<int> result = *container;
    result.insert(containee->begin(), containee->end());
    
    return result == *container;
}

void prune(vector<pair<set<int>, int>> *candidates, int min_support) {
    for (auto &vit : *candidates) {
        for (auto &mit : table) {
            if (is_subset(&(vit.first), &(mit.second))) {
                vit.second++;
            }
        }
    }

    for (vector<pair<set<int>, int>>::iterator vit = candidates->begin(); vit != candidates->end();) {
        if (vit->second < min_support) {
            vit = candidates->erase(vit);
        } else {
            ++vit;
        }
    }
}

void combination(vector<pair<set<int>, int>> *src, vector<pair<set<int>, int>> *tgt, int n) {
    for (int i=0; i<src->size(); ++i) {
        for (int j=i+1; j<src->size(); ++j) {
            set<int> intersect;
            set_intersection(
                (src->at(i)).first.begin(), (src->at(i)).first.end(),
                (src->at(j)).first.begin(), (src->at(j)).first.end(),
                inserter(intersect, intersect.begin())
            );

            set<int> u = (src->at(i)).first;
            u.insert((src->at(j)).first.begin(), (src->at(j)).first.end());
            if (intersect.size() + 1 == n && find(tgt->begin(), tgt->end(), make_pair(u, 0)) == tgt->end()) {
                tgt->push_back(make_pair(u, 0));
            }
        }
    }
}

void print_set(set<int> *s) {
    printf("{ ");
    for (int i : *s) {
        printf("%d ", i);
    }
    printf("}");
}


void prune_conf(pair<set<int>, int> *item, vector<set<int>> *rhs, vector<pair<set<int>, int>> *reference, double min_confidence) {
    for (vector<set<int>>::iterator vit = rhs->begin(); vit != rhs->end();) {
        set<int> lhs;
        set_difference(
            item->first.begin(), item->first.end(),
            vit->begin(), vit->end(),
            inserter(lhs, lhs.end())
        );

        bool flag = false;
        for (auto &ref : *reference) {
            if (lhs == ref.first) {
                if ((double)(item->second)/(ref.second) > min_confidence) {
                    flag = true;
                    print_set(&lhs);
                    printf(" -> ");
                    print_set(&(item->first));
                    printf(" => ");
                    printf("%.3lf\n", (double)(item->second)/(ref.second));
                }
            }
        }
        
        if (!flag) {
            vit = rhs->erase(vit);
        } else {
            ++vit;
        }
    }
}

void combination_conf(vector<set<int>> *src, vector<set<int>> *tgt, int n) {
    for (int i=0; i<src->size(); ++i) {
        for (int j=i+1; j<src->size(); ++j) {
            // printf("%d, %d\n", i, j);
            set<int> intersect;
            set_intersection(
                (src->at(i)).begin(), (src->at(i)).end(),
                (src->at(j)).begin(), (src->at(j)).end(),
                inserter(intersect, intersect.begin())
            );

            set<int> u = src->at(i);
            u.insert((src->at(j)).begin(), (src->at(j)).end());
            if (intersect.size() + 1 == n && find(tgt->begin(), tgt->end(), u) == tgt->end()) {
                tgt->push_back(u);
            }
        }
    }
}

int main(int argc, char *argv[]) {
    parse(argv[1]);
    double min_sup = atof(argv[2]), min_confidence = atof(argv[3]);
    int min_support = min_sup * table.size();

    vector<pair<set<int>, int>> frequent_itemset[one_itemset.size()];

    // initialize frequent one itemset
    for (int itid : one_itemset) {
        set<int> s;
        s.insert(itid);
        frequent_itemset[0].push_back(make_pair(s, 0));
    }
    prune(&frequent_itemset[0], min_support);

    // generate all frequent itemset (greater than minimum support)
    for (int n=1; n<=frequent_itemset[0].size()-1; ++n) {
        combination(&frequent_itemset[n-1], &frequent_itemset[n], n);
        prune(&frequent_itemset[n], min_support);
    }

    // generate assocation rules (greater than minimum confidence)
    for (int n=1; n<=frequent_itemset[0].size()-1; ++n) { // 一層
        for (auto &vit : frequent_itemset[n]) { // 一個 set
            vector<set<int>> rhs[vit.first.size()];
            // 第一層
            for (auto &item : vit.first) {
                set<int> s;
                s.insert(item);
                rhs[0].push_back(s);
            }

            prune_conf(&vit, &rhs[0], &frequent_itemset[vit.first.size()-2], min_confidence);

            for (int d=1; d<vit.first.size()-1; ++d) {
                combination_conf(&rhs[d-1], &rhs[d], d);
                prune_conf(&vit, &rhs[d], &frequent_itemset[vit.first.size()-d-2], min_confidence);
            }
        }
    }

    return 0;
}
