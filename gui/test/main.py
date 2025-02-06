import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 10
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 10
CROSS_WIDTH = 10
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

# Fonts
pygame.font.init()
font = pygame.font.Font(r"C:\Users\kenne\Experiments\!STS-TES\card-game\assets\Planewalker.otf", 50)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")
screen.fill(BG_COLOR)

# Board
board = [[None] * BOARD_COLS for _ in range(BOARD_ROWS)]
player = "X"
game_over = False


def draw_lines():
    """ Draws the grid lines. """
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), LINE_WIDTH)


def draw_marks():
    """ Draws Xs and Os based on board state. """
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == "O":
                pygame.draw.circle(
                    screen, CIRCLE_COLOR,
                    (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                    CIRCLE_RADIUS, CIRCLE_WIDTH
                )
            elif board[row][col] == "X":
                start_x = col * SQUARE_SIZE + SPACE
                start_y = row * SQUARE_SIZE + SPACE
                end_x = (col + 1) * SQUARE_SIZE - SPACE
                end_y = (row + 1) * SQUARE_SIZE - SPACE
                pygame.draw.line(screen, CROSS_COLOR, (start_x, start_y), (end_x, end_y), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, (start_x, end_y), (end_x, start_y), CROSS_WIDTH)


def check_winner():
    """ Checks for a winner and returns X, O, or None. """
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]

    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]

    return None


def draw_winner(winner):
    """ Displays the winner and restarts the game. """
    text = font.render(f"{winner} Wins! Click to Restart", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 4, HEIGHT // 2))
    pygame.display.update()


def restart():
    """ Resets the game state. """
    global board, player, game_over
    board = [[None] * BOARD_COLS for _ in range(BOARD_ROWS)]
    player = "X"
    game_over = False
    screen.fill(BG_COLOR)
    draw_lines()


# Game loop
draw_lines()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, y = event.pos
            row, col = y // SQUARE_SIZE, x // SQUARE_SIZE

            if board[row][col] is None:
                board[row][col] = player
                player = "O" if player == "X" else "X"

                winner = check_winner()
                if winner:
                    draw_winner(winner)
                    game_over = True

        elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
            restart()

    draw_marks()
    pygame.display.update()
