import random
def shuffle():
    l = list(range(100))
    for i in range(100):
        index = random.randint(0,99)
        index_2 = random.randint(0,99)
        while index == index_2:
            index_2 = random.randint(0,99)
        l[index],l[index_2] = l[index_2],l[index]
    return l
