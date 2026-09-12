import random
from parse import parse_dictionary

def index_is_already_marked(secret_word, word, guess_state, index):
	k = 0
	while k < 5:
		if guess_state[k] == index:
			return 1
		k = k + 1
	return 0

def guess_word(secret_word, word):
	guess_state = [-1]*5
	tuple_list = list(zip(secret_word, word))
	i = 0
	for tuple in tuple_list:
		if (tuple[0] == tuple[1]):
			guess_state[i] = -2
		i = i + 1
	for i in range(5):
		if guess_state[i] == -1:
			for j in range(5):
				print("comparing %c with %c", secret_word[j], word[i])
				if guess_state[j] == -1 and secret_word[j] == word[i]:
					guess_state[i] = j
	return guess_state

if __name__ == "__main__":
	content = parse_dictionary("../words.txt")
	wordlist = content.split()
	guess_count = 6
	game_won = 0
	secret_word = random.choice(wordlist)
	print(secret_word)
	while guess_count > 0:
		word = input("")
		guess_state = guess_word(secret_word, word)
		# print_guess_state(guess_state)
		# if check_game_completion(guess_state):
		# 	game_won = 1
		# 	break
		print("guess_state_array is:")
		for i in range(5):
			print(guess_state[i], end=" ")
		print("")
		guess_count = guess_count - 1
	if game_won:
		print("You won")
