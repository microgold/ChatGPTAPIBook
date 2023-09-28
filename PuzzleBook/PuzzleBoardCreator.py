import random
import string


class PuzzleBoardCreator:
    def __init__(self, default_value=""):
        self.board = [[default_value for _ in range(13)] for _ in range(13)]

    def clean_word(self, word):
        word = word.upper().replace(" ", "")
        # remove any punctuation
        word = word.translate(str.maketrans('', '', string.punctuation))
        if (len(word) > 10):
            word = word[:10]
        return word

    def place_word(self, board, word):
        print("placing word: " + word)
        # keep it at 10 characters
        word = self.clean_word(word)
        # Randomly choose orientation: 0=horizontal, 1=vertical, 2=diagonal
        orientation = random.randint(0, 3)
        placed = False
        count = 0
        while not placed:
            count += 1
            if count > 200000:
                print("count exceeded {count}".format(count=count))
                return placed

            if orientation == 0:  # Horizontal
                row = random.randint(0, len(board)-1)
                col = random.randint(0, len(board)-len(word))
                reverse = random.choice([True, False])
                if reverse:
                    word = word[::-1]
                space_available = all(board[row][c] == '-' or
                                      board[row][c] == word[i]
                                      for i, c in enumerate(range(col, col+len(word))))
                if space_available:
                    for i, c in enumerate(range(col, col+len(word))):
                        board[row][c] = word[i]
                    placed = True

            elif orientation == 1:  # Vertical
                row = random.randint(0, len(board)-len(word))
                col = random.randint(0, len(board)-1)
                reverse = random.choice([True, False])
                if reverse:
                    word = word[::-1]
                space_available = all(board[r][col] == '-' or
                                      board[r][col] == word[i]
                                      for i, r in enumerate(range(row, row+len(word))))
                if space_available:
                    for i, r in enumerate(range(row, row+len(word))):
                        board[r][col] = word[i]
                    placed = True

            elif orientation == 2:  # Diagonal top-left to bottom right
                row = random.randint(0, len(board)-len(word))
                col = random.randint(0, len(board)-len(word))
                reverse = random.choice([True, False])
                if reverse:
                    word = word[::-1]
                space_available = all(board[r][c] == '-' or
                                      board[r][c] == word[i]
                                      for i, (r, c) in enumerate(zip(range(row, row+len(word)),
                                                                     range(col, col+len(word)))))
                if space_available:
                    for i, (r, c) in enumerate(zip(range(row, row+len(word)),
                                                   range(col, col+len(word)))):
                        board[r][c] = word[i]
                    placed = True

            elif orientation == 3:  # Diagonal bottom-left to top-right
                row = random.randint(len(word) - 1, len(board) - 1)
                col = random.randint(0, len(board) - len(word))
                reverse = random.choice([True, False])
                if reverse:
                    word = word[::-1]
                space_available = all(board[r][c] == '-' or
                                      board[r][c] == word[i]
                                      for i, (r, c) in enumerate(zip(range(row, row-len(word), -1),
                                                                     range(col, col+len(word)))))
                if space_available:
                    for i, (r, c) in enumerate(zip(range(row, row-len(word), -1),
                                                   range(col, col+len(word)))):
                        board[r][c] = word[i]
                    placed = True
        return placed

    def fill_empty(self, board):
        for row in range(len(board)):
            for col in range(len(board)):
                if board[row][col] == '-':
                    board[row][col] = random.choice(string.ascii_uppercase)

    def create_word_search(self, words):
        words_to_remove = []
        board = [['-' for _ in range(13)] for _ in range(13)]

        for word in words:
            placed = self.place_word(board, word)
            if (not placed):
                words_to_remove.append(word)

        self.fill_empty(board)

        return (board, words_to_remove)

    def display_board(self, board):
        for row in board:
            print(' '.join(row))
