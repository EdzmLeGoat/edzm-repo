#imports
from enum import Enum
import math, random
from components.Player import Player, ShuffleMethod
from components.Card import Card, suits, ranks
class Deck:
  players: list[Player]
  cards: list[Card]
  discarded: list[Card]
  results: list[Card]
  playerNames: list[str]
  def __init__(self, players: list[Player]):
    self.players = players
    self.cards = []
    self.discarded = []
    self.results = []
    self.playerNames = []
    for player in players:
      self.playerNames.append(player.name)
    for i in range(4):
      for j in range(13):
        suit = suits[i]
        rank = ranks[j]
        self.cards.append(Card(suit, rank))
        
  def printDeck(self) -> None:
    index = 1;
    for card in self.cards:
      print(str(index) + ": ", end="")
      card.printCard()
      index += 1
    print("")
  
  @staticmethod
  def _print_any_deck(list: list[Card]) -> None:
    index = 1;
    for card in list:
      print(str(index) + ":", card.rank.name, "of", card.suit.name)
      index += 1
    print("\n\n")
  def cutShuffle(self, cuts: int) -> None:
    for _ in range(cuts):   
      # should be around the middle of the deck
      cutIndex = random.randint(22, 30)
      # sometimes it isn't, so on the off chance:
      if(random.randint(0, 5) == 0):
        cutIndex = random.randint(0, 52)
      
      partOne = self.cards[:cutIndex]
      partTwo = self.cards[cutIndex:]
      self.cards = partTwo + partOne
    
  def moverShuffle(self, moves: int) -> None:
    #selects a bunch of cards from the middle to move to the end
    for _ in range(moves):
      firstIndex = random.randint(10, 42)
      secondIndex = random.randint(firstIndex + 1, 52)
      self.cards = self.cards[:firstIndex] + self.cards[secondIndex:] +  self.cards[secondIndex:firstIndex]
  def riffleShuffleList(self, list: list[Card], evenness: float, sliceEvenness) -> list[Card]:
    midList = len(list) // 2
    cutIndex = random.randint(midList - sliceEvenness, midList + sliceEvenness) # Cut near the middle
    deck1 = list[:cutIndex]
    deck2 = list[cutIndex:]
    decks = [deck1, deck2]
    lastDeck = 0
    shuffled_deck = []
    while len(deck1) > 0 and len(deck2) > 0:
      # Choose which deck to draw from based on the last roll and the evenness
      if random.random() <= evenness:
        shuffled_deck.append(decks[(lastDeck + 1) % 2].pop(0)) 
      else:
        shuffled_deck.append(decks[lastDeck].pop(0)) 
      lastDeck = (lastDeck + 1) % 2
        
    shuffled_deck.extend(deck1)
    shuffled_deck.extend(deck2)
    return shuffled_deck
  def riffleShuffle(self, riffles, evenness: float, sliceEvenness: int) -> None:
    for _ in range(riffles):
      self.cards = self.riffleShuffleList(self.cards, evenness, sliceEvenness)
  def deal(self, dealerIndex: int):
    for _ in range(2):
      for i in range(len(self.players)):
        #needs to go counterclockwise from the dealer
        dealingIndex = (dealerIndex + i) % len(self.players)
        player = self.players[dealingIndex]
        player.receiveCard(self.cards.pop(0))
    
    for player in self.players:
      print("Player " + player.name + ":")
      player.printHand() 
      
  def revealThree(self) -> None:
    self.discarded.append(self.cards.pop(0))
    for _ in range(3):
      self.results.append(self.cards.pop(0))
    
    print("Revealed Cards:")
    for i in range(3):
      self.results[i].printCard()
      
  def revealNext(self) -> None:
    self.discarded.append(self.cards.pop(0))
    self.results.append(self.cards.pop(0))
    print("Revealed Card:")
    self.results[-1].printCard()
    
  def getRanks(self) -> None:
    playerRanks = []
    for player in self.players:
      playerRanks.append(player.getRank(self.results))
    mostIndex = []
    highestRank = 0
    for i in range(len(playerRanks)):
      if playerRanks[i] >= highestRank:
        mostIndex = [i]
        highestRank = playerRanks[i]
      elif playerRanks[i] == highestRank:
        mostIndex.append(i)
        
    if len(mostIndex) == 1:
      print("Player " + self.playerNames[mostIndex[0]] + " won the game with a hand of ", end="")
      self.players[mostIndex[0]].printHand()
    else:
      print("Players," + ", ".join(self.playerNames[i] for i in mostIndex) + " tied with a hand of: ", end="")
      for player in self.players:
        print(player.name + ":")
        player.printHand()
    
  def recycleDiscardedCards(self) -> None:
    #random throwing in of decks
    allDiscardedHands = []
    for player in self.players:
      allDiscardedHands.append(player.forfeitCards())
    while len(allDiscardedHands) > 0:
      thrower = random.randint(0, len(allDiscardedHands) - 1)
      self.discarded.extend(allDiscardedHands[thrower])
      
    #want less evenness here because discarded cards are more likely to be in clumps
    self.discarded = self.riffleShuffleList(self.discarded, 0.3, 0)
    self.cards.extend(self.discarded)
    self.discarded = []
    self.results = []

  def shuffle(self, methods: list[ShuffleMethod]) -> None:
    for method in methods:
      if method == ShuffleMethod.Riffle:
        self.riffleShuffle(2, 0.9, 4)
      elif method == ShuffleMethod.Cut:
        self.cutShuffle(3)
      elif method == ShuffleMethod.Mover:
        self.moverShuffle(5)
      elif method == ShuffleMethod.Pharaoh:
        #a pharaoh shuffle is just a more accurate riffle shuffle
        self.riffleShuffle(2, 0.98, 2)   
  