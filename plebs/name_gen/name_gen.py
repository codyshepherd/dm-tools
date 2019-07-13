import numpy
import random
import re
import string

VOWELS = ('a', 'e', 'i', 'o', 'u', 'y')
CONSONANTS = tuple(l for l in string.ascii_lowercase if l not in VOWELS)


def name_gen():
    name = ''
    name_len = random.randint(3, 10)
    print(f"Name len: {name_len}")

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
        print(f"Chose letter: {letter}")
        name += letter

        last_letter = name[-1]

        v_seq_regex = re.compile('.*[{}]+$'.format(''.join(VOWELS)))
        cons_seq_regex = re.compile('.*[{}]+$'.format(''.join(CONSONANTS)))

        if last_letter in VOWELS:
            cons_seq_len = 0
            seq = re.search(v_seq_regex, name).group(0)
            print(f"regex seq: {seq}")

            v_seq_len = len(seq)

            v_prob -= round(.05 * v_seq_len, 2)
            cons_prob += round(.05 * v_seq_len, 2)

            if v_prob < 0 or cons_prob < 0:
                v_prob = init_v_prob
                cons_prob = init_cons_prob

        elif last_letter in CONSONANTS:
            v_seq_len = 0

            seq = re.search(cons_seq_regex, name).group(0)
            print(f"regex seq: {seq}")

            cons_seq_len = len(seq)

            v_prob += round(.05 * cons_seq_len, 2)
            cons_prob -= round(.05 * cons_seq_len, 2)

            if v_prob < 0 or cons_prob < 0:
                v_prob = init_v_prob
                cons_prob = init_cons_prob


        print(v_prob, cons_prob)
        print(name)

    return name


if __name__ == "__main__":
    print(name_gen())
