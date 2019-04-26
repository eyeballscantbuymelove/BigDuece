#!/usr/bin/python3

from enum import IntEnum
from random import shuffle
from collections import Counter
from itertools import chain, combinations, filterfalse
from heapq import nlargest
# create a dictionary to map a cards number to its rank
valid_ranks = list(range(0,13))
valid_cards = ['3','4', '5', '6', '7','8', '9','T', 'J', 'Q', 'K','A','2']
value_rules = dict(zip(valid_ranks, valid_cards))

class Suits(IntEnum): #Clubs, Hearts, Diamonds, Spades
    '''
    map integers to a specific suit value
    XXX: probably could also be a dictionary but whatever
    '''
    C = 0
    H = 1
    D = 2
    S = 3

class Card:
    '''
    cards have a rank (3 to Ace) and a suit (clubs to spades)
    cards are ordered first by their rank, and then by their suit
    '''
    def __init__(self,rank,suit):
        assert rank in valid_ranks
        self.rank = rank
        self.suit = Suits(suit)

    def __add__ (self,other):
        return Card((self.rank+other)%13,self.suit.value)

    def __hash__(self):
        return hash(self.rank)

    def __eq__ (self,other):
        '''
        cards are unique, so no two cards can ever be 'equal', but we only
        care about rank equality and making the cards hashable
        '''
        return (self.rank==other.rank)

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
        return repr(self)

    def __repr__(self):
        # TODO: look up less stupid way of making the output prettier
        return "{}{}".format(value_rules[self.rank],self.suit.name)


class Deck:
    '''
    decks consist of 52 unique cards, decks can shuffle themselves and deal
    out cards to players
    '''
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
    def reset(self):
        self.cards = []
        for suit in Suits:
            for rank in valid_ranks:
                self.cards.append(Card(rank,suit))
    def shuffle(self):
        shuffle(self.cards)

    def dealCard(self):
        return self.cards.pop()

    def dealHand(self, amount): #returns # sized list of cards from top of deck
        hand = []
        for x in range(amount):
            hand.append(self.dealCard())
        return hand

# XXX: from https://docs.python.org/3/library/itertools.html
def powerset(iterable):
    '''generates a powerset of a given iterable object'''
    #low priority TODO: look for cleaner way to do this
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))

def checkPokerHand2(cards):
    '''return value of poker hand as an int
        0=invalid, 1=high card, 2=pair, 3=set, 4=straight, 5=fullhouse, 6 = fullhouse'''
    if(len(cards)==0):
        return 0 #emtpy set = playing nothing = obviously invalid
    if(len(cards)==1):
        return 1 #set of size = high card, always a valid sets
    reps=sorted(list(dict(Counter(cards)).values()),reverse=True)
    if(len(cards) < 5 and len(cards)==reps[0]):
        if(len(cards)==4):
            return 6      #quads are highest
        return len(cards) #check for pairs and sets
    if(len(cards)==5 and reps[0]==3 and reps[1]==2):
        return len(cards) #check for full house
    if(len(cards)==5):
        straight_count = 1
        for (indx, card) in enumerate(cards):
            if(card+1==cards[indx+1]):
                straight_count +=1
                if(straight_count==5):
                    return 4 #check for straight
            else:
                return 0

if __name__ == '__main__':
    d = Deck()
    d.shuffle()
    h = d.dealHand(13)
    h.sort(reverse=False)
    sets = powerset(h)
    good = []
    for play in sets:
        if(checkPokerHand2(play)):
            good.append(play)
    d.reset()
    for play in good:
        print(play)
