import random
import time

from prompt_toolkit import PromptSession

NUMBER_OF_GUESSES = 6
WORD_SIZE = 5
WHITE = 0
GREEN = 1
YELLOW = 2
GREY = 3
ANSI_RED = "\033[31m"
ANSI_WHITE = "\033[37m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[38;5;214m"
ANSI_GREY = "\033[38;5;247m"
ANSI_RESET = "\033[0m"
ANSI_DELETE = "\033[2K\r"
ANSI_CLEAR = "\033[1A\033[2K\r"

COLOR_DICTIONARY = {
	WHITE: ANSI_WHITE,
	GREEN: ANSI_GREEN,
	YELLOW: ANSI_YELLOW,
	GREY: ANSI_GREY,
}


def print_in_colors(character: str, state: int) -> None:
	"""Prints a character using the color specified in its state."""
	print(COLOR_DICTIONARY[state] + character + ANSI_RESET, end="")


def print_current_state(guess: str, guess_state: list[int]) -> None:
	"""Reprints the guess with each letter colored by its corresponding state."""
	print(ANSI_CLEAR, end="")
	for i in range(WORD_SIZE):
		print_in_colors(guess[i], guess_state[i])
	print()


def parse_dictionary(path: str) -> list[str]:
	"""Reads a list of words, separated by whitespace from the given file path."""
	with open(path, "r") as file:
		content = file.read()
	wordlist = content.split()
	return wordlist


def game_is_complete(guess_state: list[int]) -> bool:
	"""Returns True if every guess character is green."""
	for i in range(WORD_SIZE):
		if guess_state[i] != GREEN:
			return 0
	return 1


def update_current_state(word: str, guess: str) -> list[int]:
	"""Finds the right color for each character within a guess by comparing it to target word."""
	guess_state = [WHITE] * WORD_SIZE
	word_state = [WHITE] * WORD_SIZE
	tuple_list = list(zip(word, guess))
	i = 0
	for tuple in tuple_list:
		if tuple[0] == tuple[1] or tuple[0] == tuple[1].lower():
			guess_state[i] = GREEN
			word_state[i] = GREEN
		i = i + 1
	for i in range(WORD_SIZE):
		if guess_state[i] != GREEN:
			for j in range(WORD_SIZE):
				if word_state[j] == WHITE and (
					word[j] == guess[i] or word[j] == guess[i].lower()
				):
					guess_state[i] = YELLOW
					word_state[j] = YELLOW
					break
	for i in range(WORD_SIZE):
		if guess_state[i] == WHITE:
			guess_state[i] = GREY
	return guess_state


def guess_word(wordlist: list[str], word: str) -> tuple[str, list[int]]:
	"""Reads input, checks if it is in the dictionary, then updates current state and return the results."""
	session = PromptSession(erase_when_done=True)
	with session.app.input.raw_mode():
		guess = session.prompt("")
		while guess.lower() not in wordlist:
			print(ANSI_DELETE + ANSI_RED + guess + ANSI_RESET, end="")
			time.sleep(0.3)
			print(ANSI_DELETE, end="")
			guess = session.prompt("", default=guess)
	print()
	guess_state = update_current_state(word, guess)
	return guess, guess_state


def main() -> None:
	"""Main function which runs Wordle."""
	wordlist = parse_dictionary("words.txt")
	word = random.choice(wordlist)
	# print(word)
	counter = NUMBER_OF_GUESSES
	while counter > 0:
		guess, guess_state = guess_word(wordlist, word)
		print_current_state(guess, guess_state)
		if game_is_complete(guess_state):
			break
		counter = counter - 1


if __name__ == "__main__":
	main()
