import numpy as np
import matplotlib.pyplot as plt
import kivy
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.app import App
#X is 1, O is -1, and - is 0


in_dim = 9
player = "X"
ai = "O"

playerc = [1,0,0,1]
aic = [0,1,0,1]
optimal = [1,3,6,1,1,7,2,5,2]
def CheckVictory(board, pos_y, pos_x, stride,pcheck = False, ptype = [0]):
    #check if previous move caused a win on vertical line
    valc= [0]
    if pcheck:
        valc = ptype
    if board[pos_x] == board[pos_x + stride] == board[pos_x + 2 * stride] and not board[pos_x] in valc:
        return True

    #check if previous move caused a win on horizontal line
    if board[pos_y * stride] == board[pos_y * stride + 1] == board [pos_y * stride + 2] and not board[pos_y * stride] in valc:
        return True

    #check if previous move was on the main diagonal and caused a win
    if pos_x == pos_y and board[0] == board[1 + stride] == board [2 + 2 * stride] and not board[0] in valc:
        return True

    #check if previous move was on the secondary diagonal and caused a win
    if pos_x + pos_y == 2 and board[2 * stride] == board[1 + stride] == board[2] and not board[2] in valc:
        return True

    return False

#Makes and returns a copy
def modifyboard(board, index, val):
    newboard = list(board)
    newboard[index] = val
    return newboard

def minimax(board, flip,depth, coeff = 1, decay = 0.66):
    pos = 0
    sumv = 0
    if depth != 0:
        for index in board:
            #Spot is available
            if index == 0:
                #Check victory if we were to take one of the available spots
                victory = CheckVictory(modifyboard(board,pos,flip), pos % 3, (pos - pos%3)/3,3,True, [0,-flip])
                if victory:
                    sumv += coeff * flip
                else:
                    sumv += coeff * minimax(modifyboard(board, pos, flip), -flip, depth - 1, coeff * decay, decay)
            pos+=1
    return sumv
#First set gets returned as an array
def minimax_initial(board, flip, depth, coeff = 1, decay = 1):
    pos = 0
    sumv = [0]*9
    for index in board:
        #Spot is available
        #print index
        if index == 0:
            #Check victory if we were to take one of the available spots
            victory = CheckVictory(modifyboard(board, pos, flip), pos % 3, (pos - pos%3)/3, 3,True, [0, -flip])
            if victory:
                sumv[pos] = flip
            else:
                sumv[pos] = minimax(modifyboard(board, pos, flip), -flip, depth - 1, coeff, decay)
        pos+=1
    return sumv

def checkallboard(board, pcheck=False, ptype=[0]):
    for i in range(0, len(board)):
        if board[i] != 0:
            if CheckVictory(board,i%3, (i- i%3)/3,3,pcheck,ptype):
                return True
    return False

def generateboard():
    board =  np.random.randint(low=-1, high=2, size=9)
    for i in range(0, len(board)):
        if CheckVictory(board,i%3, (i- i%3)/3,3):
            return generateboard()
    return board


def printboard(board):
    print board[0], "|", board[1], "|", board[2]
    print "-------------"
    print board[3], "|", board[4], "|", board[5]
    print "-------------"
    print board[6], "|", board[7], "|", board[8]


def cycleinput(x, period, dt=0.01):
    step = int(round(period/dt))
    def stimulus(t):
        i = int(round((t-dt)/dt))
        return x[(i/step)%len(x)]
    return stimulus


class GridDisplay_Low(GridLayout):
    def btn_to_board(self):
        board  = [0] * in_dim
        for btn in range(0,in_dim):
            if self.squares[btn].text == "X":
                board[btn] = 1
            elif self.squares[btn].text == "O":
                board[btn] = -1
        return board
    def setcolor(self, color):
        for btn in self.squares:
            btn.background_color = color
    def _update(self, i):
        def _handle(value):
            if value.text != player and value.text != ai and self.winner == "--":
                value.text = player
                board = self.btn_to_board()
                if(checkallboard(board)):
                    self.winner = player
                    self.setcolor(playerc)
                self.movecount+=1
                self.superfunc(board,i, self.ind)
        return _handle
    def __init__(self,f,index):
        super(GridDisplay_Low, self).__init__()
        self.winner = "--"
        self.superfunc = f
        self.rows = int(np.sqrt(in_dim))
        self.cols = int(np.sqrt(in_dim))
        self.squares = [None] * in_dim
        self.movecount = 0
        self.ind = index
        for i in range(in_dim):
            self.squares[i] = Button(text='--', font_size=30)
            func = self._update(i)
            self.squares[i].bind(on_press=func)
            self.add_widget(self.squares[i])

class GridDisplay_High(GridLayout):
    def btn_to_board(self):
        board = [0] * in_dim
        for i in range(in_dim):
            if self.high_squares[i].winner == "X":
                board[i] = 1
            elif self.high_squares[i].winner == "O":
                board[i] = -1
        return board
    def put_ai(self, index, pos):
        if self.high_squares[pos].squares[index].text== "--":
            self.high_squares[pos].squares[index].text= ai
            return True
        return False
    def win_next_turn(self,ptype):
        ret = [[0] * 9] * 9

        for i in range(len(self.lowboards)):
            ret[i] = minimax_initial(self.lowboards[i], ptype,1)
        return ret
    #index is the index of the square, pos is the index inside the square
    def update(self, board,pos,index):
        highboard = self.btn_to_board()
        self.lowboards[index] = board
        made_move = False

        selected_board = 0


        h1_lvl_decision = minimax_initial(highboard, -1, 3)
        h2_lvl_decision = minimax_initial(highboard, 1, 3)
        #Look at where they played last
        print "--------------"
        print "h1", h1_lvl_decision
        print "h2", h2_lvl_decision
        w1 = self.win_next_turn(-1)
        w2 = self.win_next_turn(1)
        printboard(board)
        print w1[index]
        print w2[index]

        if not made_move and self.high_squares[index].movecount == 1:
           made_move = self.put_ai(optimal[pos],index)

        winning_index = np.argmax(w1[index])
        print winning_index
        if not made_move and w1[index][winning_index] != 0:
            made_move = self.put_ai(winning_index, index)

        winning_index = np.argmax(w2[index])
        if not made_move and w2[index][winning_index] != 0:
            made_move = self.put_ai(winning_index, index)

        if self.high_squares[index].winner == "--":
            l1_lvl_decision = minimax_initial(board, -1, 5)
            l2_lvl_decision = minimax_initial(board, 1, 5)
            print "l1", l1_lvl_decision, np.sum(l1_lvl_decision)
            print "l2", l2_lvl_decision, np.sum(l2_lvl_decision)


            max_l1 = np.argmax(np.abs(l1_lvl_decision))
            max_l2 = np.argmax(np.abs(l2_lvl_decision))
            max_list = np.abs([l1_lvl_decision[max_l1], l2_lvl_decision[max_l2]])

            selected_board = index
            if not made_move and np.argmax(max_list) == 0:
                made_move = self.put_ai(max_l1,index)
            if not made_move and np.argmax(max_list) != 0:
                made_move = self.put_ai(max_l2,index)

        #Update the board that the AI has chosen
        self.lowboards[selected_board] = self.high_squares[selected_board].btn_to_board()
        if checkallboard(self.lowboards[selected_board], True, [1,0]):
            self.high_squares[selected_board].winner = ai
            self.high_squares[selected_board].setcolor(aic)


    def __init__(self):
        super(GridDisplay_High,self).__init__()
        self.winner = "--"
        self.rows = int(np.sqrt(in_dim))
        self.cols = int(np.sqrt(in_dim))
        self.high_squares = [None] * in_dim

        self.lowboards = [[0] * in_dim] * in_dim

        for i in range(in_dim):
            self.high_squares[i] = GridDisplay_Low(self.update,i)
            self.add_widget(self.high_squares[i])


class TicTacToe(App):
    def build(self):
        return GridDisplay_High()

TicTacToe().run()
