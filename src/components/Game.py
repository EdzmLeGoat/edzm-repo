#imports
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
  shufflingDeckIndex: int = 0
  dealingDeckIndex: int = 1
  
  #requires 3 people to start
  def __init__(self, players: list[Player]):
    if(len(players) < 4):
      raise ValueError("Must have at least 4 players.")
    self.players = players
    self.decks = [Deck(players), Deck(players)]
    self.players[self.smallBlindIndex].hasSmallBlind = True
    self.players[self.bigBlindIndex].hasBigBlind = True
    self.decks[self.shufflingDeckIndex].shuffle(self.players[self.dealerIndex].methods)

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
      
  def getPlayerFromName(self, name: str) -> Player:
    for player in self.players:
      if player.name == name:
        return player
    raise ValueError("No player with that name found.")

  def handlePlayerRound(self, namesIn: list[str], pools: list[Pool], poolIndex: int, round: int) -> list[str]:
    print("round:", + round)
    someoneAllIn = False
    if(round == 1):
      #first round, set min bet to big blind
      pools[poolIndex].setMinBet(10)
    
    for name in namesIn:
      player = self.getPlayerFromName(name)
      player.getRank()
      bet = player.decideAction(pools[poolIndex].minBet, someoneAllIn, round, len(namesIn))
      if(bet != -1):
        pools[poolIndex].addChips(bet, round)
      if player.isAllIn:
        someoneAllIn = True
        #since when a player goes all in, they create a new pool that
        #they are not eligible for
        pools.append(Pool())
        poolIndex += 1
        for player in self.players:
          if not player.isAllIn:
            player.eligiblePools.append(pools[poolIndex])
            
      if player.bet == Bet.Fold:
        print("Player " + name + " has folded.")
        namesIn.remove(name)
        
      print("")
        
    pools[poolIndex].resetIncrease()
    return namesIn
  
  def decideWinner(self, namesIn: list[str]) -> None:
    #winner decided
    maxRank = 0.0
    names: list[str] = []
    for name in namesIn:
      player = self.getPlayerFromName(name)
      player.getRank()
      if player.handRating > maxRank:
        maxRank = player.handRating
        names = [name]
      elif player.handRating == maxRank:
        names.append(name)
    if len(names) == 1:
      player = self.getPlayerFromName(names[0])
      print("Player " + player.name + " won the game with a hand of: ")
      player.printHand()
      print("They won with a ranking of " + str(player.getRank()) + ".")
      for pool in player.eligiblePools:
        player.winChips(pool.chips)
      print("Chips won: " + str(pool.chips))
      
      losers: list[int] = []
      for i in range(len(self.players)):
        if not self.players[i] == player:
          losers.append(i)
      self.checkPlayerOut(losers)
    else:
      print("It's a tie between the players: ")
      print(names)
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
    print("Starting Round " + str(self.trial + 1) + ".")
    
    poolIndex = 0
    pools: list[Pool] = []
    pools.append(Pool())
    bigBlindPlayer = self.players[self.bigBlindIndex]
    smallBlindPlayer = self.players[self.smallBlindIndex]
    bigBlindPlayer.payBlind(10)
    smallBlindPlayer.payBlind(5)
    self.checkPlayerOut([self.smallBlindIndex, self.bigBlindIndex])
    
    #set up players
    namesIn: list[str] = []
    for player in self.players:
      namesIn.append(player.name)
    
    for player in self.players:
      player.eligiblePools.append(pools[poolIndex])
    
    #deal cards
    self.shufflingDeckIndex = (self.shufflingDeckIndex + 1) % len(self.decks)
    self.dealingDeckIndex = (self.dealingDeckIndex + 1) % len(self.decks)
    self.decks[self.shufflingDeckIndex].shuffle(self.players[self.preDealerIndex].methods)
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
    self.decideWinner(namesIn)
    
    #reset
    self.reset(self.dealingDeckIndex)
    
  def simulate(self, rounds: int = -1) -> None:
    if rounds == -1:
      done = False
      while not done:
        self.playRound()
        if(len(self.players) == 1):
          done = True
    else:
      for _ in range(rounds):
        self.playRound()
        if(len(self.players) == 1):
          break