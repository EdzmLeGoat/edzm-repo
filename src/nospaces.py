file = open("nospaces.txt", "w+")

# Read the contents of the original file
ogFile = open("web/hands.txt", "r")

sortedLines: list[str] = []
# Iterate through each line in the original file
for line in ogFile:
  if(line != "\n" and line != " " and line != ""):
    # Write the line to the new file without spaces
    line = line.strip()
    cards = [line.split(" ")[0], line.split(" ")[1]]
    cards.sort()
    cardLine = cards[0] + " " + cards[1] + "\n"
    print(cardLine)
    sortedLines.append(cardLine)
    
sortedLines.sort()

for line in sortedLines:
  file.write(line)

# Close both files
ogFile.close()
file.close()