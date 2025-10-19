#main class
class Pool:
  chips: int = 0
  increase: int = 0
  def __init__(self):
    self.chips = 0
    self.minBet = 0
    self.round = 0
  
  def addChips(self, amount: int, round: int) -> None:
    if(round != self.round):
      self.round = round
      self.minBet = 0
    if(not amount == 0):
      self.chips += amount
      if(amount > self.minBet):
        self.minBet = amount
      print(f"Added {amount} chips to the pool. Current total: {self.chips}")
  #called at the end of each betting round
  def resetIncrease(self) -> None:
    self.increase = 0
    
  def addIncrease(self, amount: int) -> None:
    self.increase += amount
    
  def setMinBet(self, amount: int) -> None:
    self.minBet = amount