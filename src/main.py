#imports
from components.Game import Game
from components.Player import Player, ShuffleMethod
#constants
initialChips = 60
p1 = Player("Mr. Kirk", ShuffleMethod.Pharaoh, initialChips)
p2 = Player("Edem", ShuffleMethod.Riffle, initialChips)
p3 = Player("Justin", ShuffleMethod.Cut, initialChips)
p4 = Player("Mr. Sahu", ShuffleMethod.Pharaoh, initialChips)
p5 = Player("minecraft", ShuffleMethod.Riffle, initialChips)
p6 = Player("pokemon", ShuffleMethod.Cut, initialChips)

#start simulations
game = Game([p1, p2, p3, p4, p5, p6])