file = open("nospaces.txt", "w+")

# Read the contents of the original file
ogFile = open("web/hands.txt", "r")

# Iterate through each line in the original file
for line in ogFile:
  if(line != "\n" and line != " " and line != ""):
    # Write the line to the new file without spaces
    file.write(line.strip())
    file.write("\n")

# Close both files
ogFile.close()
file.close()