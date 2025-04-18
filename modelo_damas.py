import pygame
from copy import deepcopy

# Configuración inicial
WIDTH, HEIGHT = 650, 650
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colores
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BEIGE = (240, 217, 181)
BROWN = (181, 136, 99)
CROWN = pygame.transform.scale(pygame.image.load("c:/Users/rofer/OneDrive/Documentos/FACULTAD ROCIO/MODELOS Y SIMULACIONES/crown.png"), (44, 25))  # Asegurate de tener una imagen de corona

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Juego de Damas')


class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)


class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.black_left = 12
        self.red_kings = self.black_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BEIGE)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = None, piece
        piece.move(row, col)

        if row == 0 or row == ROWS - 1:
            piece.make_king()
            if piece.color == RED:
                self.red_kings += 1
            else:
                self.black_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    self.board[row].append(None)
                else:
                    if row < 3:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(None)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = None
            if piece != None:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.black_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return "Negras"
        elif self.black_left <= 0:
            return "Rojas"
        return None

    def get_valid_moves(self, piece):
        moves = {}

        # Definimos las direcciones válidas
        if piece.king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            # RED se mueve hacia arriba (-1), BLACK hacia abajo (+1)
            direction = -1 if piece.color == RED else 1
            directions = [(direction, -1), (direction, 1)]

        for dy, dx in directions:
            row, col = piece.row, piece.col
            skipped = []
            has_captured = False

            for i in range(1, ROWS):
                r = row + dy * i
                c = col + dx * i

                if not (0 <= r < ROWS and 0 <= c < COLS):
                    break

                current = self.board[r][c]

                if current is None:
                    if skipped:
                        moves[(r, c)] = skipped
                        break  # Después de una captura, no puede avanzar más
                    elif not piece.king:
                        if i == 1:
                            moves[(r, c)] = skipped
                        break  # Movimiento simple no coronado, solo 1 casilla
                    else:
                        if not has_captured:
                            moves[(r, c)] = skipped
                elif current.color == piece.color:
                    break
                else:
                    if skipped:
                        break  # No puede saltar dos piezas
                    skipped = [current]
                    has_captured = True

        return moves




    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves


class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != None and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, (0, 255, 0), (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                      row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = BLACK
        else:
            self.turn = RED


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(60)

        if game.board.winner() != None:
            print("Ganó", game.board.winner())
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        game.update()

    pygame.quit()


if __name__ == "__main__":
    main()
