#imports
from components.Game import Game
from components.Player import Player, ShuffleMethod
#constants
initialChips = 60
p1 = Player("Mr. Kirk", ShuffleMethod.Pharaoh)
p2 = Player("Edem", ShuffleMethod.Riffle)
p3 = Player("Justin", ShuffleMethod.Cut)
p4 = Player("Mr. Sahu", ShuffleMethod.Pharaoh)
p5 = Player("minecraft", ShuffleMethod.Riffle)
p6 = Player("pokemon", ShuffleMethod.Cut)

#start simulations
game = Game([p1, p2, p3, p4, p5, p6])