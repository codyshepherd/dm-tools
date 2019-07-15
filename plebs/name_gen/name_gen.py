import numpy
import random
import re
import string
import yaml

VOWELS = ('a', 'e', 'i', 'o', 'u', 'y')
CONSONANTS = tuple(l for l in string.ascii_lowercase if l not in VOWELS)
LETTER_TYPES = (VOWELS, CONSONANTS)


def name_gen_prob(max_len=10):
    print("name_gen")
    name = []
    name_len = random.randint(3, max_len)

    with open('name_gen/probs.yaml', 'r') as fh:
        probs = yaml.safe_load(fh)

    letters = list(probs.keys())
    dist = list(probs.values())
    sumdist = sum(dist)
    diff = 1.0 - sumdist
    dist[16] += diff    # add any residual required probability to q, for that
                        # fantasy name panache

    while len(name) < name_len:
        name.append(numpy.random.choice(letters, p=dist))

    return ''.join(name).capitalize()


def name_gen_pairs(max_len=10):
    print("name_gen_pairs")
    name = []
    name_len = random.randint(3, max_len)
    order = list(range(len(LETTER_TYPES)))

    while len(name) < name_len:
        random.shuffle(order)
        for i in order:
            name.append(numpy.random.choice(LETTER_TYPES[i]))

    return ''.join(name).capitalize()


def name_gen_alternator(max_len=10):
    print("name_gen_alternator")
    name = ''
    name_len = random.randint(3, max_len)

    init_cons_prob = .25
    init_v_prob = .75

    cons_prob = init_cons_prob
    v_prob = init_v_prob

    v_seq_len = 0
    cons_seq_len = 0
    while len(name) < name_len:
        choice = numpy.random.choice([VOWELS, CONSONANTS],
                                     p=[v_prob, cons_prob])
        letter = numpy.random.choice(list(choice))
        name += letter

        last_letter = name[-1]

        v_seq_regex = re.compile('.*[{}]+$'.format(''.join(VOWELS)))
        cons_seq_regex = re.compile('.*[{}]+$'.format(''.join(CONSONANTS)))

        if last_letter in VOWELS:
            cons_seq_len = 0
            seq = re.search(v_seq_regex, name).group(0)

            v_seq_len = len(seq)

            v_prob -= round(.05 * v_seq_len, 2)
            cons_prob += round(.05 * v_seq_len, 2)

            if v_prob < 0 or cons_prob < 0:
                v_prob = init_v_prob
                cons_prob = init_cons_prob

        elif last_letter in CONSONANTS:
            v_seq_len = 0

            seq = re.search(cons_seq_regex, name).group(0)

            cons_seq_len = len(seq)

            v_prob += round(.05 * cons_seq_len, 2)
            cons_prob -= round(.05 * cons_seq_len, 2)

            if v_prob < 0 or cons_prob < 0:
                v_prob = init_v_prob
                cons_prob = init_cons_prob

    return name.capitalize()


if __name__ == "__main__":
    print(name_gen())
