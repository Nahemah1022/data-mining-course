CC = g++
CFLAGS = -std=c++11
OBJ := fp-growth apriori

all: fp-growth apriori

fp-growth: fp-growth.cpp
	$(CC) -o $@ $(CFLAGS) $<

apriori: apriori.cpp
	$(CC) -o $@ $(CFLAGS) $<

clean:
	rm -f $(OBJ)
