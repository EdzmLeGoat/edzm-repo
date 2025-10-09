#imports
import random 
import math
from components.Player import Player
from components.Deck import Deck
from components.Pool import Pool
from components.Player import Bet

#main class
class Game:
  players: list[Player]
  decks: list[Deck]
  preDealerIndex: int = 0
  dealerIndex: int = 1
  smallBlindIndex: int = 2
  bigBlindIndex: int = 3
  trial: int = 0
  
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
    playersOut = []
    for index in playerIndices:
      if(self.players[index].chips <= 0):
        print("Player " + self.players[index].name + " is out of chips.")
        print("Players left: " + str(len(self.players)) + ".")
        playersOut.append(index)
        if(len(self.players) == 1):
          print("Game over. " + self.players[0].name + " wins!")    
    for index in playersOut:
      self.players.pop(index)
  
  def checkAllPlayerOut(self) -> None:
    indicesOut = []
    for player in self.players:
      if(player.chips <= 0):
        print("Player " + player.name + " is out of chips.")
        print("Players left: " + str(len(self.players)) + ".")
        indicesOut.append(self.players.index(player))
        if(len(self.players) == 1):
          print("Game over. " + self.players[0].name + " wins!")   
    for index in indicesOut:
      self.players.pop(index)

  def handlePlayerRound(self, playersIn: list[Player], pools: list[Pool], poolIndex: int, round: int) -> list[Player]:
    someoneAllIn = False
    #first bet
    poolIncrease = 0
    for player in playersIn:
      player.getRank()
      #if we're not all in
      if(bet != -1):
        bet = player.decideAction(poolIncrease, someoneAllIn, round)
        pools[poolIndex].addChips(bet)
        pools[poolIndex].setIncrease(bet)
      if player.isAllIn:
        someoneAllIn = True
        #since when a player goes all in, they create a new pool that
        #they are not eligible for
        pools.append(Pool())
        poolIndex += 1
        for player in self.players:
          if not player.isAllIn:
            player.eligiblePools.append(pools[poolIndex])
        
    pools[poolIndex].resetIncrease()
    
    for player in playersIn:
      if player.bet == Bet.Fold:
        playersIn.remove(player)
    return playersIn
  
  def decideWinner(self, playersIn: list[Player]) -> None:
    #winner decided
    maxRank = 0.0
    index: list[int] = [0]
    for i in range(len(playersIn)):
      playersIn[i].getRank()
      if playersIn[i].handRating > maxRank:
        maxRank = playersIn[i].handRating
        index = [i]
      elif playersIn[i].handRating == maxRank:
        index.append(i)
    if len(index) == 1:
      player = self.players[index[0]]
      print("Player " + player.name + " won the game with a hand of: ", end="")
      player.printHand()
      print("They won with a ranking of " + str(player.getRank()) + ".")
      for pool in player.eligiblePools:
        player.winChips(pool.chips)
      print("Chips won: " + str(player.chips))
      
      losers: list[int] = []
      for i in range(len(self.players)):
        if not self.players[i] == player:
          losers.append(i)
      self.checkPlayerOut(losers)
  def reset(self, dealingDeckIndex: int) -> None:
    self.players[self.smallBlindIndex].hasSmallBlind = False
    self.players[self.bigBlindIndex].hasBigBlind = False
    self.players[self.dealerIndex].isDealer = False
    
    self.smallBlindIndex = (self.smallBlindIndex + 1) % len(self.players)
    self.bigBlindIndex = (self.bigBlindIndex + 1) % len(self.players)
    self.dealerIndex = (self.dealerIndex + 1) % len(self.players)
    
    self.players[self.smallBlindIndex].hasSmallBlind = True
    self.players[self.bigBlindIndex].hasBigBlind = True
    self.players[self.dealerIndex].isDealer = True
    
    self.decks[dealingDeckIndex].recycleDiscardedCards()
    self.trial += 1
  def playRound(self):
    print("Starting Round " + str(self.trial) + ".")
    
    poolIndex = 0
    pools: list[Pool] = []
    pools.append(Pool())
    pools[poolIndex].addChips(self.players[self.bigBlindIndex].loseChips(10))
    pools[poolIndex].addChips(self.players[self.smallBlindIndex].loseChips(5)) 
    self.checkPlayerOut([self.smallBlindIndex, self.bigBlindIndex])
    
    #set up players
    playersIn = self.players.copy()
    for player in playersIn:
      player.eligiblePools.append(pools[poolIndex])
    
    #deal cards
    shufflingDeckIndex = (self.trial + 1) % 2
    dealingDeckIndex = (self.trial) % 2
    self.decks[shufflingDeckIndex].shuffle(self.players[self.preDealerIndex].method)
    self.players[self.dealerIndex].isDealer = True
    self.decks[dealingDeckIndex].deal(self.dealerIndex)
    
    #first bets
    self.handlePlayerRound(playersIn, pools, poolIndex, 1)
    #3 revealed
    self.decks[dealingDeckIndex].revealThree()
    #second bet
    self.handlePlayerRound(playersIn, pools, poolIndex, 2)
    #4 revealed
    self.decks[dealingDeckIndex].revealNext()
    #third bet
    self.handlePlayerRound(playersIn, pools, poolIndex, 3)
    #final card revealed
    self.decks[dealingDeckIndex].revealNext()
    
    #decide winner
    self.decideWinner(playersIn)
    
    #reset
    self.reset(dealingDeckIndex)
    
  def simulate(self, rounds: int) -> None:
    if rounds == -1:
      condition = True
      onlyPlayer = True
      for player in self.players:
        if(player.chips == 0 and onlyPlayer):
          onlyPlayer = False
        else:
          condition = False
      while not condition:
        self.playRound()
    else:
      for _ in range(rounds):
        self.playRound()