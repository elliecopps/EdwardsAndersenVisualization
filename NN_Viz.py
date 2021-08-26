import numpy as np
import random
import tfim
import itertools as it
import networkx as nx
from line_profiler import LineProfiler

import threading
import sys, os
from itertools import combinations
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont, QColor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox



class Window(QMainWindow):
    def __init__(self, yheight, xwidth, seed):
        QMainWindow.__init__(self)
        
        #Set these to True to see periodic boundary conditions or Energy info, respectively
        ######################################################################
        self.PBC = True
        self.spins = True
        ######################################################################

        #Window size and label
        self.title = "Edwards Andersen Spin Configuration"
        self.top= 50
        self.left= 100
        self.width = 1000
        self.height = 750
        self.center = (500,375)
        self.spacing = 35

        self.yheight = yheight
        self.xwidth = xwidth
        self.seed = seed
        
        self.lasty = yheight
        self.lastx = xwidth
        self.lastseed = seed
        
        self.xchange = False
        self.ychange = False
        self.seedchange = False
        
        self.setStyleSheet("background-color: white;")
        
        self.Clabel = QLabel(self)
        self.Clabel.setFont(QFont('Decorative', 13))
        self.Clabel.setStyleSheet("color: black")
        self.Clabel.resize(400,30)
        self.Clabel.move(500,20)
        
        self.countLabel = QLabel(self)
        self.countLabel.setStyleSheet("color: black")
        self.countLabel.move(20,20)
        self.countLabel.resize(400,30)
        
        self.cEdit = QLineEdit(self)
        self.cEdit.setStyleSheet("color: black")
        self.cEdit.move(80, 650)
        self.cEdit.resize(100,32)
        self.cLabel = QLabel(self)
        self.cLabel.setStyleSheet("color: black")
        self.cLabel.setText("Config")
        self.cLabel.move(20,650)
        self.cLabel.resize(50,32)

        self.sEdit = QLineEdit(self)
        self.sEdit.setStyleSheet("color: black")
        self.sEdit.setText(str(self.seed))
        self.sEdit.move(80, 600)
        self.sEdit.resize(100,32)
        self.sLabel = QLabel(self)
        self.sLabel.setStyleSheet("color: black")
        self.sLabel.setText("Seed")
        self.sLabel.move(20,600)
        self.sLabel.resize(50,32)

        self.xwidthEdit = QLineEdit(self)
        self.xwidthEdit.setStyleSheet("color: black")
        self.xwidthEdit.setText(str(self.xwidth))
        self.xwidthEdit.move(80, 550)
        self.xwidthEdit.resize(100,32)
        self.xwidthLabel = QLabel(self)
        self.xwidthLabel.setStyleSheet("color: black")
        self.xwidthLabel.setText("Width")
        self.xwidthLabel.move(20,550)
        self.xwidthLabel.resize(50,32)
        
        self.yheightEdit = QLineEdit(self)
        self.yheightEdit.setStyleSheet("color: black")
        self.yheightEdit.setText(str(self.yheight))
        self.yheightEdit.move(80, 500)
        self.yheightEdit.resize(100,32)
        self.yheightLabel = QLabel(self)
        self.yheightLabel.setStyleSheet("color: black")
        self.yheightLabel.setText("Height")
        self.yheightLabel.move(20,500)
        self.yheightLabel.resize(50,32)
        

        self.ucountLabel = QLabel(self)
        self.ucountLabel.setStyleSheet("color: black")
        self.ucountLabel.setText("Unsatisfied: ")
        self.ucountLabel.move(20,50)
        self.ucountLabel.resize(400,32)
        
        self.configlstLabel = QLabel(self)
        self.configlstLabel.setStyleSheet("color: black")
        self.configlstLabel.setText("Configurations: ")
        self.configlstLabel.move(20, 80)
        self.configlstLabel.resize(1000, 32)
        
        self.pybutton = QPushButton('Enter', self)
        self.pybutton.setStyleSheet("QPushButton {color: white; background-color: black}")
        self.pybutton.clicked.connect(self.clickMethod)
        self.pybutton.resize(100,32)
        self.pybutton.move(300, 650)
        
        self.helpbutton = QPushButton('What is this?', self)
        self.helpbutton.setStyleSheet("QPushButton {color: white; background-color: red}")
        self.helpbutton.clicked.connect(self.helpWindow)
        self.helpbutton.resize(100, 32)
        self.helpbutton.move(800, 650)
        
        self.runMyCode()
        self.setLabels()
        
        self.InitWindow()

    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == QtCore.Qt.Key_Return: 
            self.clickMethod()


    def clickMethod(self):
        thread = threading.Thread(target=self.DynMethod())
        thread.start()
        
    def helpWindow(self):
        msg = QMessageBox()
        msg.setText("Changing the seed will change the bonds to a different random system. You can type the configurations listed above into the 'config' box to see one of the lowest-energy state solutions for this particular system. Click below for a more detailed explanation.")
        msg.setDetailedText("This is a visual representation of an algorithm that tries to find the lowest-energy configuration of a group of particle spins. 'Seed' represents the seed used to randomly generate the bonds connnecting the spins. Red bonds are satisfied (low-energy) when the spins they connect point in the same direction. Blue bonds are satisfied when the spins the connect point in opposite directions. The algorithm identifies 'plaquettes', groups of four spins, that will have at least one unsatisfied bond. The pink lines connect the plaquettes, and represent bonds that will be broken in an ideal energy state. This is an NP-complete problem.")
        x = msg.exec()


    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top, self.width, self.height)
        self.show()

    def clickMethod(self):
        thread = threading.Thread(target=self.DynMethod())
        thread.start()


    def DynMethod(self):

        new_window = False
        ws = self.xwidthEdit.text()
        hs = self.yheightEdit.text()
        
        #Check if the height or width was changed
        if len(ws)>0:
            ws = int(ws)
            if ws != self.xwidth:
                new_window = True
                self.lastx = self.xwidth
                self.xwidth = ws
                self.xchange = True
        if len(hs) > 0:
            hs = int(hs)
            if hs != self.yheight:
                new_window = True
                self.lasty = self.yheight
                self.yheight = hs
                self.ychange = True
        
        #Check if the seed was changed
        ss = self.sEdit.text()
        if len(ss) > 0:
            s = int(ss)
            if s != self.seed:
                new_window = True
                self.lastseed = self.seed
                self.seed = s
                self.seedchange = True
                
        #See if we need to make a new window
        if new_window == True:
        
            self.runMyCode()
            self.setLabels()
            self.repaint()

        #Finally, check if the configuration has been changed
        cs = self.cEdit.text()
        if len(cs) > 0:
            c = int(cs)
            if c != self.cnfg:
                self.cnfg = c
                self.configuration = list(map(int,list(bin(self.cnfg)[2:].zfill(self.N))))
                self.Clabel.setText('Configuration: ' + str(self.configuration))
                self.repaint()


    def paintEvent(self, event):
        if self.number_ground_states > 0:
            self.setLabels
            qp = QPainter()
            qp.begin(self)
            qp.setPen(QPen(Qt.blue, 3))
            self.drawBonds(qp,self.coordList)
            self.drawSpins(qp,self.coordList)
            if self.spins == True:
                self.drawConfiguration(qp,self.configuration,self.coordList)
                self.drawBonds_spins(qp, self.coordList)
            self.draw_frustrated(qp)
            self.drawStrings(qp)
            qp.end()
        else:
            self.cantFind()


    
    def drawSpins(self, qp, coordList):
        qp.setBrush(QBrush(QColor(0,0,0), Qt.SolidPattern))
        for i in range(len(coordList)):
            qp.setPen(QPen(Qt.black, 5))
            c = coordList[i]
            qp.drawEllipse(c[0]-6,c[1]-6,12,12)
            qp.setFont(QFont('Decorative', 9.5))
            qp.drawText(c[0]+5, c[1]+15, str(i))

        
    def drawBonds(self, qp, coordList):
        for i, coord in enumerate(coordList):
            NNs = self.lattice.NN(i)
            for j in NNs:
                qp.setPen(QPen(bondColor(self.Jij,i,j), 5))
                drawn = False
                coord2 = coordList[j]
                if j == (i + (self.yheight-1)*self.xwidth) or i == (j + (self.yheight-1)*self.xwidth):
                    if (self.yheight != 2 or self.PBC == True) and i < j:
                        drawn = True
                        qp.drawLine(coord2[0], coord2[1], coord2[0], coord2[1] + (self.spacing)/2)
                        if self.yheight == 2:
                            qp.drawLine(coord[0], coord[1], coord2[0], coord2[1])
                if j == i + self.xwidth - 1 or i == j + self.xwidth - 1:
                    if (self.xwidth != 2 or self.PBC == True) and i < j:
                        drawn = True
                        qp.drawLine(coord2[0], coord2[1], coord2[0] + (self.spacing)/2, coord2[1])
                        if self.xwidth == 2:
                            qp.drawLine(coord[0], coord[1], coord2[0], coord2[1])
                if drawn == False:
                    if i<j:
                        qp.drawLine(coord[0], coord[1], coord2[0], coord2[1])
                        
    def drawBonds_spins(self, qp, coordList):
        for i in range(self.N):
            for j in range(i+1,self.N):
                if int(self.Jij[i][j]*(2*self.configuration[-i-1]-1)*(2*self.configuration[-j-1]-1)) == -1: #bond broken
                    qp.setPen(QPen(Qt.white, 2, Qt.DashLine))
                    diff = False
                    #ci = coordList[i]
                    cj = coordList[j]
                    if self.PBC:
                        if j == i+self.xwidth-1:
                            diff = True
                            ci = [cj[0]+23.5, cj[1]] #to the right
                        elif j == i + (self.yheight-1)*self.xwidth: #down from bottom
                            diff = True
                            ci = [cj[0], cj[1]+23.5]
                        else:
                            ci = coordList[i]
                    else:
                        ci = coordList[i]
                    if ci[0] == cj[0]:
                        if not diff:
                            qp.drawLine(ci[0],ci[1]+8.5,cj[0],cj[1]-8.5)
                        else:
                            qp.drawLine(ci[0],ci[1]+8.5,cj[0],cj[1]+8.5) #drawing line down
                    else:
                        if not diff:
                            qp.drawLine(ci[0]+8.5, ci[1], cj[0]-8.5, cj[1])
                        else:
                            qp.drawLine(ci[0]+8.5,ci[1],cj[0]+8.5,cj[1])
            

    def drawConfiguration(self,qp,config,coordList):
        i=0
        for c in coordList:
            if config[-i - 1] == 1:
                qp.setPen(QPen(Qt.magenta, 2))
                self.drawArrow(qp,1,c)
            else:
                qp.setPen(QPen(Qt.cyan, 2))
                self.drawArrow(qp,-1,c)
            i+=1
            
    def draw_frustrated(self,qp):
        for plaq in self.f_plaq:
            qp.setPen(QPen(Qt.magenta, 4))
            coord = self.coordList[plaq]
            qp.drawPoint(coord[0] + (self.spacing)/2, coord[1] + (self.spacing)/2)
            
        if self.PBC:
            num_of_bonds = 2*self.N
        else:
            num_of_bonds = (self.xwidth - 1)*(self.yheight) + (self.xwidth)*(self.yheight - 1)
            
            #self.scountLabel.setText("Unsatisfied: " + str(self.str_length))
        
    def drawArrow(self, qp, dir, coords):
        qp.drawLine(coords[0],coords[1]+(dir*6),coords[0],coords[1]-(dir*6))
        qp.drawLine(coords[0]-6,coords[1]-(dir*2.2),coords[0],coords[1]-(dir*6))
        qp.drawLine(coords[0]+6,coords[1]-(dir*2.2),coords[0],coords[1]-(dir*6))
        
    def drawStrings(self,qp):
        strings = []
        for i, state in enumerate(self.ground_config):
            if state[0] == self.cnfg:
                strings = self.true_ground_strings[i]#self.string_index]
                break
        qp.setPen(QPen(Qt.magenta, 4))
        for string in strings:
            for index in range(0, len(string)-1):
                switched = False
                pp1 = string[index]
                pp2 = string[index + 1]
                if pp2 < pp1:
                    p1 = pp2
                    p2 = pp1
                else:
                    p1 = pp1
                    p2 = pp2
                coord1x = self.coordList[p1][0] + (self.spacing)/2
                coord1y = self.coordList[p1][1] + (self.spacing)/2
                coord2x = self.coordList[p2][0] + (self.spacing)/2
                coord2y = self.coordList[p2][1] + (self.spacing)/2
                xweight = abs(coord2x - coord1x)/self.spacing
                yweight = abs(coord1y - coord2y)/self.spacing
                
                qp.setPen(QPen(Qt.magenta, 4))
                if xweight > 1:
                    qp.drawLine(coord1x, coord1y, coord1x - self.spacing, coord1y)
                    qp.drawPoint(coord2x, coord2y)
                elif yweight > 1:
                    qp.drawLine(coord1x, coord1y, coord1x, coord1y - self.spacing)
                    qp.drawPoint(coord2x, coord2y)
                else:
                    qp.drawLine(coord1x, coord1y, coord2x, coord2y)
                
            qp.setPen(QPen(Qt.black, 2.5))
            qp.drawPoint(self.coordList[string[0]][0] + (self.spacing)/2, self.coordList[string[0]][1] + (self.spacing)/2)
            qp.drawPoint(self.coordList[string[-1]][0] + (self.spacing)/2, self.coordList[string[-1]][1] + (self.spacing)/2)
        return
        

    def runMyCode(self):
    
        self.L = [self.yheight, self.xwidth]
        self.lattice = tfim.Lattice(self.L, self.PBC)
        self.N = self.lattice.N
        self.bonds = bond_list(self)
        self.Jij = make_Jij(self)
        self.cnfg = 0
        self.configuration = list(map(int,list(bin(self.cnfg)[2:].zfill(self.N))))
        
        self.coordList = spinCoords(self)
        self.plaq = make_plaquettes(self)
        self.f_plaq = frustrated(self)
        
        self.node_pairs = plaq_pairing(self)
        init_ground = initial_ground(self)
        self.p_pairings = init_ground[0]
        self.ground_distance = init_ground[1]
        self.str_length = self.ground_distance
        self.string_index = 0
        self.edges = viable_edges(self)
        self.matchings = plaq_groups(self)
        self.string_groups = add_all_strings(self)
        self.b_bonds = broken_bonds(self)
        true_ground = make_config(self)
        self.ground_config = true_ground[0]
        self.true_ground_strings = true_ground[1]
        self.number_ground_states = len(self.true_ground_strings)
        
        return
        
    def setLabels(self):
        self.Clabel.setText('Configuration: ' + str(self.configuration))
        self.cEdit.setText(str(self.cnfg))
        
        configs = []
        for state in self.ground_config:
            configs.append(state[0])
        self.configlstLabel.setText("Configurations: " + str(configs))
        
        self.countLabel.setText("Number of ground states: " + str(self.number_ground_states))
        self.ucountLabel.setText("Number of Unsatisfied Bonds: " + str(self.str_length))
        
        return
        
        
    def cantFind(self):
        msg = QMessageBox()
        msg.setText("Sorry! The algorithm can't find a ground state for that one yet.")
        msg.setDetailedText("The algorithm assumes that the minimum posible distance between the frustrated plaquettes will result in a ground state. With periodic boundary conditions, this is not always the case. Therefore, some configurations are not yet working with this algorithm.")
        x = msg.exec()
        if self.xchange:
            self.xwidth = self.lastx
            self.xchange = False
        if self.ychange:
            self.yheight = self.lasty
            self.ychange = False
        if self.seedchange:
            self.seed = self.lastseed
            self.seedchange = False
        self.runMyCode()
        self.setLabels()
        return



def spinCoords(self):
    coords = []
    y_init = self.center[1] - ((self.yheight*self.spacing)/2)
    for j in range(0, self.yheight):
        y = y_init + (j * self.spacing)
        x_init = self.center[0] - ((self.xwidth*self.spacing)/2)
        for i in range(0, self.xwidth):
            x = x_init + (i * self.spacing)
            c = (x,y)
            coords.append(c)
    return coords


def bond_list(self):
    np.random.seed(self.seed)
    # Generates a random list of bonds with equal numbers of ferromagnetic and antiferromagnetic bonds
    N = self.N
    if self.PBC == True:
        num_of_bonds = 2*N
    else:
        num_of_bonds = (self.xwidth - 1)*(self.yheight) + (self.xwidth)*(self.yheight - 1)
    if num_of_bonds%2 == 0:
        a1 = [-1 for i in range(num_of_bonds//2)]
    else:
        a1 = [-1 for i in range((num_of_bonds//2) + 1)]
    a2 = [1 for i in range(num_of_bonds//2)]
    a = list(np.random.permutation(a1+a2))
    return a
    


def make_Jij(self):
    bond_index = 0
    N = self.N
    b_list = self.bonds
    Jij = np.zeros((N,N))
    for i in range(0,N):
        lattice = self.lattice
        NNs = self.lattice.NN(i)
        for j in NNs:
            if Jij[i][j] == 0:
                Jij[i][j] = b_list[bond_index]
                Jij[j][i] = b_list[bond_index]
                bond_index += 1
    return Jij
    
    
def make_plaquettes(self):
    p_list = []
    if self.PBC:
        for i in range(0, self.N):
            NNs = self.lattice.NN(i)
            plaq = [i]
            plaq.append(NNs[3])
            NNs2 = self.lattice.NN(NNs[3])
            plaq.append(NNs2[1])
            plaq.append(NNs[1])
            p_list.append(plaq)
    else:
        for y in range(0,self.yheight):
            for x in range(0, self.xwidth):
                if y == self.yheight-1 or x == self.xwidth-1: #This part adds empty plaquettes so the first number is also the index of each plaquette
                    #if i want to take it out, just need to subtract 1 from x and y range
                    p_list.append([])
                else:
                    plaq = []
                    i = y*self.xwidth + x
                    plaq.append(i)
                    plaq.append(i+1)
                    plaq.append(i+self.xwidth+1)
                    plaq.append(i+self.xwidth)
                    p_list.append(plaq)
    return p_list
    
    
def frustrated(self):
    Jij = self.Jij
    f_plaq = []
    for plaq in self.plaq:
        count = 0
        if len(plaq)!=0:
            if Jij[plaq[0]][plaq[1]] == -1:
                count += 1
            if Jij[plaq[1]][plaq[2]] == -1:
                count += 1
            if Jij[plaq[2]][plaq[3]] == -1:
                count += 1
            if Jij[plaq[0]][plaq[3]] == -1:
                count += 1
            if count == 1 or count == 3:
                f_plaq.append(plaq[0])
    return f_plaq
        
        
def plaq_pairing(self):

    pair_list = []
    for index, p1 in enumerate(self.f_plaq):
        coord1 = self.coordList[p1]
        for p2 in self.f_plaq[index+1:]:
            coord2 = self.coordList[p2]
            x1 = coord1[0] + (self.spacing)/2
            x2 = coord2[0] + (self.spacing)/2
            
            y1 = coord1[1] + (self.spacing)/2
            y2 = coord2[1] + (self.spacing)/2
            
            xdiff = abs((x1 - x2)/self.spacing)
            ydiff = abs((y2-y1) / self.spacing)
            if xdiff > (self.xwidth)//2:
                xdiff = (self.xwidth) - xdiff
            if ydiff > (self.yheight)//2:
                ydiff = (self.yheight) - ydiff
            tot_dist = int(xdiff + ydiff)
            #Here we build a list of pairs with the distance between them
            max = self.xwidth//2 + self.yheight//2
            op_dist = (max - tot_dist)
            if p1 > p2:
                pair_list.append((p2, p1, op_dist))
            else:
                pair_list.append((p1, p2, op_dist)) #Pair_list does not have true distance between pairs, the true distance is subtracted from the max possible distance to help with node matching later
    return pair_list
    

def initial_ground(self):

    pair_list = self.node_pairs
    G = nx.Graph()
    G.add_weighted_edges_from(pair_list) #makes graph of all node pairs
    matching = nx.max_weight_matching(G) #gives one solution
    ground_dist = 0
    p_pairs = []
    for pair in matching:
        edge = G.get_edge_data(pair[0], pair[1])
        pair_dist = (self.xwidth//2 + self.yheight//2)-edge['weight']
        ground_dist += pair_dist #total string length for a ground state soln
        if pair[0] > pair[1]:
            p0 = pair[1]
            p1 = pair[0]
            pair = (p0, p1)
        p_pairs.append([pair, pair_dist]) #adds solution from above to list with pairs and pair distance
    return p_pairs, ground_dist


  
def viable_edges(self):
    '''Function takes the list of all possible pairings of nodes and returns a list of all combinations of those nodes that would result in a ground state energy'''
    pair_list = self.node_pairs # The list of all pairs of nodes
    p_pairs = self.p_pairings
    ground_dist = self.ground_distance
    f_plaq = self.f_plaq
    xwidth = self.xwidth
    yheight = self.yheight
    edge_lst = []
    plaq_dict = {}
    
    #Make the list for the edges grouped by plaquette
    for index, plaq in enumerate(f_plaq):
      edge_lst.append([])
      plaq_dict[plaq] = index

    G = nx.Graph()
    G.add_weighted_edges_from(pair_list)  #creates a graph with edges between each pair in pair_list

    #This bit just checks if p_pairs, the ground state that we found in the last function, has the ground_dist that we are looking for
    #It will if we haven't incremented anything yet
    first = False
    p_dist = 0
    for pair in p_pairs:
      dist = pair[1]
      p_dist += dist
    if p_dist == ground_dist:
      first = True #So we only remove certain edges if p_pairs is relevant
      


    if first:   #if the initial ground distance for p_pairs is good, we add the edges from p_pairs to the list of viable edges
      for pair in p_pairs:
          plaq = pair[0][0]
          ind = plaq_dict.get(plaq)
          edge_lst[ind].append(pair)


    loopnum = 0
    for plaq2 in f_plaq:   #We start looping through each frustrated plaquette

      G2 = G.copy()  #returns us to a full graph of pairs each time we loop through a plaquette
      
      loopnum += 1
      
      if first:
          for pair in p_pairs:   #Remember p_pairs is the list of pairs in the ground state we found above
              if pair[0][1] == plaq2 or pair[0][0] == plaq2:
                  #print("Removing edge: ", pair)
                  G2.remove_edge(*pair[0])  #Remove the edge in our graph that has already been added to edge_lst above
                  break
              
      ground_energy = True
      while ground_energy == True:
                #This chunk builds the best ground state it can by using the edges in the graph called matching
                #Once it builds the ground state, it removes the edge that contains the plaquette we are currently on, and then it makes another matching to see if any other ground states include that edge paired with a different plaquette
      
      
          matching = nx.max_weight_matching(G2) #make the best graph for the edges that we haven't yet removed
          if len(matching) != len(f_plaq)/2: #This would happen if we have taken out all edges for a particular plaquette
              ground_energy = False
              break  #takes us back to loop through edges for a new plaquette
          new_length = 0
          new_group = []
          for pair in matching:  #takes each pair in the best matching and adds it to a group
              edge = G2.get_edge_data(pair[0], pair[1])
              if pair[0] == plaq2 or pair[1] == plaq2:
                  rem_edge = (pair[0], pair[1])  #the edge that we are going to remove
              pair_dist = (xwidth//2 + yheight//2)-edge['weight']  #the actual distance
              new_length += pair_dist
              if pair[0] > pair[1]:  #This makes it so the first listed spin is the smaller one
                  p0 = pair[1]
                  p1 = pair[0]
                  pair = (p0, p1)
              new_group.append([pair, pair_dist])
              
          if new_length == ground_dist: #if we made a possible ground state from the matching
          
              G2.remove_edge(*rem_edge)  #removes the edge with the current plaquette in it
          
              for pair in new_group:    #"new group" is a group of edges for the plaquette we are on
                  plaq3 = pair [0][0]
                  ind = plaq_dict.get(plaq3)
                  
                  if pair not in edge_lst[ind]:
                      edge_lst[ind].append(pair)
          elif new_length < ground_dist:   #This would only happen if you are incrementing the minimum ground distance, might be a spot where the code isn't doing what we want
              G2.remove_edge(*rem_edge)
          else:
              ground_energy = False   #This means that we have taken all possible ground states for that plaquette, and we need to move to the next one
              ind = plaq_dict[plaq2]
              
                
    zeroes = True
    for plaq in edge_lst:
      if len(plaq) != 0:
          zeroes = False
          break
    if zeroes:
      edge_lst = []

    return edge_lst


def plaq_groups(self):
    edges = self.edges
    f_plaq = self.f_plaq
    ground_dist = self.ground_distance
    
    group = []
    used_plaquettes = []
    all_groups = []
    current_plaq = 0
    p_ind = 0
    index = 0
    loop_count = 0
    
    new = False
    running = True
    
    plaq_dict = {}
    for index, plaq in enumerate(f_plaq): #Allows me to find the index of the frustrated plaquettes
        plaq_dict[plaq] = index
    #print(edges)
    
    '''The main piece of the function'''
    
    #This is only important if there are only two frustrated plaquettes
    if len(f_plaq) == 2:
        for i in edges[current_plaq:]:
            for pair in i:
                group.append(pair)
        all_groups.append(group)
        return all_groups
    
    
    while running:
        for group_index, p_edges in enumerate(edges[current_plaq:]):
            #here we loop through each group of plaquettes from the current_plaq to the end
            #p_edges contains each possible edge associated with the plaquette
            
            #print("p_edges: ", p_edges)
        
            if new:
                new = False #new allows me to restart the for loop when i change current_plaq
                break
                
            if group_index + current_plaq == len(edges) - 1: #if we get to the last group of edges for the last possible plaquette without having a full ground state, we need to use a different combination of edges
                try_new = False
                for_loop = False
                for e_ind, edge in enumerate(group[::-1]): #going through the ground state group backwards to see if other edge choices will work
                    loop_count +=1
                    if loop_count > 1000000:
                        running = False
                        new = True
                    for_loop = True
                    if try_new == True:
                        break
                    else:
                        plaq_ind = plaq_dict.get(edge[0][0])
                        for e_index, edge2 in enumerate(edges[plaq_ind]):
                            if edge2 == edge:
                                if e_index == len(edges[plaq_ind])-1 and plaq_ind == 0: #end of program, we've reached the last entry of the first plaquette
                                    running = False
                                    new = True
                                    try_new = True
                                    break
                                elif e_index == len(edges[plaq_ind])-1: #Move to the previous plaquette list to find a viable edge
                                    break
                                else:
                                    current_plaq = plaq_ind #move to the next edge in the list for the plaquette
                                    p_ind = e_index + 1
                                    try_new = True
                                    new = True
                                    break
                if for_loop:
                    group = group[:-e_ind]
                    #print("Line 387 Current group: ", group)
                    used_plaquettes = used_plaquettes[:-e_ind]#FACTOR OF 2 ADDED
                    if len(group) == 1 and current_plaq == 0: #and group[0][0][0] == plaq_dict.get(current_plaq):
                        #WHAT I CHANGED: current_plaq == 0 is new, i replaced that other and statement with it and it worked better? still missing one state
                        group = []
                        used_plaquettes = []
                        
            
            #The general part of the function when we are not at the end and do not yet have a full list of edges
            
            for pair in p_edges[p_ind:]: #Here we are looping through each single edge from the edges associated with the current plaquette
                #p_ind depends on which edges we get through below
            
                p_ind = 0 #Resets p_ind for the next loop through
                
                if (pair[0][0] in used_plaquettes):
                    
                    #current_plaq += 1 #new
                    #new = True #new
                    break #Can move to next plaquette because the first plaquette has already been used. This moves us back to the first for loop and a new group of edges for the next plaquette
                #elif len(group) != 0 and pair[0][0] == group[-1][0][0]:
                    #print("Line 404 yuh")
                    #break
                elif pair[0][1] in used_plaquettes:
                    continue #Need to go through to the next pair to see if we can use this plaquette still
                else:
                    group.append(pair) #neither element has been used yet
                    #print("Line 412 Current group: ", group)
                    #if current_plaq == 0: #also new
                    #used_plaquettes.append(pair[0][0]) #THIS IS NEW, Might not be a good idea
                                           
                        #need to see how I am handling used-plaquettes to see if this is good
                    
                    used_plaquettes.append(pair[0][1])#maybe add the first element of pair if this is the first plaquette we visit
                   
                    if len(group) == len(f_plaq)//2: #Group is full
                        #print('used: ', used_plaquettes)
                        length = 0
                        for pair in group:
                            #print ("Pair: ", pair)
                            length += pair[1]
                        if length == ground_dist:
                            all_groups.append(group) #once we have filled a group, we know it will be good so we can add it to all_groups
                            #print('group added: ', group)
                        
                        last_pair = group[-2] #This is the pair that we remove and replace before cycling through other options
                        #print('last pair: ', last_pair)
                        ind = plaq_dict.get(last_pair[0][0]) #The plaquette index
                        group = group[:-2]
                        #print('group 432: ', group)
                        used_plaquettes = used_plaquettes[:-2] #WAS AT -2
                        #print ('after reducing used: ', used_plaquettes)
                        found = False
                        while found == False:
                            loop_count += 1
                            if loop_count > 1000000:
                                running = False
                                new = True
                                found = True
                                break
                            for index, pairing in enumerate(edges[ind]):
                                if pairing == last_pair and index == len(edges[ind])-1: #This happens if we are at the last pair of a particular plaquette
                                    if len(group) == 0: #This happens if we have gotten through the last edge of the first plaquette, function is done
                                        running = False
                                        found = True
                                        break
                                    last_pair = group[-1] #Take off the last pair and go to that plaquette to see if there are further pairs to use
                                    ind = plaq_dict.get(last_pair[0][0])
                                    group = group[:-1]
                                    #print('group 452', group)
                                    used_plaquettes = used_plaquettes[:-1]#WAS AT -1
                                elif pairing == last_pair: #This means there are more pairs for the plaquette in question, so we adjust current_plaq and p_ind, and go through the for loops again from there
                                    current_plaq = ind
                                    p_ind = index + 1
                                    found = True
                                    new = True
                                    break
                    break
    

    return all_groups
    

def add_all_strings(self):
    edges = []
    groups = self.matchings
    coordList = self.coordList
    lattice = self.lattice

    edges = []
    for i in range(len(coordList)):
        NNs = lattice.NN(i)
        for j in NNs:
            if i < j:
                edges.append((i,j))
    G = nx.Graph()
    G.add_edges_from(edges) #G has edges connecting all points in a lattice with PBC
    
    all_groups = []
    index = 0
    for group in groups:  #loops through each group of plaquette pairs
    
        if index > 20000:
            print('Not all ground states found')  #This is a safeguard against it running for too long
            break
    
        single_pairing = []
        index += 1
        for pairing in group:  #each plaquette pair in the group
            paths = nx.all_shortest_paths(G, pairing[0][0], pairing[0][1]) #finds all possible paths between two points
            paths_list = []
            for path in paths:
                paths_list.append(path)
            single_pairing.append(paths_list)
        path_combos = it.product(*single_pairing) #
        for combo in path_combos:
            all_groups.append(combo)

    return all_groups
    

def broken_bonds(self):
    '''Returns an NxN matrix with 1's where there are broken bonds between two spins'''
    string_groups = self.string_groups
    N = self.N
    coordList = self.coordList
    xwidth=self.xwidth
    yheight=self.yheight
   
    config_Jij_list = []
    for str_index, state in enumerate(string_groups):
        config_Jij = np.zeros((N,N)) #makes a Jij matrix that will eventually give the locations of broken bonds
        #print('state: ', state)
        for string in state:       #string is a path between frustrated plaquettes
            for index in range(0, len(string)-1):  #go through the whole string
                p1 = string[index]        #p1 and p2 are the two plaquettes we are going between
                p2 = string[index + 1]
                if p1>p2:
                    hold = p1
                    p1 = p2
                    p2 = hold
                c1x = coordList[p1][0]
                c2x = coordList[p2][0]
                if c1x == c2x:     #there will be a vertical bond broken
                    
                    if p2 + xwidth > N - 1 and p1 < xwidth:
                        sp1 = p1
                        if (p1+1) % xwidth == 0:
                        
                            sp2 = p1 - xwidth + 1
                            
                        else:
                            sp2 = p1 + 1
                          
                    else:
                        
                        sp1 = p2
                        if (p1+1) % xwidth == 0: #on the far right
                            sp2 = p2 - xwidth + 1
                        else:
                            sp2 = p2 + 1
                       
                else:
                    if p2 + xwidth > N - 1: #Will be broken between a top and a bottom
                        if (p2+1) % xwidth == 0:
                            if p1 % xwidth == 0: #Then the plaquettes are on opposite sides
                                sp1 = p1
                            else:
                                sp1 = p2
                        else:
                            sp1 = p2
                        sp2 = sp1 - (xwidth * (yheight - 1))
                    elif (p2+1) % xwidth == 0:
                        
                        if p1 % xwidth == 0:
                            sp1 = p1
                        else:
                            sp1 = p2
                        sp2 = sp1 + xwidth
                    else:
                        sp1 = p2
                        sp2 = p2 + xwidth
                bond = (sp1, sp2)
                
                config_Jij[sp1][sp2] = 1
                config_Jij[sp2][sp1] = 1
        config_Jij_list.append([config_Jij, str_index])
        #print('config_Jij: ', config_Jij)
    return config_Jij_list  #a list of Jij matrices of broken bonds, the str_index says which path group it correponds to in string_groups from the function add_all_strings

    
def make_config(self):
    ground_states = []
    true_strings = []
    s_index = 0
    #print('initial number potential ground states: ', len(self.string_groups))
    for Jij in self.b_bonds:
        broken = Jij[0]
        bonds = self.Jij
        spin_list = []
        spin_list.append(0) #Set the first spin as down
        valid = True
        
        #Loop through all other spins
        for sp1 in range(1, self.N):
            if valid == False:
                #print('String group: ', self.string_groups[Jij[1]])
                break
            if sp1 % self.xwidth == 0:
                sp2 = sp1 - self.xwidth
            else:
                sp2 = sp1 - 1
            spin2 = spin_list[sp2]
            bond = bonds[sp1][sp2]
            status = broken[sp1][sp2]
            
            #Set spin
            if bond == 1:
                #Spins want to be the same
                if status == 1: #broken
                    spin1 = abs(spin2 - 1)
                else:
                    spin1 = spin2
            else:
                #Spins want to be opposite
                if status == 1: #broken
                    spin1 = spin2
                else:
                    spin1 = abs(spin2 - 1)
            spin_list.append(spin1)
            
            #Check bonds to all lower spins
            NNs = self.lattice.NN(sp1)
            for i in NNs:
                if i < sp1:
                    spini = spin_list[i]
                    bond = bonds[sp1][i]
                    status = broken[sp1][i]
                    if bond == 1: #Spins want to be same
                        if status == 1: #Spins should be opposite
                            if spin1 == spini:
                                valid = False
                                #print("1")
                                break
                        else: #Spins should be same
                            if spin1 != spini:
                                valid = False
                                #print("2")
                                break
                    else: #Spins want to be opposite
                        if status == 1: #spins should be same
                            if spini != spin1:
                                valid = False
                                #print("3")
                                break
                        else: #Spins should be opposite
                            if spini == spin1:
                                valid = False
                                #print("4")
                                break
        if valid:
            index = 0
            for i in range(0, self.N):
                if spin_list[i] == 1:
                    index += 2**i
            #spin_list.reverse()
            ground_states.append([index, s_index])
            s_index +=1
            true_strings.append(self.string_groups[Jij[1]])
            
    #print('ground states: ', ground_states)
    return ground_states, true_strings
    
def bondColor(Jij,i,j):
    if Jij[i][j] == 1:
        return Qt.red
    else:
        return Qt.blue


if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window(4, 4, 15)
    sys.exit(App.exec())
    
