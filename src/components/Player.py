#imports
from enum import Enum
import random 
import math
from components.Card import Card, NoCard, ranks, suits
from components.Pool import Pool
#enums
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
  
#main class
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
  def __init__(self, name: str, shuffleMethod: ShuffleMethod, initialChips: int):
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
  
  def randDecision(self, probability: float, betOne: Bet, betTwo: Bet) -> Bet:
    if(random.random() < probability):
      return betOne
    return betTwo
  #poolIncrease: how much the pool has increased by in the round
  #someoneAllIn: if someone has all inned in the current round
  
  def runRegularLogic(self, poolIncrease: int):
    raiseAmount = 0
    if(self.handRating > 25):
      if self.chips > 50:
        #great hand
        decision = Bet.Raise
        raiseAmount = 20
      else:
        decision = Bet.StayIn
    elif poolIncrease > self.chips / 8:
      if poolIncrease > self.chips / 4:
        if random.random() < 0.2:
          decision = Bet.StayIn
        else:
          decision = Bet.Fold
      else:
        if self.handRating > 20:
          decision = Bet.StayIn
        else:
          decision = Bet.Fold
    else:
      decision = Bet.StayIn
    return [decision, raiseAmount]
    
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
              decision = self.randDecision(0.8, Bet.Raise, Bet.StayIn)
              raiseAmount = 10
            else:
              if(poolIncrease > self.chips / 4):
                decision = self.randDecision(0.2, Bet.StayIn, Bet.Fold)
              else:
                decision = Bet.StayIn
          elif(self.handRating > 4):
            if self.chips > 60:
              #raise a bit
              decision = self.randDecision(0.6, Bet.Raise, Bet.StayIn)
              raiseAmount = 5
            else:
              decision = Bet.StayIn
          else:
            #if the amount to stay in is too high leave
            if(poolIncrease > 20 or poolIncrease > self.chips / 4):
              decision = Bet.Fold
            #stay in
            decision = self.randDecision(0.7, Bet.StayIn, Bet.Fold)
        elif(bettingRound > 1): #2, 3, or 4
          bluffCaller = 25 + (bettingRound-2) * 5
          bluffChance = 15 + (bettingRound-2) * 5
          if(self.handRating > 40):
            #extremely good hand so play a lot of chips
            #go all in to punish those who think it's a bluff
            decision = self.randDecision(0.3 + (bettingRound - 2)*0.1, Bet.AllIn, Bet.StayIn)
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
                else: #we called the bluff, so run regular logic.
                  results = self.runRegularLogic(poolIncrease)
                  decision = results[0]
                  raiseAmount = results[1]
              else:
                results = self.runRegularLogic(poolIncrease)
                decision = results[0]
                raiseAmount = results[1]
            
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
    return 0 #catchall

