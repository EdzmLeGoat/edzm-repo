file = open("nospaces.txt", "r")
prev = ""
count = 1
max = 0
maxlines : list[str] = [""]
for line in file:
  if(line == prev):
    count += 1
    if(count > max):
      max = count
      maxlines = [line]
    elif count == max:
      maxlines.append(line)
  else:
    prev = line
    count = 1
print(max)
print(" ".join(maxlines))