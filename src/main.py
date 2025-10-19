#imports
from components.Game import Game
from components.Player import Player, ShuffleMethod
import sys
#constants
initialChips = 60
p1 = Player("Mr. Kirk", [ShuffleMethod.Pharaoh,ShuffleMethod.Mover, ShuffleMethod.Pharaoh], initialChips)
p2 = Player("Edem", [ShuffleMethod.Riffle, ShuffleMethod.Cut, ShuffleMethod.Cut], initialChips)
p3 = Player("Justin", [ShuffleMethod.Cut, ShuffleMethod.Mover, ShuffleMethod.Cut], initialChips)
p4 = Player("Mr. Sahu", [ShuffleMethod.Pharaoh,ShuffleMethod.Pharaoh, ShuffleMethod.Pharaoh], initialChips)
p5 = Player("minecraft", [ShuffleMethod.Cut,ShuffleMethod.Mover, ShuffleMethod.Cut], initialChips)
p6 = Player("pokemon", [ShuffleMethod.Riffle,ShuffleMethod.Mover, ShuffleMethod.Riffle], initialChips)

#start simulations
game = Game([p1, p2, p3, p4, p5, p6])
game.simulate(1)
print("Simulation complete.")
sys.exit()