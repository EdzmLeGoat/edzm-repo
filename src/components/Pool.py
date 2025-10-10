#main class
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
    
  def addIncrease(self, amount: int) -> None:
    self.increase += amount