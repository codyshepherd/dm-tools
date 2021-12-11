from wonderwords import RandomWord, Defaults


def name_gen_adj_noun(**kwargs):
    r = RandomWord()

    adj = r.random_words(1, include_parts_of_speech=["adjectives"])[0].capitalize()
    noun = r.random_words(1, include_parts_of_speech=["nouns"])[0].capitalize()

    return f"The {adj} {noun}"
