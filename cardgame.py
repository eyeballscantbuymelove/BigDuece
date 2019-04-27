#!/usr/bin/python3

from enum import IntEnum
from random import shuffle
from collections import Counter
from itertools import chain, combinations, filterfalse
import time

# create a dictionary to map a cards number to its rank
valid_ranks = list(range(13))
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
    cards have a rank (0 to 12: 3 to Ace) and a suit (0 to 3: clubs to spades)
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

    def __int__(self):
        return self.rank*4+self.suit.value
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
    def reclaimCard(self,card):
        assert isinstance(card,Card)
        self.cards.append(card)
    def reclaimCards(self,cards):
        for card in cards:
            assert isinstance(card,Card)
            self.cards.append(card)

class Player:
    ''' players of card games have at least one hand of cards, have a unique id, and occupy a position in the state, and a history of cards played'''
    def __init__(self,hand = [],id = -1):
        assert(isinstance(hand,list))
        self.hand=hand
        self.id=id
        self.position = -1
        self.history = []
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return str(self.hand)
    def takeCards(self,cards,sort=True):
        '''takes a list of cards, adds to them to the hand, (default sorted), returns the hand'''
        assert isinstance(cards,list)
        for card in cards:
            self.hand.append(card)
        if(sort):
            self.hand.sort()
        return self.hand
    def playCards(self,indexes):
        '''takes a list indexes, removes cards at those hand indexes, and returns them in a list'''
        assert isinstance(indexes,list)
        play = []
        for index in indexes:
            play.append(self.hand.pop(index))
        self.hand.sort()
        self.history.extend(play)
        return play

    ''' players have two notable states
        the full state, visible to only the players
        the visible state, known to anybody observing the game'''
    def getFullState(self):
        self.hand.sort(reverse=True)
        state=list(map(int,p1.hand))
        while (len(state)<13):
            state.append(-1)
        state.extend([self.id,self.position])
        state.extend(self.history)
        return state
    def getVisibleState(self):
        return [self.id,self.position].extend(self.history)




# XXX: from https://docs.python.org/3/library/itertools.html
def powerset(iterable, n=6):
    '''generates members of the powerset of a given iterable object up to cardinality n, default size is size of poker hand'''
    #low priority TODO: look for cleaner way to do this
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(6)))

def checkPokerHand2(cards):
    '''return value of poker hand as an int
        0=invalid, 1=high card, 2=pair, 3=set, 4=straight, 5=fullhouse, 6 = quads'''
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

class Big2State:
    ''' the state of a generic card game can be defined by
        the players: the list of players who can alter the state
        the board: the list of cards currently viewable by players
        the stack: the list cards which have been played, but are not viewable by players
        the turn: an integer number representing which player may act on the State
        the round: the number of times a full set of turns has been completed
        additionally, a big two state needs to keep track of the following
        the trick: the currently allowed set of plays in the round, represented as an integer
            0=wild, 1=high card, 2=pair, 3=set, 4=straight, 5=fullhouse, 6 = quads
        players still able to compete for the trick
        the win state: a boolean--does the current turn's player have no cards in their hand at the end of the turn, signifying a win'''
    def __init__(self,players,board=[]):
        assert len(players)==4
        self.players = players
        self.board = board
        self.stack = []
        self.turn = 0
        self.round = 0
        self.trick = 0
        self.competitors = self.players
        self.winstate = False

    def checkWinstate(self,player):
        return player.hand==[]
    def checkValidPlay(self,cards):
        ''' check if a set of cards matches is a valid poker hand and matches the current trick
            checkPokerHand supports checking for only a single category of tricks
            low priority, adjust logic for more efficient checking of sets rather than checking all hands'''
        play_type = checkPokerHand2(cards)
        if (self.trick==0) or (play_type == self.trick) or (play_type == 6):
            '''quats are always bombs'''
            return True
        else:
            return False
    #todo, advance game state


class Game:
    ''' a generic card game consists of decks of cards and players, who sit in a fixed position and act on one or more states'''
    def __init__(self,decks,players,state):
        for deck in decks:
            assert isinstance(Deck)
        for player in players:
            assert isinstance(Player)
        assert isinstance(state,State)
        self.decks=decks
        self.players=players
        self.state=state



if __name__ == '__main__':
    start = time. time()
    d = Deck()
    d.shuffle()
    p1 = Player(id=1)
    p1.takeCards(d.dealHand(13))
    print(p1)
    print(p1.getFullState())
    sets = powerset(p1.hand)
    good = []
    for play in sets:
        if(checkPokerHand2(play)):
            good.append(play)
    d.reset()
    for play in good:
        print(play)
    end = time. time()
    print(end - start)
    print(Card(0,1))
    print(int(Card(0,1)))
