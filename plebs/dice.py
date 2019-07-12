import random


def roll(n, d):
    return [random.randint(1, d) for i in range(n)]
