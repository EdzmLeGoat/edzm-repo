import random 
from enum import Enum
import math
from typing import Optional

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

class ShuffleMethod(Enum):
  Riffle = 0,
  Cut = 1,
  Pharaoh = 2,
  Mover = 3

class Bet(Enum):
  Call = 0,
  Raise = 1,
  Fold = 2,
  Check = 3,
  AllIn = 4,
  StayIn = 5,
  Null = 6
  
class HandRankings(Enum):
  HighCard = 0,
  Pair = 1,
  TwoPair = 2,
  ThreeOfAKind = 3,
  Straight = 4,
  Flush = 5,
  FullHouse = 6,
  FourOfAKind = 7,
  StraightFlush = 8,
  RoyalFlush = 9
  
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
initialChips = 60

class Pool:
  chips: int = 0
  increase: int = 0
  def __init__(self):
    self.chips = 0
    self.increase = 0
  
  def addChips(self, amount: int) -> None:
    self.chips += amount
    self.increase += amount
    print(f"Added {amount} chips to the pool. Current total: {self.chips}")
  #called at the end of each betting round
  def resetIncrease(self) -> None:
    self.increase = 0

class Player:
  
  #init method
  cardOne: Card = NoCard()
  cardTwo: Card = NoCard()
  name: str
  method: ShuffleMethod
  chips: int
  bet: Bet
  hasBigBlind: bool = False
  hasSmallBlind: bool = False
  isDealer: bool = False
  isAllIn: bool = False
  eligiblePools: list[Pool] = []
  handRating: int = 0
  def __init__(self, name: str, shuffleMethod: ShuffleMethod, initialChips: int = initialChips):
    self.name = name
    self.method = shuffleMethod
    self.chips = initialChips
    self.bet = Bet.Null
  
  def receiveCard(self, card: Card) -> None:
    if(self.cardOne != None):
      self.cardTwo = card
    else: 
      self.cardOne = card
      
  #presupposes that both cards are given at this point
  def forfeitCards(self) -> list[Card]:
    cards = [self.cardOne, self.cardTwo]
    self.cardOne = NoCard()
    self.cardTwo = NoCard()
    return cards
  
  def printHand(self) -> None:
    print("Card One: ", end="")
    self.cardOne.printCard()
    print("Card Two: ", end="")
    self.cardTwo.printCard()
  
  #returns a float from 0-100 rating how likely the hand is to win
  def rankingToRating(self, handRanks: list[int], handRanking: HandRankings, pairs: list[int]) -> float:
    # handRanks is sorted from highest to lowest card so 0
    # will always be the highest card.
    # ranks of the cards is 0-12
    # the rank of the card will play a small role in the rating
    cardBoost = handRanks[0] * 5/12
    
    #pairs is already sorted by highest rank
    if handRanking == HandRankings.HighCard:
      return cardBoost
    elif handRanking == HandRankings.Pair:
      return 10 + cardBoost
    elif handRanking == HandRankings.TwoPair:
      return 25 + pairs[0] * 5/12 + pairs[1] * 5/12
    elif handRanking == HandRankings.ThreeOfAKind:
      return 40 + pairs[0] * 5/12
    elif handRanking == HandRankings.Straight:
      return 95 + cardBoost
    else:
      #hand is so good at this point nothing is gonna beat it
      return 100
    
  #presupposes that both cards are given at this point
  def getRank(self, results: list[Card] = []) -> HandRankings:
    card1 = self.cardOne
    card2 = self.cardTwo
    allList = [card1, card2] + results
    
    handRanks: list[int] = []
    for card in allList:
      handRanks.append(ranks.index(card.rank))
    #sort handRanks in descending order
    handRanks.sort(reverse=True)
    
    handSuits: list[int] = []
    for card in allList:
      handSuits.append(suits.index(card.suit))
    
    ranking = HandRankings.HighCard
    
    rankSet = set(handRanks)
    rankSetLength = len(rankSet)
    suitSet = set(handSuits)
    suitSetLength = len(suitSet)
    numCards = len(allList)
    
    uniquePairs = []
    
    #check pairs / of a kind / full house
    if(rankSetLength < numCards):
      #assume pair for now
      for i in range(len(handRanks) - 1):
        if(handRanks[i] == handRanks[i+1]):
          uniquePairs.append(handRanks[i])
      ranking = HandRankings.Pair
          
      if len(uniquePairs) == 2:
        if(uniquePairs[0] == uniquePairs[1]):
          ranking = HandRankings.ThreeOfAKind
        else:
          ranking = HandRankings.TwoPair
      if len(uniquePairs) == 3:
        if(uniquePairs[0] == uniquePairs[1] == uniquePairs[2]):
          ranking = HandRankings.FourOfAKind
        else:
          ranking = HandRankings.FullHouse
        
    #check flushes
    if suitSetLength == 1 & numCards == 5:
      #since sets remove duplicates
      ranking = HandRankings.Flush
      
    #check straights
    straight = True
    for i in range(len(handRanks) - 1):
      if(handRanks[i] + 1 != handRanks[i+1]):
        straight = False
        break
    
    if straight:
      if ranking == HandRankings.Flush:
        ranking = HandRankings.StraightFlush
      else:
        ranking = HandRankings.Straight
    
    #check royal flush
    if ranking == HandRankings.StraightFlush and handRanks[0] == 12:
      ranking = HandRankings.RoyalFlush
    
    self.handRating = int(self.rankingToRating(handRanks, ranking, uniquePairs))
    #return the hand ranking
    return ranking
  
  def loseChips(self, amount: int) -> int:
    self.chips -= amount
    return amount
  
  def winChips(self, amount: int) -> int:
    self.chips += amount
    return amount
  
  def doRaise(self, amount: int) -> int:
    self.bet = Bet.Raise
    amount = min(self.chips, amount)
    print(f"{self.name} raises the prize pool by {str(amount)} chips. {self.reportChips()}")
    return self.loseChips(amount)
      
  def doCall(self, amount: int) -> int:
    if(amount > self.chips):
      return self.doFold()
    else:
      self.bet = Bet.Call
      print(f"{self.name} calls in, paying {str(amount)} chips. {self.reportChips()}")
      return self.loseChips(amount)
  
  def doCheck(self) -> int:
    self.bet = Bet.Check
    print(f"{self.name} checks. {self.reportChips()}")
    return 0
    
  def doFold(self) -> int:
    self.bet = Bet.Fold
    print(f"{self.name} folds. {self.reportChips()}")
    return -1
  
  def goAllIn(self) -> int:
    self.bet = Bet.AllIn
    self.isAllIn = True
    print(f"{self.name} is going all in, paying {str(self.chips)} chips! {self.reportChips()}")
    return self.loseChips(self.chips)
  
  def reportChips(self) -> str:
    return f"Chips left: {self.chips}"
  #poolIncrease: how much the pool has increased by in the round
  #someoneAllIn: if someone has all inned in the current round
  def decideAction(self, poolIncrease: int, someoneAllIn: bool, bettingRound: int) -> int:
    if not self.isAllIn:
      if(poolIncrease > self.chips):
        print(f"Player {self.name} does not have enough chips to stay in the round.")
        return self.doFold()
      else:
        decision = Bet.Fold
        raiseAmount = 0
        #the player always has enough chips to play in here
        if(bettingRound == 1):
          if(self.handRating > 10):
            if self.chips > 40:
              #raise cuz hand is good
              decision = Bet.Raise
              raiseAmount = 10
            else:
              decision = Bet.StayIn
          elif(self.handRating > 4):
            if self.chips > 40:
              #raise a bit
              decision = Bet.Raise
              raiseAmount = 5
            else:
              decision = Bet.StayIn
          else:
            #if the amount to stay in is too high leave
            if(poolIncrease > 20 or poolIncrease > self.chips / 4):
              decision = Bet.Fold
            #stay in
            decision = Bet.StayIn
        elif(bettingRound > 1): #2, 3, or 4
          bluffCaller = 25 + (bettingRound-2) * 5
          bluffChance = 15 + (bettingRound-2) * 5
          if(self.handRating > 40):
            #extremely good hand so play a lot of chips
            #go all in to punish those who think it's a bluff
            decision = Bet.AllIn
          else:
            #bluffing, only bluff if low on chips because you need to take a risky chance
            if(random.randint(1,bluffChance) and not someoneAllIn and self.chips < 20):
              decision = Bet.AllIn
            else:
              #calling a bluff  
              if(someoneAllIn):
                #chance to call a buff should be proportional to how good the current hand is
                if(self.handRating < bluffCaller and not random.randint(1,100) < self.handRating * 3):
                  #fold because we didn't call the bluff
                  decision = Bet.Fold
                else: #we called the bluff
                  if(self.handRating > 25):
                    if self.chips > 50:
                      #stay in cause good hand
                      decision = Bet.StayIn
                    else:
                      #if someone is all in, the call cost is gonna be a lot
                      #and it's not worth it if you have less than 50 chips
                      decision = Bet.Fold
              else:
                if(self.handRating > 25):
                  if self.chips > 50:
                    #great hand
                    decision = Bet.Raise
                    raiseAmount = 20
                  else:
                    decision = Bet.StayIn
                elif self.handRating > 15:
                  decision = Bet.StayIn
                else:
                  if poolIncrease < self.chips / 8:
                    #you can afford to stay in
                    decision = Bet.StayIn
                  else:
                    decision = Bet.Fold
            
        if decision == Bet.Fold:
          return self.doFold()
        else:
          if decision == Bet.Raise:
            self.doCall(poolIncrease)
            return self.doRaise(raiseAmount)
          elif decision == Bet.StayIn:
            if(poolIncrease == 0):
              return self.doCheck()
            else:
              return self.doCall(poolIncrease)
          elif decision == Bet.AllIn:
            self.doCall(poolIncrease)
            return self.goAllIn()
    else: #you are all in, you can't bet
      return -1 #you can't bet
    return 0
      
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
  def riffleShuffleList(self, list: list[Card], evenness: float) -> list[Card]:
    midList = len(list) // 2
    cutIndex = random.randint(midList - 2, midList + 2) # Cut near the middle
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
  def riffleShuffle(self, riffles, evenness: float = 0.5) -> None:
    for _ in range(riffles):
      self.cards = self.riffleShuffleList(self.cards, evenness)
  def deal(self, dealerIndex: int):
    for _ in range(2):
      for i in range(len(self.players)):
        #needs to go counterclockwise from the dealer
        dealingIndex = (dealerIndex + i) % len(self.players)
        if(dealingIndex < 0):
          dealingIndex += len(self.players)
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
    self.discarded = self.riffleShuffleList(self.discarded, 0.3)
    self.cards.extend(self.discarded)
    self.discarded = []
    self.results = []

  def shuffle(self, method: ShuffleMethod) -> None:
    if method == ShuffleMethod.Riffle:
      self.riffleShuffle(2, 0.9)
    elif method == ShuffleMethod.Cut:
      self.cutShuffle(3)
    elif method == ShuffleMethod.Mover:
      self.moverShuffle(5)
    elif method == ShuffleMethod.Pharaoh:
      #a pharaoh shuffle is just a more accurate riffle shuffle
      self.riffleShuffle(2, 0.98)   
  
class Game:
  players: list[Player]
  decks: list[Deck]
  preDealerIndex: int = 0
  dealerIndex: int = 1
  smallBlindIndex: int = 2
  bigBlindIndex: int = 3
  trial: int = 1
  
  #requires 3 people to start
  def __init__(self, players):
    if(len(players) < 4):
      raise ValueError("Must have at least 4 players.")
    self.players = players
    self.decks = [Deck(players), Deck(players)]
    self.players[self.smallBlindIndex].hasSmallBlind = True
    self.players[self.bigBlindIndex].hasBigBlind = True
    self.decks[0].shuffle(self.players[self.dealerIndex])

  def checkPlayerOut(self, playerIndices: list[int]) -> None:
    for index in playerIndices:
      if(self.players[index].chips <= 0):
        print("Player " + self.players[index].name + " is out of chips.")
        print("Players left: " + str(len(self.players)) + ".")
        if(len(self.players) == 1):
          print("Game over. " + self.players[0].name + " wins!")    

  def playRound(self):
    pools: list[Pool] = []
    pools.append(Pool())
    pools[0].addChips(self.players[self.bigBlindIndex].loseChips(10))
    pools[0].addChips(self.players[self.smallBlindIndex].loseChips(5)) 
    self.checkPlayerOut([self.smallBlindIndex, self.bigBlindIndex])
    
    #deal cards
    self.decks[self.trial % 2].shuffle(self.players[self.preDealerIndex].method)
    self.decks[(self.trial + 1) % 2].deal(self.dealerIndex)
    
    someoneAllIn = False
    #first bet
    poolIncrease = 0
    for player in self.players:
      player.getRank()
      rating = player.handRating
      bet = player.decideAction(poolIncrease, someoneAllIn, 1)
      
      
    #3 revealed
    #second bet
    #4 revealed
    #third bet
    #final card revealed
    #last bet
    #winner decided
    #players recycle discarded cards
    self.round += 1

  
p1 = Player("Mr. Kirk", ShuffleMethod.Pharaoh)
p2 = Player("Edem", ShuffleMethod.Riffle)
p3 = Player("Justin", ShuffleMethod.Cut)
p4 = Player("Mr. Sahu", ShuffleMethod.Pharaoh)
p5 = Player("minecraft", ShuffleMethod.Riffle)
p6 = Player("pokemon", ShuffleMethod.Cut)
game = Game([p1, p2, p3, p4, p5, p6])