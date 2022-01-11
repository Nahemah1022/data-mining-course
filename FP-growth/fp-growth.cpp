#include <stdio.h>
#include <stdlib.h>
#include <set>
#include <map>
#include <vector>
#include <utility>

using namespace std;

map<int, vector<int>> table;

struct node {
    int feq;
    int itid;
    struct node *parent;
    struct node *next;
};

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
        table[tid].push_back(itid);
    }
}

void print_set(set<int> &s) {
    for (int i : s) {
        printf("%d", i);
    }
}

void print_tree(map<int, struct node *> &head_table) {
    // Milk, Bread, Beer, Coffee, Egg
    for (auto &head : head_table) {
        struct node *cur = head.second;
        printf("itid: %d(%d) => { ", head.first, cur->feq);
        cur = cur->next;
        while (cur) {
            if (cur->parent) {
                printf("%d|%d ", cur->feq, cur->parent->itid);
            } else {
                printf("%d ", cur->feq);
            }
            cur = cur->next;
        }
        printf("}\n");
    }
    printf("\n");
}

int partition(vector<int> &itemset, int l, int r, map<int, struct node *> &ref) {
    int pivot = itemset[r];
    int i = l-1;
    for (int j = l; j <= r-1; j++) {
        if (ref[itemset[j]]->feq >= ref[pivot]->feq) {
            i++;
            swap(itemset[i], itemset[j]);
        }
    }
    swap(itemset[i+1], itemset[r]);
    return i+1;
}

void qsort(vector<int> &itemset, int l, int r, map<int, struct node *> &ref) {
    if (l < r) {
        int pivot = partition(itemset, l, r, ref);
        qsort(itemset, l, pivot - 1, ref);
        qsort(itemset, pivot + 1, r, ref);
    }
}

map<int, struct node *> fp_tree(map<int, vector<int>> &transactions, map<int, int> frequency, int min_support) {
    // Counting frequency and create header table
    map<int, struct node *> head_table;
    for (auto &mit : transactions) {
        for (int itid : mit.second) {
            if (head_table.count(itid)) {
                head_table[itid]->feq += frequency[mit.first];
            } else {
                head_table[itid] = (struct node *)malloc(sizeof(struct node));
                head_table[itid]->feq = frequency[mit.first];
                head_table[itid]->parent = NULL;
                head_table[itid]->next = NULL;
                head_table[itid]->itid = itid;
            }
        }
    }

    // Deleting items below minSup
    for (auto it = head_table.cbegin(); it != head_table.cend();) {
        if (it->second->feq < min_support) {
            head_table.erase(it++);
        } else {
            ++it;
        }
    }

    // Constructing FP-tree by transactions
    for (auto &mit : transactions) {
        // Deleting non-frequent items
        mit.second.erase(std::remove_if(
            mit.second.begin(), mit.second.end(), 
            [head_table](int i) { return head_table.count(i) == 0; }
        ), mit.second.end());

        // Sorting itemset order by frequence
        qsort(mit.second, 0, mit.second.size() - 1, head_table);

        struct node *suffix_head = NULL;
        for (int i=mit.second.size()-1; i>=0; --i) { // iterate items in every transaction by reversed order
            bool flag = false;
            int itid = mit.second.at(i);
            // printf("%d ", itid);
            if (head_table.count(itid)) { // 選定使用第 i 個 item 來做 merge
                struct node *last = head_table[itid];
                for (struct node *link_node = head_table[itid]->next;
                    link_node != NULL;
                    link_node = link_node->next) { // 找過所有 item id 跟第 i 個 item 相同之 node，檢查是否可作為 merge point
                    int pos = i;
                    struct node *cur = link_node;
                    last = link_node;
                    while (pos >= 0 && cur) {
                        if (cur->itid != mit.second.at(pos)) {
                            break;
                        }
                        pos--;
                        cur = cur->parent;
                    }

                    if (pos == -1 && !cur) { // 成功 path match，直接把整條 path feq++
                        flag = true;
                        if (suffix_head) { // link to suffix head
                            suffix_head->parent = link_node;
                        }
                        while (link_node) {
                            link_node->feq += frequency[mit.first];
                            link_node = link_node->parent;
                        }
                        break;
                    }
                }

                if (flag) {
                    break;
                } else { // 若現存 FP-tree 上的此 item 都無法完整 merge，則先建立新節點
                    struct node* new_head = (struct node*)malloc(sizeof(struct node));
                    new_head->itid = itid;
                    new_head->feq = frequency[mit.first];
                    new_head->parent = NULL;
                    new_head->next = NULL;
                    last->next = new_head;
                    if (suffix_head) {
                        suffix_head->parent = new_head;
                    }
                    suffix_head = new_head;
                }
            }
        }
    }

    return head_table;
}

bool feq_sort(struct node *a, struct node *b) {
    return a->feq < b->feq;
}

void mine_tree(map<int, struct node *> &head_table, int min_support, set<int> prefix, vector<set<int>> &frequent_itemsets) {
    // Sort the items with frequency and create a list
    vector<struct node *> sorted_head_table;
    for (auto &hit : head_table) {
        sorted_head_table.push_back(hit.second);
    }
    sort(sorted_head_table.begin(), sorted_head_table.end(), feq_sort);

    // Start with the lowest frequency
    for (auto &vit : sorted_head_table) {
        // Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        set<int> new_feq_set = prefix;
        new_feq_set.insert(vit->itid);
        frequent_itemsets.push_back(new_feq_set);

        // Find all prefix path, constrcut conditional pattern base
        struct node *item = vit->next;
        int index = 0;
        map<int, vector<int>> transactions;
        map<int, int> frequency;
        while (item) {
            struct node *cur = item->parent;
            while (cur) {
                transactions[index].push_back(cur->itid);
                cur = cur->parent;
            }
            frequency[index] = item->feq;
            index++;
            item = item->next;
        }

        // Construct conditonal FP Tree with conditional pattern base
        map<int, struct node *> new_head_table = fp_tree(transactions, frequency, min_support);

        if (new_head_table.size() > 0) {
            mine_tree(new_head_table, min_support, new_feq_set, frequent_itemsets);
        }
    }
}

bool is_subset(set<int> containee, vector<int> &container) {
    set<int>::iterator it;
    for (int itid : container) {
        it = containee.find(itid);
        if (it != containee.end()) {
            containee.erase(it);
        }
    }
    return containee.empty();
}

int get_support(set<int> testset) {
    int count = 0;
    for (auto &mit : table) {
        if (is_subset(testset, mit.second)) {
            count++;
        }
    }
    return count;
}

int main(int argc, char *argv[]) {
    parse(argv[1]);
    double min_sup = atof(argv[2]), min_confidence = atof(argv[3]);
    int min_support = min_sup * table.size();

    map<int, int> base_frequency;
    for (auto &mit : table) {
        base_frequency[mit.first] = 1;
    }

    map<int, struct node *> head_table = fp_tree(table, base_frequency, min_support);

    // print_tree(head_table);

    vector<set<int>> frequent_itemsets;
    set<int> s;
    mine_tree(head_table, min_support, s, frequent_itemsets);

    // Generate association rules
    for (auto &fs : frequent_itemsets) {
        // Compute powerset of each frequent itemset
        vector<set<int>> powerset;
        unsigned int pow_set_size = pow(2, fs.size());
        for (int j=1; j<pow_set_size-1; ++j) {
            int i=0;
            set<int> tmp;
            for (auto &item : fs) {
                if (j & (1 << i++)) {
                    tmp.insert(item);
                }
            }
            powerset.push_back(tmp);
        }

        int sup = get_support(fs);
        for (auto &s : powerset) {
            double confidence = (double)sup / get_support(s);
            if (confidence > min_confidence) {
                printf("Relation rules: ");
                print_set(s);
                printf(" -> ");
                print_set(fs);
                printf("\nSupport: %.6lf\nConfidence: %6lf\n", (double)sup / table.size(), confidence);
            }
        }
    }

    return 0;
}
