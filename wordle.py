from prompt_toolkit import PromptSession
import random
import time

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
	GREY: ANSI_GREY
}

def print_in_colors(character, state):
	print(COLOR_DICTIONARY[state] + character + ANSI_RESET, end="")

def print_current_state(guess, guess_state):
	print(ANSI_CLEAR, end="")
	for i in range(WORD_SIZE):
		print_in_colors(guess[i], guess_state[i])
	print("")

def parse_dictionary(path):
	with open(path, 'r') as file:
		content = file.read()
	wordlist = content.split()
	return wordlist

def game_is_complete(guess_state):
	for i in range(WORD_SIZE):
		if guess_state[i] != GREEN:
			return 0
	return 1

def update_current_state(word, guess):
	guess_state = [WHITE] * WORD_SIZE
	word_state = [WHITE] * WORD_SIZE
	tuple_list = list(zip(word, guess))
	i = 0
	for tuple in tuple_list:
		if (tuple[0] == tuple[1] or tuple[0] == tuple[1].lower()):
			guess_state[i] = GREEN
			word_state[i] = GREEN
		i = i + 1
	for i in range(WORD_SIZE):
		if guess_state[i] != GREEN:
			for j in range(WORD_SIZE):
				if word_state[j] == WHITE:
					if word[j] == guess[i] or word[j] == guess[i].lower():
						guess_state[i] = YELLOW
						word_state[j] = YELLOW
						break # missing break was causing the loop to mark more indexes than needed
	for i in range(WORD_SIZE):
		if guess_state[i] == WHITE:
			guess_state[i] = GREY
	return guess_state

def guess_word(wordlist, word):
	session = PromptSession(erase_when_done=True)
	guess = session.prompt("")
	while guess.lower() not in wordlist:
		print(ANSI_DELETE + ANSI_RED + guess + ANSI_RESET, end="")
		time.sleep(0.3)
		print(ANSI_DELETE, end="")
		guess = session.prompt("")
	print("")
	guess_state = update_current_state(word, guess)
	return guess, guess_state

def main():
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
