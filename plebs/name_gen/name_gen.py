import names
import numpy
import petname
import random
import re
import string
import yaml

from . import phonemes

VOWELS = ('a', 'e', 'i', 'o', 'u', 'y')
CONSONANTS = tuple(l for l in string.ascii_lowercase if l not in VOWELS)
LETTER_TYPES = (VOWELS, CONSONANTS)


def name_gen_normcore(**kwargs):
    gender = kwargs.get('gender', random.choice(['male', 'female']))

    first_last = kwargs.get('first_last', 'first')

    funcname = f"get_{first_last}_name"
    func = getattr(names, funcname)

    if first_last == 'first':
        return func(gender=gender)
    else:
        return func()


def name_gen_prob(**kwargs):
    max_len = kwargs.get('max_len', 10)
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


def name_gen_pairs(**kwargs):
    max_len = kwargs.get('max_len', 10)
    name = []
    name_len = random.randint(3, max_len)
    order = list(range(len(LETTER_TYPES)))

    while len(name) < name_len:
        random.shuffle(order)
        for i in order:
            name.append(numpy.random.choice(LETTER_TYPES[i]))

    return ''.join(name).capitalize()


def name_gen_alternator(**kwargs):
    max_len = kwargs.get('max_len', 10)
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


def name_gen_phonemes(**kwargs):
    max_len = kwargs.get('max_len', 10)
    name = ''
    name_len = random.randint(3, max_len)
    return phonemes.generate_string(name_len).capitalize()


def name_gen_petname(**kwargs):
    words = kwargs.get('words', random.randint(1,4))
    word_len = kwargs.get('word_len', random.randint(3, 10))

    first_last = kwargs.get('first_last', 'first')

    name = petname.generate(words, ' ', word_len)

    if first_last == 'first':
        return ' '.join(name.split(' ')[:-1])
    else:
        return name.split(' ')[-1]


if __name__ == "__main__":
    print(name_gen())
