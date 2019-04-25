from enum import IntEnum
from random import shuffle
from collections import Counter
from itertools import chain, combinations, filterfalse
#create a dictionary to map a cards number to its rank
valid_ranks = list(range(0,13))
valid_cards = ['3','4', '5', '6', '7','8', '9','T', 'J', 'Q', 'K','A','2']
value_rules = {k:v for (k,v) in zip(valid_ranks,valid_cards)}

#map integers to a specific suite value
#probably could also be a dictionary but whatever
class Suits(IntEnum): #Clubs, Hearts, Diamonds, Spades
    C = 0
    H = 1
    D = 2
    S = 3
#cards have a rank (3 to Ace) and a suit (clubs to spades)
#cards are ordered first by their rank, and then by their suit
class Card:
    def __init__(self,rank,suit):
        assert rank in valid_ranks
        self.rank = rank
        self.suit = Suits(suit)
    def __add__ (self,other):
        return Card((self.rank+other)%13,self.suit.value)
    def __hash__(self):
        return hash(self.rank)
    def __eq__ (self,other):
        return (self.rank==other.rank)
    #cards are unique, so no two cards can ever be 'equal', but we only care about rank equality and making the cards hashable
    def __lt__(self,other):
        if (self.rank < other.rank):
            return (True)
        elif (self.rank == other.rank):
            if(self.suit.value<other.suit.value):
                return True
            else:
                return False
        else:
            return False
    def __gt__(self,other):
        if (self.rank > other.rank):
            return (True)
        elif (self.rank == other.rank):
            if(self.suit.value>other.suit.value):
                return True
            else:
                return False
        else:
            return False

    def __str__ (self):
        return "{}{}".format(value_rules[self.rank],self.suit.name)
    def __repr__(self):
        return "{}{}".format(value_rules[self.rank],self.suit.name)
    #look up less stupid way of making the output prettier

#decks consist of 52 unique cards, decks can shuffle themselves and deal out cards to players
class Deck:
    def __init__(self):
        self.cards = []
        for suit in Suits:
            for rank in valid_ranks:
                self.cards.append(Card(rank,suit))
    def __str__(self):
        s = "Cards in Deck: "
        for card in d.cards:
            s+= str(card) + ' '
        return s
    def shuffle(self):
        shuffle(self.cards)
    def dealCard(self):
        return self.cards.pop()
    def dealHand(self, amount): #returns # sized list of cards from top of deck
        hand = []
        for x in range(amount):
            hand.append(self.dealCard())
        return hand

#generates a powerset of a given iterable object
def powerset(iterable):
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    #low priority: look for cleaner way to do this

#return if the cards form a poker hand as a true/false
def checkPokerHand(cards):
    if (len(cards)==0): #empty set = playing nothing so obviously invalid
        return False
    reps = dict(Counter(cards))
    if(len(cards) == max([i for i in reps.values()]) and len(cards)<5): #checks for up to 4 of a kind
        return True
    else:
        return False
    #implement straight and full house check (sequential increase and has repetition of 3 and 2)    

d = Deck()
d.shuffle()
h = d.dealHand(13)
h.sort(reverse=False)
print(h)
sets = powerset(h)
l = list(sets)
good = []
for play in l:
    if(checkPokerHand(play)):
        good.append(play)
for play in good:
    print(play)
