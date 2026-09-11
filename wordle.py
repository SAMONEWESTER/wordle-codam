import random


def check_word(guess: str, answer: str) -> list[dict[str, str]] | None:
    i = 0

    if len(guess) != 5 or len(answer) != 5:
        return None

    answer_count = {}
    for letter in answer:
        if letter in answer_count.keys():
            answer_count[letter] += 1
        else:
            answer_count[letter] = 1

    guess, answer = guess.lower(), answer.lower()
    result_list = []
    used_letters = {}
    for letter in guess:
        result_dict = {}
        if letter in used_letters.keys():
            used_letters[letter] += 1
        else:
            used_letters[letter] = 1
        if letter == answer[i]:
            result_dict[letter] = "green"
        elif letter in answer and used_letters[letter] <= answer_count[letter]:
            result_dict[letter] = "yellow"
        else:
            result_dict[letter] = "grey"
        i += 1

        result_list.append(result_dict)
    return result_list


class wordle():
    def __init__(self, wordle_list: list[str]):
        self.legal: list[str] = wordle_list
        self.board: list[list[dict[str, str]]] = []
        self.answer = random.choice(self.legal)
        self.guess_amount = 6
        self.word_length = 5

    def run_game(self):
        i: int = 0
        while i < self.guess_amount - 1:
            user_guess: str = input("Input your guess now! (5 letters)\n\n")
            if not user_guess.isalpha() or len(user_guess) != self.word_length:
                print("Syntax or word_length wrong. Please try again")
                continue
            if user_guess in self.legal:
                result = check_word(user_guess, self.answer)
                if result is not None:
                    self.board.append(result)
                i += 1
                print(result)
            else:
                print("Word not in word list!")
                continue


class wordle_list():
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.word_list: list[str] = []
        self.create_word_list()

    def get_next_line(self):
        with open(self.file_path) as f:
            for line in f:
                yield line.strip()

    def create_word_list(self) -> list[str]:
        for word in self.get_next_line():
            self.word_list.append(word)


if __name__ == "__main__":
    filepath = "words.txt"
    wordle_lister = wordle_list(filepath)
    game = wordle(wordle_lister.word_list)
    game.run_game()
    print(f"\nANSWER: {game.answer}")
    for rount in game.board:
        print(rount)
    word_length = 5
    # print(check_word("apple", "apple"))
    # print(check_word("apple", "APPLE"))
    # print(check_word("apple", "gpple"))
    # print(check_word("apple", "pplea"))
