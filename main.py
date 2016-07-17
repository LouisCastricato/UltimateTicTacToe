import numpy as np
import nengo
from nengo.networks import BasalGanglia
import nengo_ocl
import matplotlib.pyplot as plt
import kivy
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from kivy.graphics import *
from kivy.uix.widget import *
from kivy.properties import *
from kivy.uix.slider import Slider
#X is 1, O is -1, and - is 0

def CheckVictory(board, pos_y, pos_x, stride):
    #check if previous move caused a win on vertical line
    if board[pos_x] == board[pos_x + stride] == board [pos_x + 2 * stride] and not board[pos_x] == 0:
        return True

    #check if previous move caused a win on horizontal line
    if board[pos_y * stride] == board[pos_y * stride + 1] == board [pos_y * stride + 2] and not board[pos_y] == 0:
        return True

    #check if previous move was on the main diagonal and caused a win
    if pos_x == pos_y and board[0] == board[1 + stride] == board [2 + 2 * stride] and not board[0] == 0:
        return True

    #check if previous move was on the secondary diagonal and caused a win
    if pos_x + pos_y == 2 and board[2 * stride] == board[1 + stride] == board[2] and not board[2] == 0:
        return True

    return False

#Makes and returns a copy
def modifyboard(board, index, val):
    newboard = list(board)
    newboard[index] = val
    return newboard

def minimax(board, flip):
    pos = 0
    sumv = 0
    for index in board:
        #Spot is available
        if index == 0:
            #Check victory if we were to take one of the available spots
            victory = CheckVictory(board, pos % 3, (pos - pos%3)/3, 3)
            if victory:
                sumv += flip
            else:
                sumv += minimax(modifyboard(board, pos, flip), -flip)
        pos+=1
    return sumv
#First set gets returned as an array
def minimax_initial(board, flip):
    pos = 0
    sumv = [0]*9
    for index in board:
        #Spot is available
        #print index
        if index == 0:
            #Check victory if we were to take one of the available spots
            victory = CheckVictory(board, pos % 3, (pos - pos%3)/3, 3)
            if victory:
                sumv[pos] = flip
            else:
                sumv[pos]= minimax(modifyboard(board, pos, flip), -flip)
        pos+=1
    return sumv

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


x = np.arange(np.pi/16, np.pi, np.pi/16)
time = (np.pi) * 2
timedelta = 1 #time/(float(len(x)) * 2)
n_neurons = 3000
in_dim = 9


model= nengo.Network()
inputvector = [None]*len(x)
outputvector = [None]*len(x)
for i in range(0, len(x)):
    inputvector[i] = generateboard()
    printboard(inputvector[i])
    print ""
    outputvector[i] = minimax_initial(inputvector[i], -1)

inputvector=np.array(inputvector)
with model:
    inputstim = nengo.Node(output=cycleinput(inputvector, timedelta), size_out=in_dim)
    selectionstim = nengo.Node(output=cycleinput(outputvector, timedelta), size_out=in_dim)

    in_x = nengo.Ensemble(n_neurons,in_dim)
    out_y = nengo.Ensemble(n_neurons, in_dim)
    error=nengo.Ensemble(n_neurons, in_dim)

    nengo.Connection(inputstim, in_x)

    nengo.Connection(selectionstim, error,transform=-1)
    nengo.Connection(out_y, error)

    con = nengo.Connection(in_x, out_y, learning_rule_type=nengo.PES(1e-3))
    nengo.Connection(error, con.learning_rule)

    basalx = BasalGanglia(dimensions=9)
    nengo.Connection(out_y, basalx.input)

    basalo = BasalGanglia(dimensions=9)
    nengo.Connection(out_y, basalo.input,transform=-1)


    gameState = nengo.Probe(out_y, synapse=0.1)
    basalxProbe = nengo.Probe(basalx.output, synapse=0.2)
    basaloProbe = nengo.Probe(basalo.output, synapse=0.2)
with nengo_ocl.Simulator(model) as sim:
    sim.run(time)


class BoxWidget(Widget):
    r= NumericProperty(1)
    g=NumericProperty(1)
    def __init__(self,position, **kwargs):
        super(BoxWidget,self).__init__(**kwargs)
        self.bind(r = self.redraw)
        self.bind(g = self.redraw)
        self.Pos = position
        with self.canvas:
            Color(self.r,self.g,0,1)
            Rectangle(pos=position, size=(200,200))

    def redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(self.r, self.g, 0,1)
            Rectangle(pos=self.Pos, size=(200,200))
class GridDisplay(GridLayout):
    def showtime(self,instance, value):
        for i in range(0,len(self.squares)):
            val = sim.data[gameState][value][i]

            val = (val + 1)/2
            self.squares[i].r = float(val)
            self.squares[i].g = float(1 - val)

    def __init__(self):
        super(GridDisplay, self).__init__()
        self.rows = 4
        self.cols = 3
        self.squares = [None] * in_dim
        for i in range(0, in_dim):
            self.squares[i] = BoxWidget(((i%3) * 200, ((i - i%3) / 3) * 200))
            self.add_widget(self.squares[i])

        self.s = Slider(min =0,max=len(sim.trange()) -1, value=0)
        self.s.bind(value = self.showtime)
        self.add_widget(self.s)
class MyApp(App):
    def build(self):
        sc = GridDisplay()
        return sc


plt.plot(sim.trange(), sim.data[basalxProbe].argmax(axis=1))
plt.plot(sim.trange(), sim.data[basaloProbe].argmax(axis=1))

plt.show()

#MyApp().run()
