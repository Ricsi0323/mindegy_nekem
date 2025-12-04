"""
random_snippet.py

Small utility that generates random sentences and passwords.
Usage examples:
    python random_snippet.py --sentences 5
    python random_snippet.py --password --length 16
    python random_snippet.py --sentences 3 --seed 42
"""

import random
import argparse
import string

SUBJECTS = [
    "A cat",
    "The programmer",
    "A robot",
    "My neighbor",
    "The system",
    "An old man",
    "The little bird",
]

VERBS = [
    "eats",
    "builds",
    "observes",
    "prints",
    "jumps over",
    "discovers",
    "optimizes",
]

OBJECTS = [
    "a sandwich",
    "the algorithm",
    "the sunrise",
    "a mystery",
    "the log file",
    "a small bug",
    "an idea",
]

ADJECTIVES = [
    "quickly",
    "silently",
    "reluctantly",
    "bravely",
    "happily",
    "weirdly",
]


def generate_sentence():
    s = random.choice(SUBJECTS)
    v = random.choice(VERBS)
    o = random.choice(OBJECTS)
    a = random.choice(ADJECTIVES)
    return f"{s} {v} {o} {a}."


def generate_password(length=12, use_symbols=True):
    chars = string.ascii_letters + string.digits
    if use_symbols:
        chars += "!@#$%^&*()-_=+"
    return ''.join(random.choice(chars) for _ in range(length))


def main():
    parser = argparse.ArgumentParser(description="Random snippet: sentences and passwords")
    parser.add_argument('--sentences', '-s', type=int, default=0, help='Number of random sentences to print')
    parser.add_argument('--password', '-p', action='store_true', help='Generate a random password')
    parser.add_argument('--length', '-l', type=int, default=12, help='Password length')
    parser.add_argument('--no-symbols', action='store_true', help='Do not include symbols in password')
    parser.add_argument('--seed', type=int, help='Optional random seed for reproducibility')

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if args.sentences > 0:
        for _ in range(args.sentences):
            print(generate_sentence())

    if args.password:
        pwd = generate_password(length=args.length, use_symbols=not args.no_symbols)
        print('\nGenerated password:')
        print(pwd)

    if args.sentences == 0 and not args.password:
        # If no options given, print one sentence as demo
        print(generate_sentence())


if __name__ == '__main__':
    main()
