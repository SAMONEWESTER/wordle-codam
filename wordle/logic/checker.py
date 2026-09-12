"""Core Wordle rules: comparing a guess against the answer.

This module has no I/O and no pygame in it on purpose, so a command
line version and the pygame visualizer can both reuse it as-is.
"""

GREEN = "green"
YELLOW = "yellow"
GREY = "grey"

WORD_LENGTH = 5


def check_word(guess: str, answer: str) -> list[dict[str, str]] | None:
    """Compare guess against answer, one result per letter.

    Returns a list of dicts like {"letter": "e", "state": "green"},
    in guess order. Returns None if either word is not 5 letters.

    Uses the same two pass idea as real Wordle:

    1. Find every green (exact position) match first, and take those
       letters out of the pool of letters that are still "available".
    2. Walk the guess again, left to right, and only hand out a
       yellow while there is still an unused copy of that letter
       left in the pool.

    Doing greens in their own pass first matters for repeated
    letters. For example, answer "evala" only has one "l" and one
    "e" available for guess "level", so only the first "l", the
    first "e" and the "v" should turn yellow. The rest stay grey.
    """
    guess = guess.lower()
    answer = answer.lower()

    if len(guess) != WORD_LENGTH or len(answer) != WORD_LENGTH:
        return None

    remaining_letters = {}
    for letter in answer:
        remaining_letters[letter] = remaining_letters.get(letter, 0) + 1

    states = [None] * WORD_LENGTH

    # Do a run with green first to get those out of the pool.
    for i, letter in enumerate(guess):
        if letter == answer[i]:
            states[i] = GREEN
            remaining_letters[letter] -= 1

    # Do a run to check for remaining yellows or grays.
    for i, letter in enumerate(guess):
        if states[i] is not None:
            continue
        if remaining_letters.get(letter, 0) > 0:
            states[i] = YELLOW
            remaining_letters[letter] -= 1
        else:
            states[i] = GREY

    return [
        {"letter": letter, "state": state}
        for letter, state in zip(guess, states)
    ]
