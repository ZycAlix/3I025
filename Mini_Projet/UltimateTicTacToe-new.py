# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys
import heapq
import time


#-------------------------------------------   
#  Functions Find the shortest path with A*
#-------------------------------------------
class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

direction = [(0,1),(0,-1),(1,0),(-1,0)]
    
def dist_Manhatan(point1, point2):
    x1, y1 = point1;
    x2, y2 = point2;
    return abs(x1-x2)+abs(y1-y2);
    
def neighbors(point1,unreachable):
    list_neigh = []
    for dirt in direction:
        if (point1[0]+dirt[0],point1[1]+dirt[1]) not in unreachable:
            list_neigh.append((point1[0]+dirt[0],point1[1]+dirt[1]))
    return list_neigh
    
def cost(current, next):
    return 1


def astar(start, end, unreachable):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    
    came_from = {}
    came_from[start] = None

    cost_so_far = {}
    cost_so_far[start] = 0
    path = []    
    while not frontier.empty():
        current = frontier.get()
            
        if(current == end):
            while current != start:
                path.append(current)
                current = came_from[current]
                path.reverse()
            return path
            
        for next in neighbors(current,unreachable):
                new_cost = cost(current, next) + cost_so_far[current]
                if next not in cost_so_far.keys() or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + dist_Manhatan(end,next)
                    frontier.put(next, priority)
                    came_from[next] = current   
    return path


#-------------------------------------------   
#  Functions TicTacToe
#-------------------------------------------
def bigTicTacToeBoard(wallStates):
    bigBoard = []
    for x in range(4,15):
        row = []
        for y in range(4,15):
            if(x,y) not in wallStates:
                if not ((x in [5,9,13] and y in [7,11]) or (x in [7,11] and y in [5,9,13])):
                    row.append((x,y))
        if row !=[]:
            bigBoard.append(row)
    return bigBoard

#Return N the smalle TicTacToeBoard nb_Board~(0,8)
def smalleTicTacToeBoard(bigBoard, nb_Board):
    smalleBoard = []
    x = (nb_Board // 3)*3
    y = (nb_Board % 3)*3
    for i in [0,1,2]:
        line = []
        for j in [0,1,2]:
            line.append(bigBoard[x+i][y+j])
        smalleBoard.append(line)
    return smalleBoard

def initialisationStates(bigBoard):
    states = {}
    for i in range(len(bigBoard)):
        for j in range(len(bigBoard[0])):
            (x,y) = bigBoard[i][j]
            states[str((x,y))] = -1
    return states;

def getStates(states,x,y):
    return states[str((x,y))];

def isSmalleBoardFull(bigBoard,nb_Board,states):
    smalleBoard = smalleTicTacToeBoard(bigBoard,nb_Board)
    full = True
    for i in range(len(smalleBoard)):
        for j in range(len(smalleBoard[0])):
            (x,y) = smalleBoard[i][j]
            if getStates(states,x,y) == -1:
                full = False
    return full

def isSmalleBoardWin(bigBoard,nb_Board,states):
    smalleBoard = smalleTicTacToeBoard(bigBoard,nb_Board)
    win = False
    numPlayer = -1
    #Check up row 
    for i in range(len(smalleBoard)):
        (x,y) = smalleBoard[i][0]
        (a,b) = smalleBoard[i][1]
        (g,h) = smalleBoard[i][2]
        if getStates(states,x,y) != -1 and getStates(states,x,y) == getStates(states,a,b) and getStates(states,a,b) == getStates(states,g,h):
            win = True
            numPlayer = getStates(states,x,y)
            return win,numPlayer
    
    #check up col 
    for i in range(len(smalleBoard)):
        (x,y) = smalleBoard[0][i]
        (a,b) = smalleBoard[1][i]
        (g,h) = smalleBoard[2][i]
        if getStates(states,x,y) != -1 and getStates(states,x,y) == getStates(states,a,b) and getStates(states,a,b) == getStates(states,g,h):
            win = True
            numPlayer = getStates(states,x,y)
            return win,numPlayer

    #check up diagonal 
    if(getStates(states,smalleBoard[0][0][0],smalleBoard[0][0][1]) !=-1 and getStates(states,smalleBoard[1][1][0],smalleBoard[1][1][1]) == getStates(states,smalleBoard[0][0][0],smalleBoard[0][0][1])):
        if(getStates(states,smalleBoard[1][1][0],smalleBoard[1][1][1]) == getStates(states,smalleBoard[2][2][0],smalleBoard[2][2][1])):
            numPlayer = getStates(states,smalleBoard[1][1][0],smalleBoard[1][1][1])
            win = True
            return win,numPlayer

    if(getStates(states,smalleBoard[0][2][0],smalleBoard[0][2][1]) !=-1 and getStates(states,smalleBoard[1][1][0],smalleBoard[1][1][1]) == getStates(states,smalleBoard[0][2][0],smalleBoard[0][2][1])):
        if(getStates(states,smalleBoard[1][1][0],smalleBoard[1][1][1]) == getStates(states,smalleBoard[2][0][0],smalleBoard[2][0][1])):
            win = True
            return win,numPlayer

    return win,numPlayer


def strategyRandom(bigBoard,states):
    nb_Board = -1
    (x,y) = (-1,-1)
    while True:
        nb_Board = random.randint(0,8)

        if not isSmalleBoardFull(bigBoard,nb_Board,states) and not isSmalleBoardWin(bigBoard,nb_Board,states)[0]:
            break
    smalleBoard = smalleTicTacToeBoard(bigBoard,nb_Board)

    while True:
        (x,y) = smalleBoard[random.randint(0,2)][random.randint(0,2)]

        if (getStates(states,x,y) == -1):
            break
    return (x,y)

def strategyGreedy(bigBoard, states):
    ordre = [8,4,0,6,2,7,5,1]
    nb_Board = -1
    for n in ordre:
        if not isSmalleBoardFull(bigBoard,n,states) and not isSmalleBoardWin(bigBoard,n,states)[0]:
            nb_Board = n
            break
    smalleBoard = smalleTicTacToeBoard(bigBoard,n)
    (x,y) = (-1,-1)
    for n in ordre:
        (x,y) = smalleBoard[(n//3)][n%3]
        if(getStates(states,x,y) == -1):
            break
    return (x,y)

def gameFinished(bigBoard,states):
    #check up all of smalleBoard
    gameOver = False
    tmp = []
    for n in [0,1,2]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 0,1,2, winner : %f ", tmp[0][1])
        return gameOver
    else: 
        tmp = []

    for n in [3,4,5]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 3,4,5, winner : %f ", tmp[0][1])
        return gameOver
    else:
        tmp = []

    for n in [6,7,8]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 6,7,8, winner : %f ", tmp[0][1])
        return gameOver
    else:
        tmp = []

    for n in [0,3,6]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 0,3,6, winner : %f ", tmp[0][1])
        return gameOver
    else:
        tmp = []

    for n in [1,4,7]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 1,4,7, winner : %f ", tmp[0][1])
        return gameOver
    else:
        tmp = []

    for n in [2,5,8]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 2,5,8, winner : %f ", tmp[0][1])
        return gameOver
    else:
        tmp = []

    for n in [0,4,8]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 0,4,8, winner : %f ", tmp[0][1])
        return gameOver
    else:
        tmp = []

    for n in [2,4,6]:
        tmp.append(isSmalleBoardWin(bigBoard,n,states))
    if (tmp[0]==tmp[1] and tmp[0][0]== True and tmp[0] == tmp[2]):
        gameOver = True
        print("Game Over with thses smalle borad 2,4,6, winner : %f ", tmp[0][1])
        return gameOver
    else:
        tmp = []

    for n in range(len(bigBoard)):
        if isSmalleBoardWin(bigBoard,n,states)[0] or isSmalleBoardFull(bigBoard,n,states):
            tmp.append(True)
        if len(tmp) == 9:
            gameOver = True
            print("Game Over with a draw")
    return gameOver
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'tictactoeBis'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 60  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 500 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    #score = [0]*nbPlayers
    #fioles = {} # dictionnaire (x,y)->couleur pour les fioles
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    #goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    # et la zone de jeu pour le tic-tac-toe
    tictactoeStates = [(x,y) for x in range(3,16) for y in range(3,16)]
    #print ("Wall states:", wallStates)
    
    bigBoard=bigTicTacToeBoard(wallStates)
    states = initialisationStates(bigBoard)


    # les coordonnees des tiles dans la fiche
    tile_fiole_jaune = (19,1)
    tile_fiole_bleue = (20,1)
    
    # listes des objets fioles jaunes et bleues
    
    fiolesJaunes = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_jaune]
    fiolesBleues = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_bleue]   
    all_fioles = (fiolesJaunes,fiolesBleues) 
    fiole_a_ramasser = (0,0) # servira à repérer la prochaine fiole à prendre
    
    # renvoie la couleur d'une fiole
    # potentiellement utile
    
    def couleur(o):
        if o.tileid==tile_fiole_jaune:
            return 'j'
        elif o.tileid==tile_fiole_bleue:
            return 'b'
    
    
    #-------------------------------
    # Placement aleatoire d'une fioles de couleur 
    #-------------------------------
    
    def put_next_fiole(j,t):
        o = all_fioles[j][t]
    
        # et on met cette fiole qqpart au hasard
    
        x = random.randint(1,19)
        y = random.randint(1,19)
    
        while (x,y) in tictactoeStates or (x,y) in wallStates: # ... mais pas sur un mur
            x = random.randint(1,19)
            y = random.randint(1,19)
        o.set_rowcol(x,y)
        # on ajoute cette fiole dans le dictionnaire
        #fioles[(x,y)]=couleur(o)
    
        game.layers['ramassable'].add(o)
        game.mainiteration()
        return (x,y)
        
        
    
    
    
    #-------------------------------
    # Boucle principale de déplacements, un joueur apres l'autre
    #-------------------------------
    
    posPlayers = initStates

    tour = 0    
    j = 0 # le joueur 0 commence
    # on place la premiere fiole jaune      

    (x,y) = (0,0) 
    fiole_a_ramasser = put_next_fiole(0,tour)    
    gameOver = False

    for i in range(iterations):
        # bon ici on fait juste plusieurs random walker pour exemple...
     

        row,col = posPlayers[j]
        
        # bouger vers la fiole
        chemin = astar((row,col),fiole_a_ramasser,wallStates)
        
        k = 0
        while (k < len(chemin)):
            next_row,next_col = chemin[k]
        
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)
                game.mainiteration()
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)


            # si on trouve la fiole par un grand hasard...
            if (row,col)==fiole_a_ramasser:
                o = players[j].ramasse(game.layers) # on la ramasse
                game.mainiteration()
                print ("Objet de couleur ", couleur(o), " trouvé par le joueur ", j)
                break
            # ici il faudrait aller la mettre a la position choisie
            # pour jouer a ultimate tic-tac-toe
            # et verifier que la position est legale etc.

            k = k + 1
            # on active le joueur suivant
            # et on place la fiole suivante
        if j%2 == 0: 
            foile_a_deposer = strategyRandom(bigBoard,states)
        else:
            foile_a_deposer = strategyGreedy(bigBoard,states)
            
        chemin = astar((row,col),foile_a_deposer,wallStates)
        l = 0

        while (l < len(chemin)):
            next_row,next_col = chemin[l]
        
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)
                game.mainiteration()
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)

            if (row,col) == foile_a_deposer:
                players[j].depose(game.layers)
                states[str((foile_a_deposer[0],foile_a_deposer[1]))] = j
                game.mainiteration()
                break
            l = l + 1


        j=(j+1)%2
        if j == 0:
            tour+=1
                 
        fiole_a_ramasser=put_next_fiole(j,tour)    

        #We check up if the game is over 
        
        gameOver = gameFinished(bigBoard,states)
        if(gameOver):
            break        
    
    print("The game is over within 20 seconds")        
    time.sleep(20)
    pygame.quit()
    
   
    
    
if __name__ == '__main__':
    main()
    


