import random

NAME = "WORDLE 42"
NUMBER_OF_GUESSES = 6
WORD_SIZE = 5
WHITE = 0
GREEN = 1
YELLOW = 2
GREY = 3
ANSI_GREEN = "\033[32m"
ANSI_ORANGE = "\033[33m"
ANSI_RESET = "\033[0m"
ANSI_CLEAR = "\033[2K\r"

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

def guess_word(wordlist, word):
	guess = input("")
	while guess not in wordlist:
		print("This word is not in the dictionary")
		guess = input("")
	guess_state = [WHITE] * WORD_SIZE
	word_state = [WHITE] * WORD_SIZE
	tuple_list = list(zip(word, guess))
	i = 0
	for tuple in tuple_list:
		if (tuple[0] == tuple[1]):
			guess_state[i] = GREEN
			word_state[i] = GREEN
		i = i + 1
	for i in range(WORD_SIZE):
		if guess_state[i] != GREEN:
			for j in range(WORD_SIZE):
				if word_state[j] == WHITE:
					if word[j] == guess[i]:					
						guess_state[i] = YELLOW
						word_state[j] = YELLOW
	for i in range(WORD_SIZE):
		if guess_state[i] == WHITE:
			guess_state[i] == GREY
	return guess, guess_state

if __name__ == "__main__":
	wordlist = parse_dictionary("words.txt")
	word = random.choice(wordlist)
	print(word)
	counter = NUMBER_OF_GUESSES
	print("Enter a word:")
	while counter > 0:
		print_current_state(*guess_word(wordlist, word))
		print("guess_state_array is:")
		for i in range(5):
			print(guess_state[i], end=" ")
		print("")
		if game_is_complete(guess_state):
			break
		counter = counter - 1
