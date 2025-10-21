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
  def __init__(self, name: str, shuffleMethod: list[ShuffleMethod], initialChips: int):
    self.name = name
    self.methods = shuffleMethod
    self.chips = initialChips
    self.bet = Bet.Null
    self.cardOne: Card = NoCard()
    self.cardTwo: Card = NoCard()
    self.name: str
    self.methods: list[ShuffleMethod]
    self.chips: int
    self.bet: Bet
    self.isAllIn: bool = False
    self.eligiblePoolIndices: list[int] = []
    self.handRating: float = 0
    self.alreadyCalledBluff: bool = False
    self.ranking: HandRankings = HandRankings.HighCard
  
  def receiveCard(self, card: Card) -> None:
    if(type(self.cardOne) == NoCard):
      self.cardOne = card
    else: 
      self.cardTwo = card
      
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

  def addIndexToEligiblePools(self, index: int) -> None:
    self.eligiblePoolIndices.append(index)
  
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
      return 15
    elif handRanking == HandRankings.TwoPair:
      return 25
    elif handRanking == HandRankings.ThreeOfAKind:
      return 40
    elif handRanking == HandRankings.Straight:
      return 60 + cardBoost
    elif handRanking == HandRankings.Flush:
      return 70 + cardBoost
    elif handRanking == HandRankings.FullHouse:
      return 80
    elif handRanking == HandRankings.FourOfAKind:
      return 98
    elif handRanking == HandRankings.StraightFlush:
      return 99
    elif handRanking == HandRankings.RoyalFlush:
      return 100.0
    
  #presupposes that both cards are given at this point
  def getRankOfCards(self, cardList: list[Card]) -> list:
    allList = cardList
    
    handRanks: list[int] = []
    for card in allList:
      handRanks.append(ranks.index(card.rank))
    #sort handRanks in descending order
    handRanks.sort(reverse=True)
    
    handSuits: list[int] = []
    for card in allList:
      handSuits.append(suits.index(card.suit))
    handSuits.sort()
    
    ranking = HandRankings.HighCard
    
    rankSet = set(handRanks)
    rankSetLength = len(rankSet)

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
          
      if len(uniquePairs) >= 3:
        run = 0
        maxRun = 1
        prevPair = uniquePairs[0]
        for pair in uniquePairs:
          if(pair == prevPair):
            run += 1
            if(run > maxRun):
              maxRun = run
          else:
            run = 0
          prevPair = pair
                  
        ranking = HandRankings.TwoPair
        if(maxRun == 2):
          ranking = HandRankings.FullHouse
        elif(maxRun == 3):
          ranking = HandRankings.FourOfAKind

    #check flushes
    run = 0
    maxRun = 1
    prevSuit = list(handSuits)[0]
    for suit in list(handSuits):
      if(suit == prevSuit):
        run += 1
        if(run > maxRun):
          maxRun = run
          if(maxRun > 4):
            break
      else:
        run = 0
        prevSuit = suit
    if(maxRun > 4):
      ranking = HandRankings.Flush
      
    #check straights
    run = 0
    maxRun = 1
    starter = list(handRanks)[0]
    prevRank = list(handRanks)[0]
    for rank in list(handRanks):
      if(rank == prevRank + 1):
        run += 1
        if(run > maxRun):
          maxRun = run 
          if(maxRun > 4):
            break
      else:
        run = 0
        starter = rank
      prevRank = rank

    if(maxRun > 4):
      if ranking == HandRankings.Flush:
        ranking = HandRankings.StraightFlush
      else:
        ranking = HandRankings.Straight
    
    #check royal flush
    if ranking == HandRankings.StraightFlush and starter == 12:
      ranking = HandRankings.RoyalFlush
    
    #return the hand ranking
    return [ranking, handRanks, uniquePairs]
  
  def getHandRank(self, results: list[Card]) -> HandRankings:
    handRankDetails = self.getRankOfCards(results + [self.cardOne, self.cardTwo])
    handRanking = handRankDetails[0]
    handRanks = handRankDetails[1]
    pairs = handRankDetails[2]
    handRating = self.rankingToRating(handRanks, handRanking, pairs)
    
    if(len(results) > 0):
      baseRankDetails = self.getRankOfCards(results)
      baseRanking = baseRankDetails[0]
      baseRanks = baseRankDetails[1]
      basePairs = baseRankDetails[2]
      baseRating = self.rankingToRating(baseRanks, baseRanking, basePairs)
      
      self.handRating = handRating - baseRating
    else:
      self.handRating = handRating
    
    self.ranking = handRanking
    return handRanking
 
  
  def loseChips(self, amount: int) -> int:
    self.chips -= amount
    return amount
  
  def winChips(self, amount: int) -> int:
    self.chips += amount
    print(f"{self.name} wins {amount} chips. Total chips: {self.chips}")
    return amount
  
  def payBlind(self, amount: int) -> None:
    if(amount == 5):
      self.loseChips(5)
      print(f"{self.name} pays the small blind price of 5 chips. {self.reportChips()}")
    else:
      self.loseChips(10)
      print(f"{self.name} pays the big blind price of 10 chips. {self.reportChips()}")
  
  def doRaise(self, amount: int) -> int:
    self.bet = Bet.Raise
    amount = min(self.chips, amount)
    print(f"{self.name} raises the prize pool by {str(amount)} chips.")
    return self.loseChips(amount)
      
  def doCall(self, amount: int) -> int:
    if(amount > self.chips):
      return self.doFold()
    else:
      self.bet = Bet.Call
      print(f"{self.name} calls in, paying {str(amount)} chips.")
      return self.loseChips(amount)
  
  def doCheck(self) -> int:
    self.bet = Bet.Check
    print(f"{self.name} checks. {self.reportChips()}")
    return 0
    
  def doFold(self) -> int:
    self.bet = Bet.Fold
    print(f"{self.name} folds. {self.reportChips()}")
    return 0
  
  def goAllIn(self) -> int:
    self.bet = Bet.AllIn
    self.isAllIn = True
    print(f"{self.name} is going all in, paying {str(self.chips)} chips!")
    self.printHand()
    return self.loseChips(self.chips)
  
  def reportChips(self) -> str:
    return f"Chips left: {self.chips}"
  
  def randDecision(self, probability: float, betOne: Bet, betTwo: Bet) -> Bet:
    if(random.random() < probability):
      return betOne
    return betTwo
  #poolIncrease: how much the pool has increased by in the round
  #someoneAllIn: if someone has all inned in the current round
  
  def runRegularLogic(self, minBet: int):
    raiseAmount = 0
    if(self.handRating > 25):
      if self.chips > 50:
        #great hand
        decision = Bet.Raise
        raiseAmount = 20
      else:
        decision = Bet.StayIn
    elif minBet > self.chips / 5:
      if minBet > self.chips / 3:
        decision = self.randDecision(0.3, Bet.StayIn, Bet.Fold)
      else:
        if self.handRating > 20:
          decision = self.randDecision(0.9, Bet.StayIn, Bet.Fold)
        else:
          decision = self.randDecision(0.7, Bet.StayIn, Bet.Fold)
    else:
      decision = Bet.StayIn
    return [decision, raiseAmount]
    
  def decideAction(self, minBet: int, someoneAllIn: bool, bettingRound: int, playersLeft: int) -> int:
    enoughChips = False
    if not self.isAllIn:
      if(minBet > self.chips):
        print(f"Player {self.name} does not have enough chips to stay in the round.")
        return self.doFold()
      else:
        enoughChips = True
        decision = Bet.Null
        raiseAmount = 0
        #the player always has enough chips to play in here
        if(bettingRound == 1):
          if(self.handRating > 10):
            if self.chips > 40:
              #raise cuz hand is good
              decision = self.randDecision(0.8, Bet.Raise, Bet.StayIn)
              raiseAmount = 10
            else:
              if(minBet > self.chips / 3):
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
            if(minBet > 20 or minBet > self.chips / 3):
              decision = self.randDecision(0.1, Bet.StayIn, Bet.Fold)
            #stay in
            decision = self.randDecision(0.7, Bet.StayIn, Bet.Fold)
        elif(bettingRound > 1): #2, 3, or 4
          #bluff chance decreases as rounds go on
          bluffChance = 15 + (bettingRound-2) * 5
          if(self.handRating > 40):
            #extremely good hand so play a lot of chips
            #go all in to punish those who think it's a bluff
            decision = self.randDecision(0.6 + (bettingRound - 2)*0.1, Bet.AllIn, Bet.StayIn)
          else:
            #bluffing, only bluff if low on chips because you need to take a risky chance
            if(random.randint(1, bluffChance) and not someoneAllIn and self.chips < 20):
              decision = Bet.AllIn
            else:
              #calling a bluff  
              if(someoneAllIn and not self.alreadyCalledBluff):
                #chance to call a buff should be proportional to how good the current hand is
                if(random.randint(1,100) < self.handRating * 2):
                  #most likely fold because we didn't call the bluff
                  decision = self.randDecision(0.2, Bet.StayIn, Bet.Fold)
                  self.alreadyCalledBluff = True #in case we stayed in still
                else: #we called the bluff, so run regular logic.
                  self.alreadyCalledBluff = True
                  results = self.runRegularLogic(minBet)
                  decision = results[0]
                  raiseAmount = results[1]
              else:
                results = self.runRegularLogic(minBet)
                decision = results[0]
                raiseAmount = results[1]
        if decision == Bet.Fold:
          print(f"Player {self.name} has decided to fold.")
          if(enoughChips and playersLeft == 1):
            if(minBet == 0):
              return self.doCheck()
            else:
              return self.doCall(minBet)
          return self.doFold()
        
        else:
          if decision == Bet.Raise:
            return self.doRaise(raiseAmount)
          elif decision == Bet.StayIn:
            if(minBet == 0):
              return self.doCheck()
            else:
              return self.doCall(minBet)
          elif decision == Bet.AllIn:
            return self.goAllIn()
          else:
            raise Exception("Decision logic failed.")
          
    else: #you are all in, you can't bet
      print("Player " + self.name + " is all in and cannot make a decision.")
      return -1 #you can't bet

  def toString(self) -> str:
    return self.name
  
  def reset(self) -> None:
    self.isAllIn = False
    self.eligiblePoolIndices = []
    self.handRating = 0
    self.alreadyCalledBluff = False
    self.ranking = HandRankings.HighCard