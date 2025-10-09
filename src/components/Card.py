from enum import Enum
#enums
class Suit(Enum):
  Hearts = 0,
  Clubs = 1,
  Spades = 2,
  Diamonds = 3
  
class Rank(Enum):
  Two = 0,
  Three = 1,
  Four = 2,
  Five = 3,
  Six = 4,
  Seven = 5,
  Eight = 6,
  Nine = 7,
  Ten = 8,
  Jack = 9,
  Queen = 10
  King = 11,
  Ace = 12

#main class
class Card:
  suit: Suit
  rank: Rank
  def __init__(self, suit, rank):
    self.suit = suit
    self.rank = rank
    
  def printCard(self) -> None:
    print(self.rank.name, "of", self.suit.name)

class NoCard(Card):
  def __init__(self):
    super().__init__(Suit.Clubs, Rank.Ace)
    
suits = list(Suit)
ranks = list(Rank)