lst = [1, 2, 3, 4]

# Goal: find the index at which lst is x
x = 3

# Solution 1:
for i in range(len(lst)):
    if lst[i] == x:
        index_1 = i


# Solution 2:
index_2 = [j for j, y in enumerate([i == x for i in lst]) if y]

# Solution 3:
index_3 = lst.index(x)

def starting_with(lst, start):
    for idx in range(len(lst)):
        yield lst[(idx + start) % len(lst)]


for j in starting_with(lst, 2):
    print(j)