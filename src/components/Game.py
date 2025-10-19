#imports
from components.Player import Player
from components.Deck import Deck
from components.Pool import Pool
from components.Player import Bet

#main class
class Game:
  players: list[Player]
  decks: list[Deck]
  dealerIndex: int = 1
  trial: int = 0
  shufflingDeckIndex: int = 0
  dealingDeckIndex: int = 1
  
  #requires 3 people to start
  def __init__(self, players: list[Player]):
    if(len(players) < 4):
      raise ValueError("Must have at least 4 players.")
    self.players = players
    self.decks = [Deck(players), Deck(players)]
    self.players[(self.dealerIndex + 1) % len(self.players)].hasSmallBlind = True
    self.players[(self.dealerIndex + 2) % len(self.players)].hasBigBlind = True
    self.decks[self.shufflingDeckIndex].shuffle(self.players[self.dealerIndex].methods)

  def checkPlayerOut(self, players: list[Player]) -> None:
    playersOut = []
    for player in players:
      if(player.chips <= 0):
        playersOut.append(player)
        print("Player " + player.name + " is out of chips.")
        if(len(self.players) == 1):
          print("Game over. " + self.players[0].name + " wins!")    
    for player in playersOut:
      self.players.remove(player)
    print("Players left: " + str(len(self.players)) + ".")

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
      
  def getPlayerFromName(self, name: str) -> Player:
    for player in self.players:
      if player.name == name:
        return player
    raise ValueError("No player with that name found.")

  def handlePlayerRound(self, namesIn: list[str], pools: list[Pool], poolIndex: int, round: int) -> list[str]:
    print("betting round:", + round)
    someoneAllIn = False
    if(round == 1):
      #first round, set min bet to big blind
      pools[poolIndex].setMinBet(10)
    else:
      pools[poolIndex].setMinBet(0)
    
    for name in namesIn:
      player = self.getPlayerFromName(name)
      player.getRank(self.decks[self.dealingDeckIndex].results)
      betAmount = player.decideAction(pools[poolIndex].minBet, someoneAllIn, round, len(namesIn))
      if(betAmount != -1):
        pools[poolIndex].addChips(betAmount, round)
        if player.isAllIn:
          someoneAllIn = True
          #since when a player goes all in, they create a new pool that
          #they are not eligible for
          print("making new pool")
          pools.append(Pool())
          poolIndex += 1
          for player in self.players:
            if not player.isAllIn:
              print("adding eligible player to new pool:", player.name)
              player.addIndexToEligiblePools(poolIndex)
            
      if player.bet == Bet.Fold:
        namesIn.remove(name)
        
      print("")
        
    pools[poolIndex].resetIncrease()
    return namesIn
  
  def decideWinner(self, pools: list[Pool], namesIn: list[str]) -> None:
    #winner decided
    maxRank = 0.0
    names: list[str] = []
    for name in namesIn:
      player = self.getPlayerFromName(name)
      player.getRank(self.decks[self.dealingDeckIndex].results)
      if player.handRating > maxRank:
        maxRank = player.handRating
        names = [name]
      elif player.handRating == maxRank:
        names.append(name)
    if len(names) == 1:
      player = self.getPlayerFromName(names[0])
      print("Player " + player.name + " won the game with a hand of: ")
      player.printHand()
      self.decks[self.dealingDeckIndex].printRevealedCards()
      print("They won with a ranking of " + str(player.getRank(self.decks[self.dealingDeckIndex].results)) + ".")
      print(len(player.eligiblePoolIndices))
      
      for ind in player.eligiblePoolIndices:
        player.winChips(pools[ind].chips)
      
      losers: list[Player] = []
      for p in self.players:
        if p != player:
          losers.append(p)
      self.checkPlayerOut(losers)
    else:
      print("It's a tie between the players: ")
      print(names)
  def reset(self, dealingDeckIndex: int) -> None:
    for player in self.players:
      player.reset()
      
    self.dealerIndex = (self.dealerIndex + 1) % len(self.players)
    
    self.players[(self.dealerIndex + 1) % len(self.players)].hasSmallBlind = True
    self.players[(self.dealerIndex + 2) % len(self.players)].hasBigBlind = True
    self.players[self.dealerIndex].isDealer = True
      
    self.decks[dealingDeckIndex].recycleDiscardedCards()
    self.trial += 1
  def runTrial(self):
    print("Starting Trial " + str(self.trial + 1) + ".")
    
    poolIndex = 0
    pools: list[Pool] = []
    pools.append(Pool())
    smallBlindIndex = (self.dealerIndex + 1) % len(self.players)
    bigBlindIndex = (self.dealerIndex + 2) % len(self.players)
    bigBlindPlayer = self.players[bigBlindIndex]
    smallBlindPlayer = self.players[smallBlindIndex]
    bigBlindPlayer.payBlind(10)
    smallBlindPlayer.payBlind(5)
    self.checkPlayerOut([self.players[smallBlindIndex], self.players[bigBlindIndex]])
    
    #set up players
    namesIn: list[str] = []
    for player in self.players:
      namesIn.append(player.name)
    
    for player in self.players:
      print("Setting up eligible pools for player:", player.name)
      player.addIndexToEligiblePools(poolIndex)
    
    #deal cards
    self.shufflingDeckIndex = (self.shufflingDeckIndex + 1) % len(self.decks)
    self.dealingDeckIndex = (self.dealingDeckIndex + 1) % len(self.decks)
    self.decks[self.shufflingDeckIndex].shuffle(self.players[(self.dealerIndex - 1) % len(self.players)].methods)
    self.players[self.dealerIndex].isDealer = True
    self.decks[self.dealingDeckIndex].deal(self.dealerIndex)
    
    #first bets
    namesIn = self.handlePlayerRound(namesIn, pools, poolIndex, 1)
    #3 revealed
    self.decks[self.dealingDeckIndex].revealThree()
    #second bet
    namesIn = self.handlePlayerRound(namesIn, pools, poolIndex, 2)
    #4 revealed
    self.decks[self.dealingDeckIndex].revealNext()
    #third bet
    namesIn = self.handlePlayerRound(namesIn, pools, poolIndex, 3)
    #final card revealed
    self.decks[self.dealingDeckIndex].revealNext()
    
    #decide winner
    self.decideWinner(pools, namesIn)
    #reset
    self.reset(self.dealingDeckIndex)
    
  def simulate(self, rounds: int = -1) -> None:
    if rounds == -1:
      done = False
      while not done:
        self.runTrial()
        if(len(self.players) == 1):
          done = True
    else:
      print("Simulating " + str(rounds) + " rounds.")
      for _ in range(rounds):
        print("round start")
        self.runTrial()
        print("round end")
        if(len(self.players) == 1):
          break