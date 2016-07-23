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
optimal = [1,7,1,5,1,3,3,1,5]
def CheckVictory(mboard, y, x, stride,pcheck = False, ptype = [0]):
    #check if previous move caused a win on vertical line
    board = np.array(mboard).reshape(3,3)
    valc= [0]
    if pcheck:
        valc = ptype
    #check if previous move caused a win on vertical line
    if board[0][y] == board[1][y] == board [2][y] and not board[0][y] in valc:
        return True

    #check if previous move caused a win on horizontal line
    if board[x][0] == board[x][1] == board [x][2] and not board[x][0] in valc:
        return True

    #check if previous move was on the main diagonal and caused a win
    if x == y and board[0][0] == board[1][1] == board [2][2] and not board[0][0] in valc:
        return True

    #check if previous move was on the secondary diagonal and caused a win
    if x + y == 2 and board[0][2] == board[1][1] == board [2][0] and not board[2][0] in valc:
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
    if depth > 0:
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
def minimax_initial(board, flip, depth, coeff = 1, decay = 0.9):
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
        if self.high_squares[pos].squares[index].text== "--" and self.high_squares[pos].winner == "--":
            self.high_squares[pos].squares[index].text= ai
            return True
        return False
    def win_next_turn(self,ptype):
        ret = [[0] * 9] * 9

        for i in range(len(self.lowboards)):
            ret[i] = minimax_initial(self.lowboards[i], ptype,1)
        return ret
    def considerIndex(self, index,w1,w2, pos,board):
        made_move = False
        defensive = True

        winning_index = np.argmin(w1[index])
        if not made_move and w1[index][winning_index] < 0:
            made_move = self.put_ai(winning_index, index)
        winning_index = np.argmax(w2[index])
        if not made_move and w2[index][winning_index] > 0:
            made_move = self.put_ai(winning_index, index)

        if defensive and not made_move:
            l1_lvl_decision = minimax_initial(board, -1, 4)
            l2_lvl_decision = minimax_initial(board, 1, 4)


            max_l1 = np.argmax(np.abs(l1_lvl_decision))
            max_l2 = np.argmax(np.abs(l2_lvl_decision))
            max_list = np.abs([l1_lvl_decision[max_l1], l2_lvl_decision[max_l2]])
            if not made_move and np.argmax(max_list) == 0:
                made_move = self.put_ai(max_l1,index)
            if not made_move and np.argmax(max_list) != 0:
                made_move = self.put_ai(max_l2,index)
        return made_move
    def considernboards(self, lst):
        max_index = 0
        max_value = 0
        max_board = 0

        min_value = 0
        min_index = 0
        min_board = 0
        for i in lst:
            arr = minimax_initial(self.lowboards[i],-1,3)

            tmin = np.argmin(arr)
            imin = arr[tmin]

            if imin <= min_value:
                min_value = imin
                min_index = tmin
                min_board = i
            tmax= np.argmax(arr)
            imax = arr[tmax]

            if imax >= max_value:
                max_value = imax
                max_index = tmax
                max_board = i
        return [[max_value, max_index, max_board], [min_value,min_index, min_board]]
    #index is the index of the square, pos is the index inside the square
    def update(self, board,pos,index):
        highboard = self.btn_to_board()
        self.lowboards[index] = board
        made_move = False
        selected_board = 0

        self.enemyrecent.append(index)
        h1_lvl_decision = minimax_initial(highboard, -1, 3)
        h2_lvl_decision = minimax_initial(highboard, 1, 3)
        #Look at where they played last
        print "--------------"
        print "h1", h1_lvl_decision
        print "h2", h2_lvl_decision
        w1 = np.array(np.negative(self.win_next_turn(-1))).clip(0)
        w2 = np.array(self.win_next_turn(1)).clip(0)

        r1 = []
        r2 = []

        for arr in w1:
            r1.append(np.sum(arr))
        for arr in w2:
            r2.append(np.sum(arr))

        max1 = np.argmax(r1)
        max2 = np.argmax(r2)
        print r1
        print r2
        print max1
        #made_move = self.considerIndex(max1,w1,w2,pos,self.lowboards[max1])
        if np.sum(w1[max1]) != 0:
            made_move = self.put_ai(np.argmax(w1[max1]), max1)
        w1 = np.negative(w1)
        if len(self.myrecent) > 0:
            mine = self.considernboards(self.myrecent)
        theirs = self.considernboards(self.enemyrecent)

        if len(self.myrecent) > 0 and np.abs(mine[1][0]) > np.abs(theirs[0][0]) and not made_move:
            made_move = self.considerIndex(mine[1][1],w1,w2,pos,self.lowboards[mine[1][1]])
            if made_move:
                selected_board = mine[1][1]

        if len(self.myrecent) > 0 and np.abs(mine[0][0]) > np.abs(theirs[1][0]):
            made_move = self.considerIndex(mine[0][1],w1,w2,pos,self.lowboards[mine[0][1]])
            if made_move:
                selected_board = mine[0][1]
        if not made_move:
            made_move = self.considerIndex(index, w1,w2,pos,board)
        if made_move:
            selected_board = index



        if not made_move:
            newIndex = np.argmin(h1_lvl_decision)
            oppIndex = np.argmax(h2_lvl_decision)

            max_list = np.abs([h1_lvl_decision[newIndex], h2_lvl_decision[oppIndex]])

            if np.argmax(max_list) == 0:
                selected_board = newIndex
            if np.argmax(max_list) != 0:
                selected_board = oppIndex
            self.considerIndex(selected_board,w1,w2,pos,self.lowboards[selected_board])

        #Update the board that the AI has chosen
        self.lowboards[selected_board] = self.high_squares[selected_board].btn_to_board()

        self.myrecent.append(selected_board)
        self.myrecent = list(set(self.myrecent))
        self.enemyrecent = list(set(self.enemyrecent))
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

        self.enemyrecent = [0,1,2,3,4,5,6,7,8]
        self.myrecent  = [0,1,2,3,4,5,6,7,8]



        for i in range(in_dim):
            self.high_squares[i] = GridDisplay_Low(self.update,i)
            self.add_widget(self.high_squares[i])


class TicTacToe(App):
    def build(self):
        return GridDisplay_High()
'''
board = [0] * 9
r = [None] * 9
for i in range(9):
    board[i] = 1
    r[i] = np.argmax(minimax_initial(board,-1,10))
    board[i] = 0
print r
'''
TicTacToe().run()
