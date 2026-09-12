import random
import pygame

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
ANSI_CLEAR = "\033[1A\033[2K\r"

COLOR_DICTIONARY = {
	WHITE: ANSI_WHITE,
	GREEN: ANSI_GREEN,
	YELLOW: ANSI_YELLOW,
	GREY: ANSI_GREY
}

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 500
RGB_GREEN_COLOR = (0, 128, 0)
RGB_YELLOW_COLOR = (255, 207, 0)
RGB_WHITE = (255, 255, 255)
RGB_BLACK = (0, 0, 0)

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
			guess_state[i] = GREY
	return guess_state

def guess_word(wordlist, word, guess):
	while guess not in wordlist:
		print(ANSI_CLEAR + ANSI_RED + guess + ANSI_RESET)
		guess = input("")
	guess_state = update_current_state(word, guess)
	return guess, guess_state

def draw_character(window, letters, current_x, current_y, color):
	
	square = pygame.Rect(current_x * 100, current_y * 100, 100, 100)
	pygame.draw.rect(window, color, square)
	font = pygame.font.Font(None, 50)
	character = font.render(letters[current_x], True, RGB_BLACK)
	window.blit(character, character.get_rect(center=square.center))
	pygame.display.flip()

if __name__ == "__main__":
	
	pygame.init()
	window = pygame.display.set_mode((WINDOW_HEIGHT, WINDOW_WIDTH))
	window.fill(RGB_WHITE)

	wordlist = parse_dictionary("words.txt")
	word = random.choice(wordlist)
	# print(word)
	counter = 0
	running = True
	letters = []
	current_x = 0
	current_y = 0
	guess_state = [WHITE] * WORD_SIZE
	while running and counter < NUMBER_OF_GUESSES:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.type == pygame.K_RETURN:
					if len(letters) == 5:
						break
				elif event.type == pygame.K_BACKSPACE:
					letters = letters[:-1]
					delete_character() #
					if (current_x > 0):
						current_x = current_x - 1
				elif event.unicode.isalpha():
					letters.append(event.unicode)
					draw_character(window, letters, current_x, current_y, WHITE) #
					current_x = current_x + 1
		guess = ''.join(letters)
		if guess in wordlist:
			guess_state = update_current_state(word, guess)
			# redraw_current_state(window, guess_state, current_y) #
			current_y = current_y + 1
		# pygame.draw.rect(window, GREEN_COLOR, [0, 0, 100, 100], 0)
		# pygame.draw.rect(window, YELLOW_COLOR, [100, 0, 100, 100], 0)
		# pygame.display.update()
		# print_current_state(guess, guess_state)
		if game_is_complete(guess_state):
			running = False
		counter = counter + 1
	pygame.quit()
