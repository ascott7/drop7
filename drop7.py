import random
import time
import sys,tty,termios
import numpy as np

class Game:
    def __init__(self, sleep=False, print_board=True):
        # board[row][column], top row is row 6 and bottom row is row 0
        # 9 means we have an unbroken piece (O) and 8 means we have a partly broken piece (@)
        self.board = np.zeros((7, 7), dtype=np.int)#[[0 for x in range(7)] for y in range(7)]
        self.sleep = sleep
        self.level = 1
        self.pieces_left = 30
        self.current_piece = random.randint(1, 9)
        self.points = 0
        self.game_over = False
        self.overflow = np.zeros((7), dtype=np.int)
        self.print_board = print_board
        """self.board[0][0] = 1
        self.board[1][0] = 2
        self.board[2][0] = 3
        self.board[3][0] = 4
        self.board[4][0] = 5
        self.board[5][0] = 6"""
        self.board[0][0] = 5
        self.board[1][0] = 7
        #self.board[2][0] = 5
        self.board[2][0] = 2
        self.board[3][0] = 1
        self.board[0][3] = 8
        self.board[0][5] = 9

    def current_piece(self):
        return self.current_piece
        
    def chain_points(self):
        yield 7
        yield 39
        current_points = 109
        point_inc, d_point_inc = 70, 38
        for i in range(30):
            yield current_points
            d_point_inc += 7
            point_inc += d_point_inc
            current_points += point_inc

    def available_cols(self):
        cols = self.board.min(axis=0)
        available = []
        for c, m in zip(range(0, 7), cols):
            if m == 0:
                available.append(c)
        return available

    def place_piece(self, col):
        """
        Tries to place the current piece in the given column, returning True if
        the piece is places and False if the piece cannot be placed.
        """
        # column is full
        if self.board[6][col] != 0:
            return False
        for j in range(0, 7):
            if self.board[j][col] == 0:
                self.board[j][col] = self.current_piece
                break
        if self.print_board:
            print self.__str__()
        if self.sleep:
            time.sleep(1)
        point_counter = self.chain_points()
        pieces_popped = self.pop_pieces()
        self.points += pieces_popped * point_counter.next()
        while pieces_popped > 0:
            if self.print_board:
                print self.__str__()
            if self.sleep:
                time.sleep(1)
            pieces_popped = self.pop_pieces()
            self.points += pieces_popped * point_counter.next()

        self.current_piece = random.choice([1, 2, 3, 4, 5, 6, 7, 9])
        self.pieces_left -= 1
        if self.pieces_left == 0:
            self.level_up()
        if self.board.min(axis=1)[6] != 0:
            self.game_over = True
        return True

    def level_up(self):
        self.level += 1
        self.pieces_left = max(31 - self.level, 5)
        self.points += 7000
        # first check if this will end the game
        self.overflow = np.copy(self.board[6])
        if self.overflow.max() != 0:
            self.game_over = True

        # add a row of unbroken pieces along the bottom,
        for j in range(6, -1, -1):
            for i in range(0, 7):
                self.board[j][i] = self.board[j - 1][i]
        for i in range(0, 7):
            self.board[0][i] = 9

    def pieces_in_row(self, row, col):
        c = 1
        # count to the right
        for i in range(col + 1, 7):
            if self.board[row][i] != 0:
                c += 1
            else:
                break
        # count to the left
        for i in range(col - 1, -1, -1):
            if self.board[row][i] != 0:
                c += 1
            else:
                break
        return c

    def pieces_in_col(self, col):
        c = 0
        for j in range(0, 7):
            if self.board[j][col] != 0:
                c += 1
        return c

    def explode_piece(self, b, row, col):
        if row >= 0 and row <= 6 and col >= 0 and col <= 6:
            if b[row][col] == 9:
                b[row][col] = 8
            elif b[row][col] == 8:
                b[row][col] = random.randint(1, 7)

    def settle_col(self, board, col):
        for j in range(0, 7):
            p = 0
            for jj in range(j, 7):
                if board[jj][col] != 0:
                    p = board[jj][col]
                    board[jj][col] = 0
                    break
            board[j][col] = p
    
    def pop_pieces(self):
        # make a deep copy of the board
        new_board = np.copy(self.board)
        popped_pieces = []

        for j in range(0, 7):
            for i in range(0, 7):
                p = self.board[j][i]
                if p != 0 and (self.pieces_in_row(j, i) == p or self.pieces_in_col(i) == p):
                    popped_pieces.append((j, i))
                    new_board[j][i] = 0
                    self.explode_piece(new_board, j + 1, i)
                    self.explode_piece(new_board, j - 1, i)
                    self.explode_piece(new_board, j, i + 1)
                    self.explode_piece(new_board, j, i - 1)

        # drop pieces down the columns after pieces have exploded
        for i in range(7):
            self.settle_col(new_board, i)
        # update the board if necessary
        if len(popped_pieces) > 0:
            self.board = new_board
        return len(popped_pieces)
        
    def __str__(self):
        board = '\n'
        board += "level: " + str(self.level)
        board += "\npieces left this level: " + str(self.pieces_left)
        board += "\nnext piece: " + str(self.current_piece)
        board += "\nscore: " + str(self.points) + "\n "
        for col in self.overflow:
            if col != 0 and col <= 7:
                board += str(col)
            elif col == 8:
                board += '@'
            elif col == 9:
                board += 'O'
            else:
                board += ' '
            board += ' '
        board += '\n'
        for row in reversed(self.board):
            for col in row:
                board += '|'
                if col != 0 and col <= 7:
                    board += str(col)
                elif col == 8:
                    board += '@'
                elif col == 9:
                    board += 'O'
                else:
                    board += ' '
            board += '|\n'
        # chop off the last newline
        return board[:-1]
                
# http://stackoverflow.com/questions/22397289/finding-the-values-of-the-arrow-keys-in-python-why-are-they-triples
class _Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(3)
        except KeyboardInterrupt:
            ch = "ctrl-C"
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
            
def get():
    inkey = _Getch()
    k=inkey()
    if k=='\x1b[A':
        return "up"
    elif k=='\x1b[B':
        return "down"
    elif k=='\x1b[C':
        return "right"
    elif k=='\x1b[D':
        return "left"
    elif k=='ctrl-C':
        return 'kill'
    else:
        print k
        return None
    
if __name__ == "__main__":

    g = Game(sleep=False, print_board=False)
    index = 0
    print g
    #time.sleep(1)
    #g.place_piece(5)
    #time.sleep(1)

    #g.place_piece(3)

    while not g.game_over:
        choices = g.available_cols()
        col = random.choice(choices)
        #time.sleep(1)
        g.place_piece(col)
        #print g
    print g
    #screen = curses.initscr()
    #screen.addstr("Hello World!!!")
    #screen.addstr(b.__str__())
    #screen.refresh()
    #a = screen.getch()
    #screen.addstr()
    #if a == '\[':
    #    screen.addstr("hello")
    #screen.addstr(str(screen.getch()))
    #curses.endwin()
    #print a
    """
    for x in range(3):
        p = random.randint(1, 7)
        while True:
            
            #print 'in loop'
            print 'index is', index
            print ' ' * index, p
            print b
            key = get()
            if key == 'left':
                index = max(0, index - 1)
            elif key == 'right':
                index = min(6, index + 1)
            elif key == 'down':
                if b.place_piece(p, index):
                    break
                else:
                    print 'can\'t place in column', index + 1
            elif key == 'kill':
                print 'trying to kill'
                sys.exit(0)
       """     

        #print b
        #col = input('column: ') - 1
        #while not b.place_piece(p, col):
        #    print 'can\'t use that column, try another'
            #col = input('column: ') - 1
