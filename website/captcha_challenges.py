import random


CAPTCHA_WORDS = (
    'growth',
    'policy',
    'public',
    'future',
    'nation',
    'report',
    'budget',
    'sector',
    'vision',
    'impact',
    'reform',
    'service',
)


def word_challenge():
    word = random.choice(CAPTCHA_WORDS)
    return word.upper(), word.lower()
